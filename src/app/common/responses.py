"""Standard response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: str = "Operation completed successfully"
    data: Any = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    detail: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str | None = None
    environment: str | None = None
