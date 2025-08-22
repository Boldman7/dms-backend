from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..permission.resource import ResourceRead

class CompanyBase(BaseModel):
    name: Annotated[str, Field(examples=["company name"])]
    parent_id: int | None = None
    province: str | None = None
    city: str | None = None
    area: str | None = None
    address: str | None = None
    email: str | None = None
    phone_number: str | None = None
    is_end_user: Annotated[int, Field(examples=[0, 1])]

    model_config = ConfigDict(from_attributes=True)


class Company(TimestampSchema, CompanyBase, UUIDSchema, PersistentDeletion):
    pass


class CompanyRead(CompanyBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class CompanyReadJoined(CompanyBase):
    id: int
    resources: List[ResourceRead] = Field(default_factory=list)

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class CompanyCreate(CompanyBase):
    resources: List[int] = Field(default_factory=list)


class CompanyCreateInternal(CompanyBase):
    update_user: int | None


class CompanyUpdate(CompanyBase):
    resources: List[int] = Field(default_factory=list)


class CompanyUpdateInternal(CompanyUpdate):
    update_user: int | None
    updated_at: datetime


class CompanyDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime


class CompanyTreeNode(CompanyRead):
    children: List["CompanyTreeNode"] = []


# Update forward references
CompanyTreeNode.model_rebuild()
