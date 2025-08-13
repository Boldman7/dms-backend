from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .plc_type import PlcTypeRead


class PlcBrandBase(BaseModel):
    name: Annotated[str, Field(examples=["plc brand name"])]


class PlcBrand(TimestampSchema, PlcBrandBase, UUIDSchema, PersistentDeletion):
    pass


class PlcBrandRead(PlcBrandBase):
    id: int
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class PlcBrandCreate(PlcBrandBase):
    pass


class PlcBrandCreateInternal(PlcBrandCreate):
    update_user: int | None


class PlcBrandUpdate(PlcBrandBase):
    pass


class PlcBrandUpdateInternal(PlcBrandUpdate):
    update_user: int | None
    updated_at: datetime


class PlcBrandDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime

class PlcTreeNode(PlcBrandRead):
    """Plc with its children in tree structure"""
    plc_type_list: List["PlcTypeRead"] = []

# Update forward references
PlcTreeNode.model_rebuild()