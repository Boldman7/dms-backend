from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_variables import crud_variables
from ....schemas.collect.variable import VariableCreate, VariableCreateInternal, VariableRead, VariableUpdate

router = APIRouter(tags=["variables"])


@router.post("/variable", status_code=201)
async def write_variable(
    request: Request, variable: VariableCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> VariableRead:
    variable_internal_dict = variable.model_dump()
    db_variable = await crud_variables.exists(db=db, name=variable_internal_dict["name"])
    if db_variable:
        raise DuplicateValueException("Variable Name not available")

    variable_internal_dict["update_user"] = None
    variable_internal = VariableCreateInternal(**variable_internal_dict)
    created_variable = await crud_variables.create(db=db, object=variable_internal)

    variable_read = await crud_variables.get(db=db, id=created_variable.id, schema_to_select=VariableRead)
    if variable_read is None:
        raise NotFoundException("Created variable not found")

    return cast(VariableRead, variable_read)


# paginated response for variables
@router.get("/variables", response_model=PaginatedListResponse[VariableRead])
async def read_variables(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    variables_data = await crud_variables.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, is_deleted=False,)

    response: dict[str, Any] = paginated_response(crud_data=variables_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/variable/{id}", response_model=VariableRead)
async def read_variable(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> VariableRead:
    db_variable = await crud_variables.get(db=db, id=id, is_deleted=False, schema_to_select=VariableRead)
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

    existing_variable = await crud_variables.exists(db=db, name=values.name)
    if existing_variable:
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
