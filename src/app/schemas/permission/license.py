from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..base.company import CompanyRead

class LicenseBase(BaseModel):
    name: Annotated[str, Field(examples=["license name"])]
    phone_number: str | None = None
    auth_code: str | None = None
    company_id: int
    valid_period: datetime | None = None

class License(TimestampSchema, LicenseBase, UUIDSchema, PersistentDeletion):
    pass


class LicenseRead(LicenseBase):
    id: int
    auth_type: Annotated[int, Field(examples=[1, 2])]

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class LicenseReadJoined(LicenseRead):
    company: CompanyRead


class LicenseCreate(LicenseBase):
    auth_type: Annotated[int, Field(examples=[1, 2])]


class LicenseCreateInternal(LicenseCreate):
    update_user: int | None


class LicenseUpdate(LicenseBase):
    pass


class LicenseUpdateInternal(LicenseUpdate):
    update_user: int | None
    updated_at: datetime


class LicenseDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime

