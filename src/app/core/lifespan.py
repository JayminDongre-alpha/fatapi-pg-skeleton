"""Application lifespan event handlers."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.models.postgres.database import db_manager

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Startup: Initialize logging, database connections, etc.
    - Shutdown: Clean up resources, close connections, etc.
    """
    settings = get_settings()

    # ============ STARTUP ============
    # Setup logging first
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    await db_manager.init(settings.database_url)
    app.state.db_manager = db_manager
    logger.info("Database connection pool initialized")

    # Add any other startup tasks here:
    # - Cache initialization (Redis)
    # - Message queue connections
    # - External service health checks

    logger.info(f"Application startup complete - Environment: {settings.environment}")

    yield  # Application runs here

    # ============ SHUTDOWN ============
    logger.info("Shutting down application...")

    # Close database connections
    await db_manager.close()
    logger.info("Database connections closed")

    # Add any other shutdown tasks here:
    # - Close cache connections
    # - Flush logs
    # - Graceful service shutdown

    logger.info("Application shutdown complete")
