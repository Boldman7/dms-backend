from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class ResourceBase(BaseModel):
    name: Annotated[str, Field(examples=["resource name"])]
    parent_id: int | None = None

class Resource(TimestampSchema, ResourceBase, UUIDSchema, PersistentDeletion):
    pass


class ResourceRead(ResourceBase):
    id: int

    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class ResourceCreate(ResourceBase):
    pass


class ResourceCreateInternal(ResourceCreate):
    update_user: int | None


class ResourceUpdate(ResourceBase):
    pass


class ResourceUpdateInternal(ResourceUpdate):
    update_user: int | None
    updated_at: datetime


class ResourceDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime


class ResourceTreeNode(ResourceRead):
    children: List["ResourceTreeNode"] = []

# Update forward references
ResourceTreeNode.model_rebuild()
