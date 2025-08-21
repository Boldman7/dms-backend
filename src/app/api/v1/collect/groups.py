from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_groups import crud_groups
from ....schemas.collect.group import GroupCreate, GroupCreateInternal, GroupRead, GroupUpdate

router = APIRouter(tags=["groups"])


@router.post("/group", status_code=201)
async def write_group(
    request: Request, group: GroupCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> GroupRead:
    group_internal_dict = group.model_dump()
    db_group = await crud_groups.get(db=db, name=group_internal_dict["name"])
    if db_group:
        if db_group["is_deleted"]:
            await crud_groups.db_delete(db=db, id=db_group["id"])
        else:
            raise DuplicateValueException("Group Name not available")
        
    group_internal_dict["update_user"] = None
    group_internal = GroupCreateInternal(**group_internal_dict)
    created_group = await crud_groups.create(db=db, object=group_internal)

    group_read = await crud_groups.get(db=db, id=created_group.id, schema_to_select=GroupRead)
    if group_read is None:
        raise NotFoundException("Created group not found")

    return cast(GroupRead, group_read)


# unpaginated response for groups
@router.get("/groups", response_model=dict[str, List[GroupRead]])
async def read_groups(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query("")
) -> dict[str, List[GroupRead]]:
    groups_data = await crud_groups.get_multi(
        db=db,
        name__contains=name,
        is_deleted=False
    )

    response: dict[str, List[GroupRead]] = {"data": cast(List[GroupRead], groups_data["data"])}
    return response


@router.get("/group/{id}", response_model=GroupRead)
async def read_group(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> GroupRead:
    db_group = await crud_groups.get(db=db, id=id, is_deleted=False, schema_to_select=GroupRead)
    if db_group is None:
        raise NotFoundException("Group not found")

    return cast(GroupRead, db_group)


@router.patch("/group/{id}")
async def patch_group(
    request: Request, id: int, values: GroupUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_group = await crud_groups.get(db=db, id=id, schema_to_select=GroupRead)
    if db_group is None:
        raise NotFoundException("Group not found")
    
    if values.name and values.name != db_group["name"]:
        existing_group = await crud_groups.get(db=db, name=values.name)
        if existing_group:
            if existing_group["is_deleted"]:
                await crud_groups.db_delete(db=db, id=existing_group["id"])
            else:
                raise DuplicateValueException("Group Name not available")

    await crud_groups.update(db=db, object=values, id=id)
    return {"message": "Group updated"}


@router.delete("/group/{id}")
async def erase_group(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_group = await crud_groups.get(db=db, id=id, schema_to_select=GroupRead)
    if db_group is None:
        raise NotFoundException("Group not found")

    await crud_groups.delete(db=db, id=id)
    return {"message": "Group deleted"}
