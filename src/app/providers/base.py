"""Base provider class for third-party integrations."""

import logging
from abc import ABC, abstractmethod

from app.core.config import Settings


class BaseProvider(ABC):
    """Abstract base class for all third-party providers.

    Providers handle external service integrations (email, payment, storage, etc.).
    They encapsulate configuration, connection management, and error handling.

    Usage in services:
        class UserService(BaseService):
            def __init__(self, db: AsyncSession, email_provider: EmailProvider):
                super().__init__(db)
                self.email = email_provider

            async def create(self, data: UserCreate) -> User:
                user = await self._create_user(data)
                await self.email.send_email(
                    to=user.email,
                    subject="Welcome!",
                    body="Thanks for signing up."
                )
                return user
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize provider with application settings.

        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.logger = logging.getLogger(f"app.providers.{self.__class__.__name__}")

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider service is healthy.

        Returns:
            True if service is reachable and operational
        """
        pass
