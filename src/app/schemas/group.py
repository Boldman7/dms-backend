from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class GroupBase(BaseModel):
    name: Annotated[str, Field(examples=["group name"])]
    is_control: Annotated[int, Field(default=0, examples=[0, 1])]


class Group(TimestampSchema, GroupBase, UUIDSchema, PersistentDeletion):
    pass

class GroupRead(GroupBase):
    id: int
    protocol_id: Annotated[str | None, Field(examples=["protocol id"])]
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class GroupCreate(GroupBase):
    pass


class GroupCreateInternal(GroupCreate):
    update_user: int | None


class GroupUpdate(GroupBase):
    pass


class GroupUpdateInternal(GroupUpdate):
    update_user: int | None
    updated_at: datetime


class GroupDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
