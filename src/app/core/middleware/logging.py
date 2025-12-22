"""Request/Response logging middleware."""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import get_access_logger, get_error_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses in JSON format."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.access_logger = get_access_logger()
        self.error_logger = get_error_logger()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log access/errors."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Record start time
        start_time = time.perf_counter()

        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log access
            self.access_logger.info(
                "Request completed",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "client_ip": client_ip,
                        "method": method,
                        "url": url,
                        "path": path,
                        "user_agent": user_agent,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                    }
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            self.error_logger.error(
                f"Request failed: {exc!s}",
                exc_info=True,
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "client_ip": client_ip,
                        "method": method,
                        "url": url,
                        "path": path,
                        "user_agent": user_agent,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(exc),
                    }
                },
            )
            raise
