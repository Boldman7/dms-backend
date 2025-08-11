from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.equipment.crud_devices import crud_devices
from ....schemas.equipment.device import DeviceCreate, DeviceCreateInternal, DeviceRead, DeviceUpdate

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

    device_read = await crud_devices.get(db=db, id=created_device.id, schema_to_select=DeviceRead)
    if device_read is None:
        raise NotFoundException("Created device not found")

    return cast(DeviceRead, device_read)


# paginated response for devices
@router.get("/devices", response_model=PaginatedListResponse[DeviceRead])
async def read_devices(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    devices_data = await crud_devices.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, is_deleted=False,)

    response: dict[str, Any] = paginated_response(crud_data=devices_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/device/{id}", response_model=DeviceRead)
async def read_device(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> DeviceRead:
    db_device = await crud_devices.get(db=db, id=id, is_deleted=False, schema_to_select=DeviceRead)
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
