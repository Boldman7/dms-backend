from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .plc_type import PlcTypeRead
from .smart_hardware import SmartHardwareReadJoined


class ConnectionBase(BaseModel):
    name: Annotated[str, Field(examples=["template connection name"])]
    plc_type_id: int
    smart_hardware_id: int | None = None
    template_connection_id: int | None = None
    ip_address: str | None = None
    port: int | None = None
    station_number: str | None = None

class Connection(TimestampSchema, ConnectionBase, UUIDSchema, PersistentDeletion):
    pass


class ConnectionRead(ConnectionBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class ConnectionReadJoined(ConnectionRead):
    plc_type: PlcTypeRead
    smart_hardware: SmartHardwareReadJoined


class ConnectionCreate(ConnectionBase):
    smart_hardware_id: int
    template_connection_id: int


class ConnectionCreateInternal(ConnectionCreate):
    update_user: int | None


class ConnectionUpdate(BaseModel):
    ip_address: str


class ConnectionUpdateInternal(ConnectionUpdate):
    update_user: int | None
    updated_at: datetime


class ConnectionDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
