from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ...schemas.collect.group import GroupRead


class VariableBase(BaseModel):
    name: Annotated[str, Field(examples=["variable name"])]
    data_type: Annotated[int, Field(examples=[1, 2, 3, 4, 5, 6])]
    address: Annotated[str, Field(examples=["variable address"])]
    transmission_mode: Annotated[int, Field(examples=[1, 2])]
    rw_mode: Annotated[int, Field(examples=[1, 2])]
    unit: Annotated[str | None, Field(examples=["variable unit"])]
    description: Annotated[str | None, Field(examples=["variable description"])]
    group_id: int
    connection_id: Annotated[int, Field(examples=[1])]


class Variable(TimestampSchema, VariableBase, UUIDSchema, PersistentDeletion):
    pass


class VariableRead(VariableBase):
    id: int
    group: GroupRead
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class VariableCreate(VariableBase):
    pass


class VariableCreateInternal(VariableCreate):
    update_user: int | None


class VariableUpdate(VariableBase):
    pass


class VariableUpdateInternal(VariableUpdate):
    update_user: int | None
    updated_at: datetime


class VariableDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
