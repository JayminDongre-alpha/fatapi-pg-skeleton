"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.middleware import LoggingMiddleware
from app.core.router import create_root_router


def create_application() -> FastAPI:
    """
    Application factory for creating the FastAPI app.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A comprehensive FastAPI skeleton project",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Add middleware (order matters - last added is first executed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(create_root_router())

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """Root endpoint returning application info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
        }

    # Health check endpoint (root level for load balancers/k8s)
    @app.get("/health", tags=["health"])
    async def health() -> dict:
        """Root health check endpoint."""
        return {"status": "healthy"}

    return app


# Create application instance
app = create_application()
