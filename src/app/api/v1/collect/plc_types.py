from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_plc_types import crud_plc_types
from ....schemas.plc_type import PlcTypeCreate, PlcTypeCreateInternal, PlcTypeRead, PlcTypeUpdate

router = APIRouter(tags=["plc_types"])


@router.post("/plc-type", status_code=201)
async def write_plc_type(
    request: Request, plc_type: PlcTypeCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> PlcTypeRead:
    plc_type_internal_dict = plc_type.model_dump()
    db_plc_type = await crud_plc_types.exists(db=db, name=plc_type_internal_dict["name"])
    if db_plc_type:
        raise DuplicateValueException("PlcType Name not available")

    plc_type_internal_dict["update_user"] = None
    plc_type_internal = PlcTypeCreateInternal(**plc_type_internal_dict)
    created_plc_type = await crud_plc_types.create(db=db, object=plc_type_internal)

    plc_type_read = await crud_plc_types.get(db=db, id=created_plc_type.id, schema_to_select=PlcTypeRead)
    if plc_type_read is None:
        raise NotFoundException("Created plc_type not found")

    return cast(PlcTypeRead, plc_type_read)


@router.get("/plc-types", response_model=List[PlcTypeRead])
async def read_plc_types(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[PlcTypeRead]:
    plc_types_data = await crud_plc_types.get_multi(db=db, is_deleted=False)

    return cast(List[PlcTypeRead], plc_types_data["data"])


@router.get("/plc-type/{id}", response_model=PlcTypeRead)
async def read_plc_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> PlcTypeRead:
    db_plc_type = await crud_plc_types.get(db=db, id=id, is_deleted=False, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    return cast(PlcTypeRead, db_plc_type)


@router.patch("/plc-type/{id}")
async def patch_plc_type(
    request: Request, id: int, values: PlcTypeUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_plc_type = await crud_plc_types.get(db=db, id=id, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    existing_plc_type = await crud_plc_types.exists(db=db, name=values.name)
    if existing_plc_type:
        raise DuplicateValueException("PlcType Name not available")

    await crud_plc_types.update(db=db, object=values, id=id)
    return {"message": "PlcType updated"}


@router.delete("/plc-type/{id}")
async def erase_plc_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_plc_type = await crud_plc_types.get(db=db, id=id, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    await crud_plc_types.delete(db=db, id=id)
    return {"message": "PlcType deleted"}
