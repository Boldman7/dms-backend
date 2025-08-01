from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class TemplateBase(BaseModel):
    name: Annotated[str, Field(examples=["template name"])]


class Template(TimestampSchema, TemplateBase, UUIDSchema, PersistentDeletion):
    pass

class TemplateRead(TemplateBase):
    id: int
    product_model: Annotated[str, Field(examples=["product_model name"])]
    product_model_type: Annotated[str | None, Field(examples=["product_model_type name"])]
    connect_num: int
    element_num: int
    update_user: int
    created_at: datetime
    updated_at: datetime


class TemplateCreate(TemplateBase):
    product_model: Annotated[str | None, Field(default=None, examples=["product model"])]


class TemplateCreateInternal(TemplateCreate):
    update_user: int


class TemplateUpdate(TemplateBase):
    pass


class TemplateUpdateInternal(TemplateUpdate):
    update_user: int
    updated_at: datetime


class TemplateDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
