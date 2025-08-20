from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.permission.crud_licenses import crud_licenses
from ....schemas.permission.license import LicenseCreate, LicenseCreateInternal, LicenseRead, LicenseReadJoined, LicenseUpdate
from ....schemas.base.company import CompanyRead
from ....models.base.company import Company

router = APIRouter(tags=["licenses"])


@router.post("/license", status_code=201)
async def write_license(
    request: Request, license: LicenseCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> LicenseReadJoined:
    license_internal_dict = license.model_dump()
    db_license = await crud_licenses.get(db=db, name=license_internal_dict["name"])
    if db_license:
        if db_license["is_deleted"]:
            await crud_licenses.db_delete(db=db, id=db_license["id"])
        else:
            raise DuplicateValueException("License Name not available")
        
    license_internal_dict["update_user"] = None
    license_internal = LicenseCreateInternal(**license_internal_dict)
    created_license = await crud_licenses.create(db=db, object=license_internal)

    license_read = await crud_licenses.get_joined(
        db=db,
        id=created_license.id,
        join_model=Company,
        join_schema_to_select=CompanyRead,
        nest_joins=True,
        schema_to_select=LicenseReadJoined,
        is_deleted=False,
    )
    if license_read is None:
        raise NotFoundException("Created license not found")

    return license_read


# paginated response for licenses
@router.get("/licenses", response_model=PaginatedListResponse[LicenseReadJoined])
async def read_licenses(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    licenses_data = await crud_licenses.get_multi_joined(
        db=db,
        join_model=Company,
        join_schema_to_select=CompanyRead,
        nest_joins=True,
        schema_to_select=LicenseReadJoined,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        name__contains=name,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=licenses_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/license/{id}", response_model=LicenseReadJoined)
async def read_license(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> LicenseReadJoined:
    db_license = await crud_licenses.get_joined(
        db=db,
        id=id,
        join_model=Company,
        join_schema_to_select=CompanyRead,
        nest_joins=True,
        schema_to_select=LicenseReadJoined,
        is_deleted=False,
    )
    if db_license is None:
        raise NotFoundException("License not found")

    return db_license


@router.patch("/license/{id}")
async def patch_license(
    request: Request, id: int, values: LicenseUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_license = await crud_licenses.get(db=db, id=id, schema_to_select=LicenseRead)
    if db_license is None:
        raise NotFoundException("License not found")

    if values.name and values.name != db_license["name"]:
        existing_plc_type = await crud_licenses.exists(db=db, name=values.name)
        if existing_plc_type:
            raise DuplicateValueException("License Name not available")

    await crud_licenses.update(db=db, object=values, id=id)
    return {"message": "License updated"}


@router.delete("/license/{id}")
async def erase_license(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_license = await crud_licenses.get(db=db, id=id, schema_to_select=LicenseRead)
    if db_license is None:
        raise NotFoundException("License not found")

    await crud_licenses.delete(db=db, id=id)
    return {"message": "License deleted"}
