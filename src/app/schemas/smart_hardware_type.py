from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class SmartHardwareTypeBase(BaseModel):
    name: Annotated[str, Field(examples=["smart_hardware_type name"])]


class SmartHardwareType(TimestampSchema, SmartHardwareTypeBase, UUIDSchema, PersistentDeletion):
    pass

class SmartHardwareTypeRead(SmartHardwareTypeBase):
    id: int
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class SmartHardwareTypeCreate(SmartHardwareTypeBase):
    pass


class SmartHardwareTypeCreateInternal(SmartHardwareTypeCreate):
    update_user: int | None


class SmartHardwareTypeUpdate(SmartHardwareTypeBase):
    pass


class SmartHardwareTypeUpdateInternal(SmartHardwareTypeUpdate):
    update_user: int | None
    updated_at: datetime


class SmartHardwareTypeDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
