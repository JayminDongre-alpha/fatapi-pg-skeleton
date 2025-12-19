"""Health check endpoints."""

from fastapi import APIRouter
from sqlalchemy import text

from app.common.dependencies import DBSession
from app.common.responses import HealthResponse
from app.core.config import get_settings

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/db")
async def db_health_check(db: DBSession) -> dict:
    """Database health check endpoint."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


@router.get("/ready")
async def readiness_check(db: DBSession) -> dict:
    """
    Readiness check endpoint.

    Verifies that all dependencies are ready to serve traffic.
    """
    checks = {"database": False}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    # Add more dependency checks here (Redis, external APIs, etc.)

    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }
