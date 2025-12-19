"""User Pydantic schemas."""

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, IDTimestampSchema


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase, IDTimestampSchema):
    """Schema for user response."""

    is_active: bool
    is_superuser: bool


class UserListResponse(BaseSchema):
    """Schema for list of users."""

    items: list[UserResponse]
    total: int
