from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.permission.crud_records import crud_records
from ....schemas.permission.record import RecordCreate, RecordCreateInternal, RecordRead, RecordUpdate
from ....schemas.base.company import CompanyRead
from ....models.base.company import Company

router = APIRouter(tags=["records"])


@router.post("/record", status_code=201)
async def write_record(
    request: Request, record: RecordCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RecordRead:
    record_internal_dict = record.model_dump()
        
    record_internal_dict["update_user"] = None
    record_internal = RecordCreateInternal(**record_internal_dict)
    created_record = await crud_records.create(db=db, object=record_internal)

    record_read = await crud_records.get(
        db=db,
        id=created_record.id,
        schema_to_select=RecordRead,
        is_deleted=False,
    )
    if record_read is None:
        raise NotFoundException("Created record not found")

    return record_read


# paginated response for records
@router.get("/records", response_model=PaginatedListResponse[RecordRead])
async def read_records(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    keyword: str = Query(""),
    license_id: int | None = None,
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    if license_id:
        records_data = await crud_records.get_multi(
            db=db,
            schema_to_select=RecordRead,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            license_id=license_id,
            content__contains=keyword,
            is_deleted=False,
        )
    else:
        records_data = await crud_records.get_multi(
            db=db,
            schema_to_select=RecordRead,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            content__contains=keyword,
            is_deleted=False,
        )

    response: dict[str, Any] = paginated_response(crud_data=records_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/record/{id}", response_model=RecordRead)
async def read_record(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> RecordRead:
    db_record = await crud_records.get_joined(
        db=db,
        id=id,
        join_model=Company,
        join_schema_to_select=CompanyRead,
        nest_joins=True,
        schema_to_select=RecordRead,
        is_deleted=False,
    )
    if db_record is None:
        raise NotFoundException("Record not found")

    return db_record


@router.patch("/record/{id}")
async def patch_record(
    request: Request, id: int, values: RecordUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_record = await crud_records.get(db=db, id=id, schema_to_select=RecordRead)
    if db_record is None:
        raise NotFoundException("Record not found")

    await crud_records.update(db=db, object=values, id=id)
    return {"message": "Record updated"}


@router.delete("/record/{id}")
async def erase_record(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_record = await crud_records.get(db=db, id=id, schema_to_select=RecordRead)
    if db_record is None:
        raise NotFoundException("Record not found")

    await crud_records.delete(db=db, id=id)
    return {"message": "Record deleted"}
