from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_template import crud_templates
from ....schemas.template import TemplateCreate, TemplateCreateInternal, TemplateRead, TemplateUpdate

router = APIRouter(tags=["templates"])


# @router.post("/template", dependencies=[Depends(get_current_superuser)], status_code=201)
# async def write_template(
#     request: Request, template: TemplateCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
# ) -> TemplateRead:
#     template_internal_dict = template.model_dump()
#     db_template = await crud_templates.exists(db=db, name=template_internal_dict["name"])
#     if db_template:
#         raise DuplicateValueException("Template Name not available")

#     template_internal = TemplateCreateInternal(**template_internal_dict)
#     created_template = await crud_templates.create(db=db, object=template_internal)

#     template_read = await crud_templates.get(db=db, id=created_template.id, schema_to_select=TemplateRead)
#     if template_read is None:
#         raise NotFoundException("Created template not found")

#     return cast(TemplateRead, template_read)


@router.get("/templates", response_model=PaginatedListResponse[TemplateRead])
async def read_templates(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    templates_data = await crud_templates.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page)

    response: dict[str, Any] = paginated_response(crud_data=templates_data, page=page, items_per_page=items_per_page)
    return response


# @router.get("/template/{name}", response_model=TemplateRead)
# async def read_template(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> TemplateRead:
#     db_template = await crud_templates.get(db=db, name=name, schema_to_select=TemplateRead)
#     if db_template is None:
#         raise NotFoundException("Template not found")

#     return cast(TemplateRead, db_template)


# @router.patch("/template/{name}", dependencies=[Depends(get_current_superuser)])
# async def patch_template(
#     request: Request, name: str, values: TemplateUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
# ) -> dict[str, str]:
#     db_template = await crud_templates.get(db=db, name=name, schema_to_select=TemplateRead)
#     if db_template is None:
#         raise NotFoundException("Template not found")

#     await crud_templates.update(db=db, object=values, name=name)
#     return {"message": "Template updated"}


# @router.delete("/template/{name}", dependencies=[Depends(get_current_superuser)])
# async def erase_template(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
#     db_template = await crud_templates.get(db=db, name=name, schema_to_select=TemplateRead)
#     if db_template is None:
#         raise NotFoundException("Template not found")

#     await crud_templates.delete(db=db, name=name)
#     return {"message": "Template deleted"}
