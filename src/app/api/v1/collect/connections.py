from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_connections import crud_connections
from ....schemas.collect.connection import ConnectionCreate, ConnectionCreateInternal, ConnectionRead, ConnectionUpdate
from ....schemas.collect.plc_type import PlcTypeRead
from ....models.collect.plc_type import PlcType

router = APIRouter(tags=["connections"])


@router.post("/connection", status_code=201)
async def write_connection(
    request: Request, connection: ConnectionCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ConnectionRead:
    connection_internal_dict = connection.model_dump()
    db_connection = await crud_connections.get(db=db, name=connection_internal_dict["name"])
    if db_connection:
        if db_connection["is_deleted"]:
            await crud_connections.db_delete(db=db, id=db_connection["id"])
        else:
            raise DuplicateValueException("Connection Name not available")

    connection_internal_dict["update_user"] = None
    connection_internal = ConnectionCreateInternal(**connection_internal_dict)
    created_connection = await crud_connections.create(db=db, object=connection_internal)

    connection_read = await crud_connections.get_joined(
        db=db,
        id=created_connection.id,
        join_model=PlcType,
        join_schema_to_select=PlcTypeRead,
        nest_joins=True,
        schema_to_select=ConnectionRead
    )
    if connection_read is None:
        raise NotFoundException("Created connection not found")

    return cast(ConnectionRead, connection_read)


# unpaginated response for connections
@router.get("/connections", response_model=dict[str, List[ConnectionRead]])
async def read_connections(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    template_id: int = Query(None)
) -> dict[str, List[ConnectionRead]]:
    if template_id:
        connections_data = await crud_connections.get_multi_joined(
            db=db,
            template_id=template_id,
            join_model=PlcType,
            join_schema_to_select=PlcTypeRead,
            nest_joins=True,
            schema_to_select=ConnectionRead,
            is_deleted=False
        )
    else:
        connections_data = await crud_connections.get_multi_joined(
            db=db,
            join_model=PlcType,
            join_schema_to_select=PlcTypeRead,
            nest_joins=True,
            schema_to_select=ConnectionRead,
            is_deleted=False
        )
    response: dict[str, List[ConnectionRead]] = {"data": cast(List[ConnectionRead], connections_data["data"])}
    return response


@router.get("/connection/{id}", response_model=ConnectionRead)
async def read_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> ConnectionRead:
    db_connection = await crud_connections.get_joined(
        db=db,
        id=id,
        join_model=PlcType,
        join_schema_to_select=PlcTypeRead,
        nest_joins=True,
        is_deleted=False,
        schema_to_select=ConnectionRead
    )
    if db_connection is None:
        raise NotFoundException("Connection not found")

    return cast(ConnectionRead, db_connection)


@router.patch("/connection/{id}")
async def patch_connection(
    request: Request, id: int, values: ConnectionUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_connection = await crud_connections.get(db=db, id=id, schema_to_select=ConnectionRead)
    if db_connection is None:
        raise NotFoundException("Connection not found")

    if values.name and values.name != db_connection["name"]:
        existing_connection = await crud_connections.get(db=db, name=values.name)
        if existing_connection:
            if existing_connection["is_deleted"]:
                await crud_connections.db_delete(db=db, id=existing_connection["id"])
            else:
                raise DuplicateValueException("Connection Name not available")

    await crud_connections.update(db=db, object=values, id=id)
    return {"message": "Connection updated"}


@router.delete("/connection/{id}")
async def erase_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_connection = await crud_connections.get(db=db, id=id, schema_to_select=ConnectionRead)
    if db_connection is None:
        raise NotFoundException("Connection not found")

    await crud_connections.delete(db=db, id=id)
    return {"message": "Connection deleted"}
