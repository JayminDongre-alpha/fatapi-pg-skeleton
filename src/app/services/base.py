"""Base service class."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base service with database session dependency."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize service with database session.

        Args:
            db: Async database session
        """
        self.db = db
