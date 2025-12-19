"""Base Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """Schema with ID field."""

    id: int


class IDTimestampSchema(IDSchema, TimestampSchema):
    """Schema with ID and timestamp fields."""

    pass
