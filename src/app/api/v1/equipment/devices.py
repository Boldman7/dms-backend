from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request, Query
from fastcrud import JoinConfig
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.equipment.crud_devices import crud_devices
from ....schemas.equipment.device import DeviceCreate, DeviceCreateInternal, DeviceRead, DeviceUpdate
from ....schemas.equipment.product import ProductRead
from ....schemas.base.company import CompanyRead
from ....models.equipment.product import Product
from ....models.base.company import Company
from ....models.equipment.device import Device

router = APIRouter(tags=["devices"])


@router.post("/device", status_code=201)
async def write_device(
    request: Request, device: DeviceCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> DeviceRead:
    device_internal_dict = device.model_dump()
    db_device = await crud_devices.exists(db=db, name=device_internal_dict["name"])
    if db_device:
        raise DuplicateValueException("Device Name not available")

    device_internal_dict["update_user"] = None
    device_internal = DeviceCreateInternal(**device_internal_dict)
    created_device = await crud_devices.create(db=db, object=device_internal)

    device_read = await crud_devices.get_joined(
        db=db,
        id=created_device.id,
        joins_config=[
            JoinConfig(
                model=Product,
                join_schema_to_select=ProductRead,
                join_on=Device.product_id == Product.id,
                join_prefix="product_"
            ),
            JoinConfig(
                model=Company,
                join_schema_to_select=CompanyRead,
                join_on=Device.company_id == Company.id,
                join_prefix="company_"
            ),
        ],
        nest_joins=True,
        schema_to_select=DeviceRead
    )
    if device_read is None:
        raise NotFoundException("Created device not found")

    return cast(DeviceRead, device_read)


# paginated response for devices
@router.get("/devices", response_model=PaginatedListResponse[DeviceRead])
async def read_devices(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    product_id: int | None = Query(None),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    if product_id:
        devices_data = await crud_devices.get_multi_joined(
            db=db,
            joins_config=[
                JoinConfig(
                    model=Product,
                    join_schema_to_select=ProductRead,
                    join_on=Device.product_id == Product.id,
                    join_prefix="product_"
                ),
                JoinConfig(
                    model=Company,
                    join_schema_to_select=CompanyRead,
                    join_on=Device.company_id == Company.id,
                    join_prefix="company_"
                ),
            ],
            nest_joins=True,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            name__contains=name,
            product_id=product_id,
            is_deleted=False
        )
    else:
        devices_data = await crud_devices.get_multi_joined(
            db=db,
            joins_config=[
                JoinConfig(
                    model=Product,
                    join_schema_to_select=ProductRead,
                    join_on=Device.product_id == Product.id,
                    join_prefix="product_"
                ),
                JoinConfig(
                    model=Company,
                    join_schema_to_select=CompanyRead,
                    join_on=Device.company_id == Company.id,
                    join_prefix="company_"
                ),
            ],
            nest_joins=True,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            name__contains=name,
            is_deleted=False
        )

    response: dict[str, Any] = paginated_response(crud_data=devices_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/device/{id}", response_model=DeviceRead)
async def read_device(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> DeviceRead:
    db_device = await crud_devices.get_joined(
        db=db,
        id=id,
        joins_config=[
            JoinConfig(
                model=Product,
                join_schema_to_select=ProductRead,
                join_on=Device.product_id == Product.id,
                join_prefix="product_"
            ),
            JoinConfig(
                model=Company,
                join_schema_to_select=CompanyRead,
                join_on=Device.company_id == Company.id,
                join_prefix="company_"
            ),
        ],
        nest_joins=True,
        is_deleted=False,
        schema_to_select=DeviceRead
    )
    if db_device is None:
        raise NotFoundException("Device not found")

    return cast(DeviceRead, db_device)


@router.patch("/device/{id}")
async def patch_device(
    request: Request, id: int, values: DeviceUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_device = await crud_devices.get(db=db, id=id, schema_to_select=DeviceRead)
    if db_device is None:
        raise NotFoundException("Device not found")

    existing_device = await crud_devices.exists(db=db, name=values.name)
    if existing_device:
        raise DuplicateValueException("Device Name not available")

    await crud_devices.update(db=db, object=values, id=id)
    return {"message": "Device updated"}


@router.delete("/device/{id}")
async def erase_device(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_device = await crud_devices.get(db=db, id=id, schema_to_select=DeviceRead)
    if db_device is None:
        raise NotFoundException("Device not found")

    await crud_devices.delete(db=db, id=id)
    return {"message": "Device deleted"}
