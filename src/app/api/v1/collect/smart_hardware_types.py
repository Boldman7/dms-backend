from typing import Annotated, Any, cast, List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_smart_hardware_types import crud_smart_hardware_types
from ....schemas.smart_hardware_type import SmartHardwareTypeCreate, SmartHardwareTypeCreateInternal, SmartHardwareTypeRead, SmartHardwareTypeUpdate

router = APIRouter(tags=["smart_hardware_types"])


@router.post("/smart-hardware-type", status_code=201)
async def write_smart_hardware_type(
    request: Request, smart_hardware_type: SmartHardwareTypeCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> SmartHardwareTypeRead:
    smart_hardware_type_internal_dict = smart_hardware_type.model_dump()
    db_smart_hardware_type = await crud_smart_hardware_types.exists(db=db, name=smart_hardware_type_internal_dict["name"])
    if db_smart_hardware_type:
        raise DuplicateValueException("SmartHardwareType Name not available")

    smart_hardware_type_internal_dict["update_user"] = None
    smart_hardware_type_internal = SmartHardwareTypeCreateInternal(**smart_hardware_type_internal_dict)
    created_smart_hardware_type = await crud_smart_hardware_types.create(db=db, object=smart_hardware_type_internal)

    smart_hardware_type_read = await crud_smart_hardware_types.get(db=db, id=created_smart_hardware_type.id, schema_to_select=SmartHardwareTypeRead)
    if smart_hardware_type_read is None:
        raise NotFoundException("Created smart_hardware_type not found")

    return cast(SmartHardwareTypeRead, smart_hardware_type_read)


@router.get("/smart-hardware-types", response_model=List[SmartHardwareTypeRead])
async def read_smart_hardware_types(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[SmartHardwareTypeRead]:
    smart_hardware_types_data = await crud_smart_hardware_types.get_multi(db=db, is_deleted=False)

    return cast(List[SmartHardwareTypeRead], smart_hardware_types_data["data"])


@router.get("/smart-hardware-type/{id}", response_model=SmartHardwareTypeRead)
async def read_smart_hardware_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> SmartHardwareTypeRead:
    db_smart_hardware_type = await crud_smart_hardware_types.get(db=db, id=id, is_deleted=False, schema_to_select=SmartHardwareTypeRead)
    if db_smart_hardware_type is None:
        raise NotFoundException("SmartHardwareType not found")

    return cast(SmartHardwareTypeRead, db_smart_hardware_type)


@router.patch("/smart-hardware-type/{id}")
async def patch_smart_hardware_type(
    request: Request, id: int, values: SmartHardwareTypeUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_smart_hardware_type = await crud_smart_hardware_types.get(db=db, id=id, schema_to_select=SmartHardwareTypeRead)
    if db_smart_hardware_type is None:
        raise NotFoundException("SmartHardwareType not found")

    existing_smart_hardware_type = await crud_smart_hardware_types.exists(db=db, name=values.name)
    if existing_smart_hardware_type:
        raise DuplicateValueException("SmartHardwareType Name not available")

    await crud_smart_hardware_types.update(db=db, object=values, id=id)
    return {"message": "SmartHardwareType updated"}


@router.delete("/smart-hardware-type/{id}")
async def erase_smart_hardware_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_smart_hardware_type = await crud_smart_hardware_types.get(db=db, id=id, schema_to_select=SmartHardwareTypeRead)
    if db_smart_hardware_type is None:
        raise NotFoundException("SmartHardwareType not found")

    await crud_smart_hardware_types.delete(db=db, id=id)
    return {"message": "SmartHardwareType deleted"}
