from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class CompanyBase(BaseModel):
    name: Annotated[str, Field(examples=["company name"])]
    parent_id: int | None
    province: str | None
    city: str | None
    area: str | None
    address: str | None
    email: str | None
    officePhone: str | None
    isEndUser: int

class Company(TimestampSchema, CompanyBase, UUIDSchema, PersistentDeletion):
    pass


class CompanyRead(CompanyBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class CompanyCreate(CompanyBase):
    pass


class CompanyCreateInternal(CompanyCreate):
    update_user: int | None


class CompanyUpdate(CompanyBase):
    pass


class CompanyUpdateInternal(CompanyUpdate):
    update_user: int | None
    updated_at: datetime


class CompanyDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime


class CompanyTreeNode(BaseModel):
    """Company with its children in tree structure"""
    id: int
    name: str
    parent_id: int | None
    province: str | None
    city: str | None
    area: str | None
    address: str | None
    email: str | None
    officePhone: str | None
    isEndUser: int
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None
    children: List["CompanyTreeNode"] = []

# Update forward references
CompanyTreeNode.model_rebuild()
