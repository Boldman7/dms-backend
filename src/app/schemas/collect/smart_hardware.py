from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..base.company import CompanyRead
# from .template import TemplateRead


class SmartHardwareBase(BaseModel):
    name: Annotated[str, Field(examples=["smart hardware name"])]
    company_id: int
    location_way: bool


class SmartHardware(TimestampSchema, SmartHardwareBase, UUIDSchema, PersistentDeletion):
    pass


class SmartHardwareRead(SmartHardwareBase):
    id: int
    code: Annotated[str, Field(examples=["smart hardware code"])]
    template_id: int | None
    sync_status: int | None

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class SmartHardwareReadJoined(SmartHardwareRead):
    # template: TemplateRead | None
    company: CompanyRead


class SmartHardwareCreate(SmartHardwareBase):
    code: Annotated[str, Field(examples=["smart hardware code"])]
    status: int = 2
    upgrade_status: int = 0


class SmartHardwareCreateInternal(SmartHardwareCreate):
    update_user: int | None


class SmartHardwareUpdate(SmartHardwareBase):
    pass


class SmartHardwareUpdateInternal(SmartHardwareUpdate):
    update_user: int | None
    updated_at: datetime

class SmartHardwareSelectTemplate(BaseModel):
    template_id: int

class SmartHardwareDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
