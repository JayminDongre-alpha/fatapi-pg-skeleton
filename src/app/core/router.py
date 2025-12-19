"""Root router mapper."""

from fastapi import APIRouter

from app.api.v1.router import router as v1_router


def create_root_router() -> APIRouter:
    """
    Create and configure the root API router.

    Includes all versioned API routers with their prefixes.
    """
    root_router = APIRouter()

    # Include versioned API routers
    root_router.include_router(v1_router, prefix="/api/v1", tags=["v1"])

    # Add future API versions here:
    # root_router.include_router(v2_router, prefix="/api/v2", tags=["v2"])

    return root_router
