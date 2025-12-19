"""Rotating JSON logger configuration."""

import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_record["extra"] = record.extra_data

        return json.dumps(log_record, default=str)


def setup_logging() -> None:
    """Configure application logging with rotating file handlers."""
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    json_formatter = JSONFormatter()

    # Access Logger (API requests)
    access_logger = logging.getLogger("app.access")
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    access_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "access.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    access_handler.setFormatter(json_formatter)
    access_logger.addHandler(access_handler)

    # Error Logger
    error_logger = logging.getLogger("app.error")
    error_logger.setLevel(logging.ERROR)
    error_logger.propagate = False

    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    error_handler.setFormatter(json_formatter)
    error_logger.addHandler(error_handler)

    # Application Logger (general logs)
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, settings.log_level.upper()))

    app_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    app_handler.setFormatter(json_formatter)
    app_logger.addHandler(app_handler)

    # Console handler for development
    if settings.debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(json_formatter)
        app_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the app namespace."""
    return logging.getLogger(f"app.{name}")


def get_access_logger() -> logging.Logger:
    """Get the access logger for API request logging."""
    return logging.getLogger("app.access")


def get_error_logger() -> logging.Logger:
    """Get the error logger for error logging."""
    return logging.getLogger("app.error")
