from typing import Annotated, Any, cast
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from ....models.collect.template import Template

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_templates import crud_templates
from ....schemas.collect.template import TemplateCreate, TemplateCreateInternal, TemplateRead, TemplateUpdate
from ....schemas.collect.smart_hardware_type import SmartHardwareTypeRead
from ....models.collect.smart_hardware_type import SmartHardwareType

router = APIRouter(tags=["templates"])


@router.post("/template", status_code=201)
async def write_template(
    request: Request, template: TemplateCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> TemplateRead:
    template_internal_dict = template.model_dump()
    db_template = await crud_templates.get(db=db, name=template_internal_dict["name"])
    if db_template:
        if db_template["is_deleted"]:
            await crud_templates.db_delete(db=db, id=db_template["id"])
        else:
            raise DuplicateValueException("Template Name not available")
        
    template_internal_dict["update_user"] = None
    template_internal = TemplateCreateInternal(**template_internal_dict)
    created_template = await crud_templates.create(db=db, object=template_internal)

    template_read = await crud_templates.get_joined(
        db=db,
        id=created_template.id,
        join_model=SmartHardwareType,
        nest_joins=True,
        schema_to_select=TemplateRead,
        join_schema_to_select=SmartHardwareTypeRead,
        is_deleted=False,
    )
    if template_read is None:
        raise NotFoundException("Created template not found")

    return cast(TemplateRead, template_read)


# paginated response for templates
@router.get("/templates", response_model=PaginatedListResponse[TemplateRead])
async def read_templates(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    templates_data = await crud_templates.get_multi_joined(
        db=db,
        join_model=SmartHardwareType,
        nest_joins=True,
        schema_to_select=TemplateRead,
        join_schema_to_select=SmartHardwareTypeRead,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        name__contains=name,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=templates_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/template/{id}", response_model=TemplateRead)
async def read_template(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> TemplateRead:
    db_template = await crud_templates.get_joined(
        db=db,
        id=id,
        join_model=SmartHardwareType,
        nest_joins=True,
        schema_to_select=TemplateRead,
        join_schema_to_select=SmartHardwareTypeRead,
        is_deleted=False,
    )
    if db_template is None:
        raise NotFoundException("Template not found")

    return cast(TemplateRead, db_template)


@router.patch("/template/{id}")
async def patch_template(
    request: Request, id: int, values: TemplateUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_template = await crud_templates.get(db=db, id=id, schema_to_select=TemplateRead)
    if db_template is None:
        raise NotFoundException("Template not found")

    existing_template = await crud_templates.exists(db=db, name=values.name)
    if existing_template:
        raise DuplicateValueException("Template Name not available")

    await crud_templates.update(db=db, object=values, id=id)
    return {"message": "Template updated"}


@router.delete("/template/{id}")
async def erase_template(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_template = await crud_templates.get(db=db, id=id, schema_to_select=TemplateRead)
    if db_template is None:
        raise NotFoundException("Template not found")

    await crud_templates.delete(db=db, id=id)
    return {"message": "Template deleted"}
