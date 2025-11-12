from typing import Annotated, Any, cast
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, Request, Query, Path
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException, BadRequestException
from ....crud.collect.crud_variables import crud_variables
from ....schemas.collect.variable import VariableCreate, VariableCreateInternal, VariableRead, VariableUpdate
from ....schemas.collect.group import GroupRead
from ....models.collect.group import Group
from ....models.collect.variable import Variable

router = APIRouter(tags=["variables"])


@router.post("/variable", status_code=201)
async def write_variable(
    request: Request, variable: VariableCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> VariableRead:
    variable_internal_dict = variable.model_dump()
    db_variable = await crud_variables.get(db=db, name=variable_internal_dict["name"])
    if db_variable:
        if db_variable["is_deleted"]:
            await crud_variables.db_delete(db=db, id=db_variable["id"])
        else:
            raise DuplicateValueException("Variable Name not available")

    variable_internal_dict["update_user"] = None
    variable_internal = VariableCreateInternal(**variable_internal_dict)
    created_variable = await crud_variables.create(db=db, object=variable_internal)

    variable_read = await crud_variables.get_joined(
        db=db,
        join_model=Group,
        join_schema_to_select=GroupRead,
        nest_joins=True,
        id=created_variable.id,
        schema_to_select=VariableRead
    )
    if variable_read is None:
        raise NotFoundException("Created variable not found")

    return cast(VariableRead, variable_read)


# paginated response for variables
@router.get("/variables", response_model=PaginatedListResponse[VariableRead])
async def read_variables(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    connection_id: int | None = Query(None),
    group_id: int | None = Query(None),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:

    if group_id:
        variables_data = await crud_variables.get_multi_joined(
            db=db,
            join_model=Group,
            join_schema_to_select=GroupRead,
            nest_joins=True,
            schema_to_select=VariableRead,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            name__contains=name,
            group_id=group_id,
            connection_id = connection_id,
            is_deleted=False,
        )
    else:
        variables_data = await crud_variables.get_multi_joined(
            db=db,
            join_model=Group,
            join_schema_to_select=GroupRead,
            nest_joins=True,
            schema_to_select=VariableRead,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            name__contains=name,
            connection_id = connection_id,
            is_deleted=False,
        )

    response: dict[str, Any] = paginated_response(crud_data=variables_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/variable/{id}", response_model=VariableRead)
async def read_variable(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> VariableRead:
    db_variable = await crud_variables.get_joined(
        db=db,
        id=id,
        join_model=Group,
        join_schema_to_select=GroupRead,
        nest_joins=True,
        is_deleted=False,
        schema_to_select=VariableRead
    )
    if db_variable is None:
        raise NotFoundException("Variable not found")

    return cast(VariableRead, db_variable)


@router.patch("/variable/{id}")
async def patch_variable(
    request: Request, id: int, values: VariableUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_variable = await crud_variables.get(db=db, id=id, schema_to_select=VariableRead)
    if db_variable is None:
        raise NotFoundException("Variable not found")

    if values.name and values.name != db_variable["name"]:
        existing_variable = await crud_variables.get(db=db, name=values.name)
        if existing_variable:
            if existing_variable["is_deleted"]:
                await crud_variables.db_delete(db=db, id=existing_variable["id"])
            else:
                raise DuplicateValueException("Variable Name not available")

    await crud_variables.update(db=db, object=values, id=id)
    return {"message": "Variable updated"}


@router.delete("/variable/{id}")
async def erase_variable(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_variable = await crud_variables.get(db=db, id=id, schema_to_select=VariableRead)
    if db_variable is None:
        raise NotFoundException("Variable not found")

    await crud_variables.delete(db=db, id=id)
    return {"message": "Variable deleted"}

@router.delete("/variables/connection/{connection_id}")
async def delete_variables(
    db: Annotated[AsyncSession, Depends(async_get_db)], 
    connection_id: int = Path(..., gt=0),
) -> dict[str, str]:
    if not connection_id:
        raise BadRequestException(
            status_code=400,
            detail="need connection id",
        )
    
    print("delete_variables", connection_id);
    # Check if any active variables exist with this connection_id
    variables = await crud_variables.get_multi(
        db=db, 
        connection_id=connection_id,
        is_deleted=False
    )
    variables_data = variables['data']

    print("delete_variables", variables_data);
    if not variables:
        raise NotFoundException("Variable not found")

    print("delete_variables: before delete");
    # Delete each variable individually
    deleted_count = 0
    for variable in variables_data:
        await crud_variables.delete(db=db, id=variable["id"])
        deleted_count += 1
    
    print("delete_variables: after delete", deleted_count);

    return {
        "message": f"Successfully deleted {deleted_count} variables",
    }

