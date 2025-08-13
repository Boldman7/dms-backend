from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class ConnectionBase(BaseModel):
    name: Annotated[str, Field(examples=["connection name"])]
    template_id: int
    plc_type_id: int
    ip_address: str | None = None
    port: int | None = None
    station_number: int | None = None

class Connection(TimestampSchema, ConnectionBase, UUIDSchema, PersistentDeletion):
    pass


class ConnectionRead(ConnectionBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionCreateInternal(ConnectionCreate):
    update_user: int | None


class ConnectionUpdate(ConnectionBase):
    pass


class ConnectionUpdateInternal(ConnectionUpdate):
    update_user: int | None
    updated_at: datetime


class ConnectionDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
