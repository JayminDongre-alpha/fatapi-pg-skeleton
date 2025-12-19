"""Sample User model for PostgreSQL."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base


class User(Base):
    """
    User model for demonstration purposes.

    Attributes:
        email: Unique email address.
        hashed_password: Bcrypt hashed password.
        full_name: User's full name.
        is_active: Whether the user account is active.
        is_superuser: Whether the user has admin privileges.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
