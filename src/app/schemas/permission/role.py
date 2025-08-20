from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..base.company import CompanyRead

class RoleBase(BaseModel):
    name: Annotated[str, Field(examples=["role name"])]
    company_id: int
    description: str | None = None

class Role(TimestampSchema, RoleBase, UUIDSchema, PersistentDeletion):
    pass


class RoleRead(RoleBase):
    id: int
    public_type: Annotated[int, Field(examples=[1, 2])]

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class RoleReadJoined(RoleRead):
    company: CompanyRead


class RoleCreate(RoleBase):
    public_type: Annotated[int, Field(examples=[1, 2])]


class RoleCreateInternal(RoleCreate):
    update_user: int | None


class RoleUpdate(RoleBase):
    pass


class RoleUpdateInternal(RoleUpdate):
    update_user: int | None
    updated_at: datetime


class RoleDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime

