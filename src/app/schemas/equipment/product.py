from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ...core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .product_group import ProductGroupRead


class ProductBase(BaseModel):
    name: Annotated[str, Field(examples=["product name"])]
    product_group_id: int | None = None
    daily_capacity: int | None = None
    description: Annotated[str | None, Field(default=None, examples=["product description"])]


class Product(TimestampSchema, ProductBase, UUIDSchema, PersistentDeletion):
    pass


class ProductRead(ProductBase):
    id: int
    product_group: ProductGroupRead | None
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class ProductCreate(ProductBase):
    pass


class ProductCreateInternal(ProductCreate):
    update_user: int | None


class ProductUpdate(ProductBase):
    pass


class ProductUpdateInternal(ProductUpdate):
    update_user: int | None
    updated_at: datetime


class ProductDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
