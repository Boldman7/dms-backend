from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class PlcTypeBase(BaseModel):
    name: Annotated[str, Field(examples=["plc type name"])]
    plc_brand_id: int
    controller_id: str | None = None
    controller_name: str | None = None
    interface_type: int


class PlcType(TimestampSchema, PlcTypeBase, UUIDSchema, PersistentDeletion):
    pass


class PlcTypeRead(PlcTypeBase):
    id: int
    plc_brand_id: int
    controller_id: str | None
    controller_name: str | None
    interface_type: int
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class PlcTypeCreate(PlcTypeBase):
    pass


class PlcTypeCreateInternal(PlcTypeCreate):
    update_user: int | None


class PlcTypeUpdate(PlcTypeBase):
    pass


class PlcTypeUpdateInternal(PlcTypeUpdate):
    update_user: int | None
    updated_at: datetime


class PlcTypeDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
