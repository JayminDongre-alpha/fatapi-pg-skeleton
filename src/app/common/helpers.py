"""Common utility functions."""

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(value: str) -> str:
    """Create SHA256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length."""
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)] + suffix


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case."""
    result = []
    for char in camel_str:
        if char.isupper():
            result.append("_")
            result.append(char.lower())
        else:
            result.append(char)
    return "".join(result).lstrip("_")
