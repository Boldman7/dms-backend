from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field, ConfigDict

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..base.company import CompanyRead
from .resource import ResourceRead

class RoleBase(BaseModel):
    name: Annotated[str, Field(examples=["role name"])]
    company_id: int
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
    

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
    resources: List[ResourceRead] = Field(default_factory=list)


class RoleCreate(RoleBase):
    public_type: Annotated[int, Field(examples=[1, 2])]
    resources: List[int] = Field(default_factory=list)


class RoleCreateInternal(RoleBase):
    public_type: Annotated[int, Field(examples=[1, 2])]
    update_user: int | None


class RoleUpdate(RoleBase):
    resources: List[int] = Field(default_factory=list)


class RoleUpdateInternal(RoleBase):
    update_user: int | None
    updated_at: datetime


class RoleDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime

