from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.equipment.crud_data_sources import crud_data_sources
from ....schemas.data_source import DataSourceCreate, DataSourceCreateInternal, DataSourceRead, DataSourceUpdate

router = APIRouter(tags=["data_sources"])


@router.post("/data-source", status_code=201)
async def write_data_source(
    request: Request, data_source: DataSourceCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> DataSourceRead:
    data_source_internal_dict = data_source.model_dump()
    db_data_source = await crud_data_sources.exists(db=db, name=data_source_internal_dict["name"])
    if db_data_source:
        raise DuplicateValueException("DataSource Name not available")

    data_source_internal_dict["update_user"] = None
    data_source_internal = DataSourceCreateInternal(**data_source_internal_dict)
    created_data_source = await crud_data_sources.create(db=db, object=data_source_internal)

    data_source_read = await crud_data_sources.get(db=db, id=created_data_source.id, schema_to_select=DataSourceRead)
    if data_source_read is None:
        raise NotFoundException("Created data_source not found")

    return cast(DataSourceRead, data_source_read)


# paginated response for data_sources
@router.get("/data-sources", response_model=PaginatedListResponse[DataSourceRead])
async def read_data_sources(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    data_sources_data = await crud_data_sources.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, is_deleted=False,)

    response: dict[str, Any] = paginated_response(crud_data=data_sources_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/data-source/{id}", response_model=DataSourceRead)
async def read_data_source(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> DataSourceRead:
    db_data_source = await crud_data_sources.get(db=db, id=id, is_deleted=False, schema_to_select=DataSourceRead)
    if db_data_source is None:
        raise NotFoundException("DataSource not found")

    return cast(DataSourceRead, db_data_source)


@router.patch("/data-source/{id}")
async def patch_data_source(
    request: Request, id: int, values: DataSourceUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_data_source = await crud_data_sources.get(db=db, id=id, schema_to_select=DataSourceRead)
    if db_data_source is None:
        raise NotFoundException("DataSource not found")

    existing_data_source = await crud_data_sources.exists(db=db, name=values.name)
    if existing_data_source:
        raise DuplicateValueException("DataSource Name not available")

    await crud_data_sources.update(db=db, object=values, id=id)
    return {"message": "DataSource updated"}


@router.delete("/data-source/{id}")
async def erase_data_source(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_data_source = await crud_data_sources.get(db=db, id=id, schema_to_select=DataSourceRead)
    if db_data_source is None:
        raise NotFoundException("DataSource not found")

    await crud_data_sources.delete(db=db, id=id)
    return {"message": "DataSource deleted"}
