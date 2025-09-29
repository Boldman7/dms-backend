from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_template_connections import crud_template_connections
from ....schemas.collect.template_connection import TemplateConnectionCreate, TemplateConnectionCreateInternal, TemplateConnectionReadJoined, TemplateConnectionUpdate
from ....schemas.collect.plc_type import PlcTypeRead
from ....models.collect.plc_type import PlcType

router = APIRouter(tags=["template-connections"])


@router.post("/template-connection", status_code=201)
async def write_connection(
    request: Request, connection: TemplateConnectionCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> TemplateConnectionReadJoined:
    connection_internal_dict = connection.model_dump()
    db_connection = await crud_template_connections.get(db=db, name=connection_internal_dict["name"])
    if db_connection:
        if db_connection["is_deleted"]:
            await crud_template_connections.db_delete(db=db, id=db_connection["id"])
        else:
            raise DuplicateValueException("TemplateConnection Name not available")

    connection_internal_dict["update_user"] = None
    connection_internal = TemplateConnectionCreateInternal(**connection_internal_dict)
    created_connection = await crud_template_connections.create(db=db, object=connection_internal)

    connection_read = await crud_template_connections.get_joined(
        db=db,
        id=created_connection.id,
        join_model=PlcType,
        join_schema_to_select=PlcTypeRead,
        nest_joins=True,
        schema_to_select=TemplateConnectionReadJoined
    )
    if connection_read is None:
        raise NotFoundException("Created connection not found")

    return cast(TemplateConnectionReadJoined, connection_read)


# unpaginated response for connections
@router.get("/template-connections", response_model=dict[str, List[TemplateConnectionReadJoined]])
async def read_connections(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    template_id: int = Query(None)
) -> dict[str, List[TemplateConnectionReadJoined]]:
    if template_id:
        connections_data = await crud_template_connections.get_multi_joined(
            db=db,
            template_id=template_id,
            join_model=PlcType,
            join_schema_to_select=PlcTypeRead,
            nest_joins=True,
            schema_to_select=TemplateConnectionReadJoined,
            is_deleted=False
        )
    else:
        connections_data = await crud_template_connections.get_multi_joined(
            db=db,
            join_model=PlcType,
            join_schema_to_select=PlcTypeRead,
            nest_joins=True,
            schema_to_select=TemplateConnectionReadJoined,
            is_deleted=False
        )
    response: dict[str, List[TemplateConnectionReadJoined]] = {"data": cast(List[TemplateConnectionReadJoined], connections_data["data"])}
    return response


@router.get("/template-connection/{id}", response_model=TemplateConnectionReadJoined)
async def read_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> TemplateConnectionReadJoined:
    db_connection = await crud_template_connections.get_joined(
        db=db,
        id=id,
        join_model=PlcType,
        join_schema_to_select=PlcTypeRead,
        nest_joins=True,
        is_deleted=False,
        schema_to_select=TemplateConnectionReadJoined
    )
    if db_connection is None:
        raise NotFoundException("TemplateConnection not found")

    return cast(TemplateConnectionReadJoined, db_connection)


@router.patch("/template-connection/{id}")
async def patch_connection(
    request: Request, id: int, values: TemplateConnectionUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_connection = await crud_template_connections.get(db=db, id=id, schema_to_select=TemplateConnectionReadJoined)
    if db_connection is None:
        raise NotFoundException("TemplateConnection not found")

    if values.name and values.name != db_connection["name"]:
        existing_connection = await crud_template_connections.get(db=db, name=values.name)
        if existing_connection:
            if existing_connection["is_deleted"]:
                await crud_template_connections.db_delete(db=db, id=existing_connection["id"])
            else:
                raise DuplicateValueException("TemplateConnection Name not available")

    await crud_template_connections.update(db=db, object=values, id=id)
    return {"message": "TemplateConnection updated"}


@router.delete("/template-connection/{id}")
async def erase_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_connection = await crud_template_connections.get(db=db, id=id, schema_to_select=TemplateConnectionReadJoined)
    if db_connection is None:
        raise NotFoundException("TemplateConnection not found")

    await crud_template_connections.delete(db=db, id=id)
    return {"message": "TemplateConnection deleted"}
