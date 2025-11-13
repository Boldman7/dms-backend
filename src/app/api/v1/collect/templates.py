from typing import Annotated, Any, cast
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException, BadRequestException
from ....crud.collect.crud_templates import crud_templates
from ....crud.collect.crud_template_connections import crud_template_connections
from ....schemas.collect.template import TemplateCreate, TemplateCreateInternal, TemplateRead, TemplateReadJoined, TemplateUpdate, TemplateCopy, TemplateCopyInternal
from ....schemas.collect.smart_hardware_type import SmartHardwareTypeRead
from ....models.collect.smart_hardware_type import SmartHardwareType

router = APIRouter(tags=["templates"])


@router.post("/template", status_code=201)
async def write_template(
    request: Request, template: TemplateCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> TemplateReadJoined:
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
        join_schema_to_select=SmartHardwareTypeRead,
        nest_joins=True,
        schema_to_select=TemplateReadJoined,
        is_deleted=False,
    )
    if template_read is None:
        raise NotFoundException("Created template not found")

    return template_read


# paginated response for templates
@router.get("/templates", response_model=PaginatedListResponse[TemplateReadJoined])
async def read_templates(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10), 
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    sort_by: str = Query("updated_at", description="Field to sort by"),
) -> dict:
    
    if sort not in ["asc", "desc"]:
        return BadRequestException("sort must be 'asc' or 'desc'");

    # Validate sort_by field to prevent SQL injection
    allowed_sort_fields = ["updated_at", "created_at", "name", "id"]
    if sort_by not in allowed_sort_fields:
        return BadRequestException(f"sort_by must be one of: {', '.join(allowed_sort_fields)}")

    templates_data = await crud_templates.get_multi_joined(
        db=db,
        join_model=SmartHardwareType,
        join_schema_to_select=SmartHardwareTypeRead,
        nest_joins=True,
        schema_to_select=TemplateReadJoined,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        name__contains=name,
        is_deleted=False,
        sort_columns=sort_by,
        sort_orders=sort,
    )

    # Extract templates and total_count from the dictionary
    templates = templates_data['data']
    total_count = templates_data['total_count']

    # Get template IDs from the current page
    template_ids = [template['id'] for template in templates]
    
    # Count connections for each template using the built-in count method
    connection_counts = {}
    for template_id in template_ids:
        count = await crud_template_connections.count(
            db=db,
            template_id=template_id,
            is_deleted=False
        )
        connection_counts[template_id] = count

    # Add connection_count to each template dictionary and convert to TemplateReadJoined
    updated_templates = []
    for template in templates:
        # Since template is already a dictionary, just add the connection_count
        template['connection_count'] = connection_counts.get(template['id'], 0)
        # Convert the dictionary to TemplateReadJoined object
        updated_templates.append(TemplateReadJoined(**template))
    
    # Reconstruct the data in the expected format
    final_data = {
        'data': updated_templates,
        'total_count': total_count
    }

    response: dict[str, Any] = paginated_response(crud_data=final_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/template/{id}", response_model=TemplateReadJoined)
async def read_template(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> TemplateReadJoined:
    db_template = await crud_templates.get_joined(
        db=db,
        id=id,
        join_model=SmartHardwareType,
        join_schema_to_select=SmartHardwareTypeRead,
        nest_joins=True,
        schema_to_select=TemplateReadJoined,
        is_deleted=False,
    )
    if db_template is None:
        raise NotFoundException("Template not found")

    return db_template


@router.patch("/template/{id}")
async def patch_template(
    request: Request, id: int, values: TemplateUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_template = await crud_templates.get(db=db, id=id, schema_to_select=TemplateRead)
    if db_template is None:
        raise NotFoundException("Template not found")

    if values.name and values.name != db_template["name"]:
        existing_template = await crud_templates.get(db=db, name=values.name)
        if existing_template:
            if existing_template["is_deleted"]:
                await crud_templates.db_delete(db=db, id=existing_template["id"])
            else:
                raise DuplicateValueException("Template Name not available")

    await crud_templates.update(db=db, object=values, id=id)
    return {"message": "Template updated"}


@router.post("/template/{id}/copy")
async def copy_template(
    request: Request, id: int, template: TemplateCopy, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    old_template = await crud_templates.get(db=db, id=id, schema_to_select=TemplateRead)
    if old_template is None:
        raise NotFoundException("Template not found")

    template_internal_dict = template.model_dump()
    same_name_template = await crud_templates.get(db=db, name=template_internal_dict["name"])
    if same_name_template:
        if same_name_template["is_deleted"]:
            await crud_templates.db_delete(db=db, id=same_name_template["id"])
        else:
            raise DuplicateValueException("Template Name not available")


    old_template["name"] = template_internal_dict["name"]
    old_template["smart_hardware_type_id"] = template_internal_dict["smart_hardware_type_id"]
    template_internal = TemplateCopyInternal(**old_template)
    await crud_templates.create(db=db, object=template_internal)

    return {"message": "Template copied"}


@router.delete("/template/{id}")
async def erase_template(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_template = await crud_templates.get(db=db, id=id, schema_to_select=TemplateRead)
    if db_template is None:
        raise NotFoundException("Template not found")

    await crud_templates.delete(db=db, id=id)
    return {"message": "Template deleted"}
