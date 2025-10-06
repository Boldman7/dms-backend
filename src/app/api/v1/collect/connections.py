from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_connections import crud_connections
from ....schemas.collect.connection import ConnectionCreate, ConnectionCreateInternal, ConnectionReadJoined, ConnectionUpdate
from ....models.collect.connection import Connection
from ....models.collect.plc_type import PlcType
from ....schemas.collect.plc_type import PlcTypeRead
from ....models.collect.smart_hardware import SmartHardware
from ....schemas.collect.smart_hardware import SmartHardwareReadJoined

router = APIRouter(tags=["connections"])


# @router.post("/connection", status_code=201)
# async def write_connection(
#     request: Request, connection: ConnectionCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
# ) -> ConnectionReadJoined:
#     connection_internal_dict = connection.model_dump()
#     db_connection = await crud_connections.get(db=db, name=connection_internal_dict["name"])
#     if db_connection:
#         if db_connection["is_deleted"]:
#             await crud_connections.db_delete(db=db, id=db_connection["id"])
#         else:
#             raise DuplicateValueException("Connection Name not available")

#     connection_internal_dict["update_user"] = None
#     connection_internal = ConnectionCreateInternal(**connection_internal_dict)
#     created_connection = await crud_connections.create(db=db, object=connection_internal)

#     connection_read = await crud_connections.get_joined(
#         db=db,
#         id=created_connection.id,
#         join_model=PlcType,
#         join_schema_to_select=PlcTypeRead,
#         nest_joins=True,
#         schema_to_select=ConnectionReadJoined
#     )
#     if connection_read is None:
#         raise NotFoundException("Created connection not found")

#     return cast(ConnectionReadJoined, connection_read)


# unpaginated response for connections
@router.get("/connections", response_model=dict[str, List[ConnectionReadJoined] | int])
async def read_connections(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    smart_hardware_id: int = Query(None),
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1)
) -> dict[str, List[ConnectionReadJoined] | int]:
    offset = (page - 1) * items_per_page
    query = (
        select(Connection)
        .options(
            selectinload(Connection.plc_type),
            selectinload(Connection.smart_hardware).selectinload(SmartHardware.company)
        )
        .where(Connection.is_deleted == False)
        .offset(offset)
        .limit(items_per_page)
    )
    if smart_hardware_id:
        query = query.where(Connection.smart_hardware_id == smart_hardware_id)
    result = await db.execute(query)
    connections = result.scalars().all()
    # Get total count for pagination
    count_query = select(func.count()).select_from(Connection).where(Connection.is_deleted == False)
    if smart_hardware_id:
        count_query = count_query.where(Connection.smart_hardware_id == smart_hardware_id)
    total_count = await db.scalar(count_query)
    response: dict[str, List[ConnectionReadJoined] | int] = {"data": connections, "total_count": total_count, "page": page, "items_per_page": items_per_page}
    return response


# @router.get("/connection/{id}", response_model=ConnectionReadJoined)
# async def read_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> ConnectionReadJoined:
#     db_connection = await crud_connections.get_joined(
#         db=db,
#         id=id,
#         join_model=PlcType,
#         join_schema_to_select=PlcTypeRead,
#         nest_joins=True,
#         is_deleted=False,
#         schema_to_select=ConnectionReadJoined
#     )
#     if db_connection is None:
#         raise NotFoundException("Connection not found")

#     return cast(ConnectionReadJoined, db_connection)


@router.patch("/connection/{id}")
async def patch_connection(
    request: Request, id: int, values: ConnectionUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_connection = await crud_connections.get(db=db, id=id, schema_to_select=ConnectionReadJoined)
    if db_connection is None or db_connection["is_deleted"]:
        raise NotFoundException("Connection not found")

    await crud_connections.update(db=db, object=values, id=id)
    return {"message": "Connection updated"}


# @router.delete("/connection/{id}")
# async def erase_connection(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
#     db_connection = await crud_connections.get(db=db, id=id, schema_to_select=ConnectionReadJoined)
#     if db_connection is None:
#         raise NotFoundException("Connection not found")

#     await crud_connections.delete(db=db, id=id)
#     return {"message": "Connection deleted"}
