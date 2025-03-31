from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ..models.user import UserRole
from .common import ObjectListAdminFilters, ObjectListRequest


class GetUsersListAdminRequest(ObjectListAdminFilters, ObjectListRequest):
    pass


class UserBase(BaseModel):
    email: EmailStr | None = Field(None, example="user@example.com", max_length=255)
    login: str = Field(..., min_length=3, max_length=50, example="john_doe")
    name: str | None = Field(None, max_length=100, example="John Doe")


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, example="user@example.com", max_length=255)
    name: str | None = Field(None, example="New Name")
    login: str | None = Field(None, example="new_login")


class UserResponse(UserBase):
    id: UUID
    email: str
    login: str
    name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserAdminResponse(UserResponse):
    yandex_id: str
    deleted_at: datetime | None


class UsersListAdminResponse(BaseModel):
    objects: list[UserAdminResponse]
    count: int


class UserUpdateAdminRequest(UserUpdate):
    is_active: bool | None = Field(default=None)
