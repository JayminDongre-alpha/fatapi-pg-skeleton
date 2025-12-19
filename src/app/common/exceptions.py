"""Custom HTTP exceptions."""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, detail: str = "Not enough permissions") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictException(AppException):
    """Conflict exception for duplicate resources."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(AppException):
    """Validation error exception."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InternalServerException(AppException):
    """Internal server error exception."""

    def __init__(self, detail: str = "Internal server error") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
