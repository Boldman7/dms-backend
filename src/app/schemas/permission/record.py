from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema

class RecordBase(BaseModel):
    type: Annotated[str, Field(examples=["record type"])]
    content: Annotated[str, Field(examples=["record content"])]
    license_id: int

class Record(TimestampSchema, RecordBase, UUIDSchema, PersistentDeletion):
    pass


class RecordRead(RecordBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None



class RecordCreate(RecordBase):
    pass


class RecordCreateInternal(RecordCreate):
    update_user: int | None


class RecordUpdate(RecordBase):
    pass


class RecordUpdateInternal(RecordUpdate):
    update_user: int | None
    updated_at: datetime


class RecordDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime

