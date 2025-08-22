from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from .permission.role import RoleRead


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    company_id: int
    phone_number: str | None = None
    office_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


class User(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    hashed_password: str
    is_superuser: bool = False


class UserRead(UserBase):
    id: int
    roles: List[RoleRead] = Field(default_factory=list)


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    roles: List[int] = Field(default_factory=list)

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    update_user: int | None
    hashed_password: str


class UserUpdate(UserBase):
    model_config = ConfigDict(extra="forbid")
    roles: List[int] = Field(default_factory=list)


class UserUpdateInternal(UserBase):
    update_user: int | None
    updated_at: datetime


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


