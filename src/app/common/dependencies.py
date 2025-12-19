"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres.database import get_db


# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_request_id(request: Request) -> str:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", "unknown")


RequestID = Annotated[str, Depends(get_request_id)]


class Pagination:
    """Pagination parameters dependency."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.limit = page_size


PaginationParams = Annotated[Pagination, Depends()]


class SortParams:
    """Sorting parameters dependency."""

    def __init__(
        self,
        sort_by: str = Query(default="id", description="Field to sort by"),
        sort_order: str = Query(
            default="asc", pattern="^(asc|desc)$", description="Sort order (asc/desc)"
        ),
    ) -> None:
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.is_descending = sort_order == "desc"


SortingParams = Annotated[SortParams, Depends()]
