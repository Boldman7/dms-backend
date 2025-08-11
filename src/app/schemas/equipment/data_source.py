from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class DataSourceBase(BaseModel):
    name: Annotated[str, Field(examples=["data source name"])]
    template_id: int | None
    is_main: int


class DataSource(TimestampSchema, DataSourceBase, UUIDSchema, PersistentDeletion):
    pass


class DataSourceRead(DataSourceBase):
    id: int
    
    update_user: int | None
    created_at: datetime
    updated_at: datetime | None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceCreateInternal(DataSourceCreate):
    update_user: int | None


class DataSourceUpdate(DataSourceBase):
    pass


class DataSourceUpdateInternal(DataSourceUpdate):
    update_user: int | None
    updated_at: datetime


class DataSourceDelete(BaseModel):
    is_deleted: bool
    deleted_at: datetime
