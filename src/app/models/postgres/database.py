"""Async SQLAlchemy database engine and session management for PostgreSQL."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


class DatabaseSessionManager:
    """
    Manages database connections and sessions.

    Provides async session context manager for use with FastAPI dependencies.
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def init(self, database_url: str) -> None:
        """Initialize the database engine and session factory."""
        settings = get_settings()

        self._engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,  # Enable connection health checks
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Close the database engine and all connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a transactional scope around a series of operations.

        Yields:
            AsyncSession: Database session for executing queries.
        """
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self) -> AsyncEngine | None:
        """Get the database engine."""
        return self._engine


# Global instance for dependency injection
db_manager = DatabaseSessionManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database sessions.

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with db_manager.session() as session:
        yield session
