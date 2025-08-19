from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .product import ProductRead
from ..base.company import CompanyRead


class DeviceBase(BaseModel):
    name: Annotated[str, Field(examples=["device name"])]
    sn: Annotated[str, Field(examples=["device sn"])]
    company_id: int
    product_id: int
    activate_date: datetime | None = None


class Device(TimestampSchema, DeviceBase, UUIDSchema, PersistentDeletion):
    pass


class DeviceRead(DeviceBase):
    id: int
    company: CompanyRead
    product: ProductRead
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class DeviceCreate(DeviceBase):
    pass


class DeviceCreateInternal(DeviceCreate):
    update_user: int | None


class DeviceUpdate(DeviceBase):
    pass


class DeviceUpdateInternal(DeviceUpdate):
    update_user: int | None
    updated_at: datetime


class DeviceDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
