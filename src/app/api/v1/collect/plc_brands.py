from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_plc_brands import crud_plc_brands
from ....schemas.plc_brand import PlcBrandCreate, PlcBrandCreateInternal, PlcBrandRead, PlcBrandUpdate

router = APIRouter(tags=["plc_brands"])


@router.post("/plc-brand", status_code=201)
async def write_plc_brand(
    request: Request, plc_brand: PlcBrandCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> PlcBrandRead:
    plc_brand_internal_dict = plc_brand.model_dump()
    db_plc_brand = await crud_plc_brands.exists(db=db, name=plc_brand_internal_dict["name"])
    if db_plc_brand:
        raise DuplicateValueException("PlcBrand Name not available")

    plc_brand_internal_dict["update_user"] = None
    plc_brand_internal = PlcBrandCreateInternal(**plc_brand_internal_dict)
    created_plc_brand = await crud_plc_brands.create(db=db, object=plc_brand_internal)

    plc_brand_read = await crud_plc_brands.get(db=db, id=created_plc_brand.id, schema_to_select=PlcBrandRead)
    if plc_brand_read is None:
        raise NotFoundException("Created plc_brand not found")

    return cast(PlcBrandRead, plc_brand_read)


@router.get("/plc-brands", response_model=List[PlcBrandRead])
async def read_plc_brands(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[PlcBrandRead]:
    plc_brands_data = await crud_plc_brands.get_multi(db=db, is_deleted=False)

    return cast(List[PlcBrandRead], plc_brands_data["data"])


@router.get("/plc-brand/{id}", response_model=PlcBrandRead)
async def read_plc_brand(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> PlcBrandRead:
    db_plc_brand = await crud_plc_brands.get(db=db, id=id, is_deleted=False, schema_to_select=PlcBrandRead)
    if db_plc_brand is None:
        raise NotFoundException("PlcBrand not found")

    return cast(PlcBrandRead, db_plc_brand)


@router.patch("/plc-brand/{id}")
async def patch_plc_brand(
    request: Request, id: int, values: PlcBrandUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_plc_brand = await crud_plc_brands.get(db=db, id=id, schema_to_select=PlcBrandRead)
    if db_plc_brand is None:
        raise NotFoundException("PlcBrand not found")

    existing_plc_brand = await crud_plc_brands.exists(db=db, name=values.name)
    if existing_plc_brand:
        raise DuplicateValueException("PlcBrand Name not available")

    await crud_plc_brands.update(db=db, object=values, id=id)
    return {"message": "PlcBrand updated"}


@router.delete("/plc-brand/{id}")
async def erase_plc_brand(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_plc_brand = await crud_plc_brands.get(db=db, id=id, schema_to_select=PlcBrandRead)
    if db_plc_brand is None:
        raise NotFoundException("PlcBrand not found")

    await crud_plc_brands.delete(db=db, id=id)
    return {"message": "PlcBrand deleted"}
