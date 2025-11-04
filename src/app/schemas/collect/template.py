from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ...schemas.collect.smart_hardware_type import SmartHardwareTypeRead


class TemplateBase(BaseModel):
    name: Annotated[str, Field(examples=["template name"])]


class Template(TimestampSchema, TemplateBase, UUIDSchema, PersistentDeletion):
    pass


class TemplateRead(TemplateBase):
    id: int
    smart_hardware_type_id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class TemplateReadJoined(TemplateBase):
    id: int
    smart_hardware_type_id: int
    smart_hardware_type: SmartHardwareTypeRead
    connection_count: int = 0

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class TemplateCreate(TemplateBase):
    smart_hardware_type_id: int


class TemplateCreateInternal(TemplateCreate):
    update_user: int | None


class TemplateUpdate(TemplateBase):
    pass


class TemplateUpdateInternal(TemplateUpdate):
    update_user: int | None
    updated_at: datetime


class TemplateCopy(TemplateBase):
    smart_hardware_type_id: int


class TemplateCopyInternal(TemplateCopy):
    update_user: int | None


class TemplateDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
