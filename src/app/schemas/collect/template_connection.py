from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .plc_type import PlcTypeRead


class TemplateConnectionBase(BaseModel):
    name: Annotated[str, Field(examples=["template connection name"])]
    plc_type_id: int
    ip_address: str | None = None
    port: int | None = None
    station_number: str | None = None

class TemplateConnection(TimestampSchema, TemplateConnectionBase, UUIDSchema, PersistentDeletion):
    pass


class TemplateConnectionRead(TemplateConnectionBase):
    id: int
    plc_type: PlcTypeRead

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class TemplateConnectionReadJoined(TemplateConnectionBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class TemplateConnectionCreate(TemplateConnectionBase):
    template_id: int


class TemplateConnectionCreateInternal(TemplateConnectionCreate):
    update_user: int | None


class TemplateConnectionUpdate(TemplateConnectionBase):
    pass


class TemplateConnectionUpdateInternal(TemplateConnectionUpdate):
    update_user: int | None
    updated_at: datetime


class TemplateConnectionDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
