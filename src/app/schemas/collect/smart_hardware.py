from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class SmartHardwareBase(BaseModel):
    name: Annotated[str, Field(examples=["smart hardware name"])]
    company_id: int
    location_way: int


class SmartHardware(TimestampSchema, SmartHardwareBase, UUIDSchema, PersistentDeletion):
    pass


class SmartHardwareRead(SmartHardwareBase):
    id: int
    template_id: int | None
    smart_hardware_type_id: int | None
    sync_status: int | None
    status: int | None
    upgrade_status: int | None

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class SmartHardwareCreate(SmartHardwareBase):
    code: Annotated[str, Field(examples=["smart hardware code"])]


class SmartHardwareCreateInternal(SmartHardwareCreate):
    update_user: int | None


class SmartHardwareUpdate(SmartHardwareBase):
    pass


class SmartHardwareUpdateInternal(SmartHardwareUpdate):
    update_user: int | None
    updated_at: datetime


class SmartHardwareDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
