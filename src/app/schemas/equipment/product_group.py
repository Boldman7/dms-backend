from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class ProductGroupBase(BaseModel):
    name: Annotated[str, Field(examples=["product_group name"])]
    parent_id: int | None


class ProductGroup(TimestampSchema, ProductGroupBase, UUIDSchema, PersistentDeletion):
    pass


class ProductGroupRead(ProductGroupBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class ProductGroupCreate(ProductGroupBase):
    pass


class ProductGroupCreateInternal(ProductGroupCreate):
    update_user: int | None


class ProductGroupUpdate(ProductGroupBase):
    pass


class ProductGroupUpdateInternal(ProductGroupUpdate):
    update_user: int | None
    updated_at: datetime


class ProductGroupDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime


class ProductGroupTreeNode(BaseModel):
    """ProductGroup with its children in tree structure"""
    id: int
    name: str
    parent_id: int | None

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None
    children: List["ProductGroupTreeNode"] = []

# Update forward references
ProductGroupTreeNode.model_rebuild()
