"""Email provider for sending emails via SMTP or third-party services."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import Settings
from app.providers.base import BaseProvider


class EmailProvider(BaseProvider):
    """Provider for sending emails.

    Supports SMTP and can be extended for services like SendGrid, AWS SES, etc.

    Configuration (add to Settings class in config.py):
        SMTP_HOST: str = "localhost"
        SMTP_PORT: int = 587
        SMTP_USER: str = ""
        SMTP_PASSWORD: str = ""
        SMTP_FROM_EMAIL: str = "noreply@example.com"
        SMTP_USE_TLS: bool = True

    Usage in services:
        from app.providers import EmailProvider

        class UserService(BaseService):
            def __init__(self, db: AsyncSession, email: EmailProvider):
                super().__init__(db)
                self.email = email

            async def send_welcome_email(self, user: User) -> bool:
                return await self.email.send_email(
                    to=user.email,
                    subject="Welcome to our platform!",
                    body=f"Hello {user.full_name}, welcome aboard!"
                )
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize email provider.

        Args:
            settings: Application settings with SMTP configuration
        """
        super().__init__(settings)
        self.logger = logging.getLogger("app.providers.EmailProvider")

        # SMTP configuration (extend Settings class with these fields)
        self.host = getattr(settings, "smtp_host", "localhost")
        self.port = getattr(settings, "smtp_port", 587)
        self.user = getattr(settings, "smtp_user", "")
        self.password = getattr(settings, "smtp_password", "")
        self.from_email = getattr(settings, "smtp_from_email", "noreply@example.com")
        self.use_tls = getattr(settings, "smtp_use_tls", True)

    async def health_check(self) -> bool:
        """Check if SMTP server is reachable.

        Returns:
            True if SMTP connection succeeds
        """
        try:
            with smtplib.SMTP(self.host, self.port, timeout=5) as server:
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
            return True
        except Exception as e:
            self.logger.error(f"Email health check failed: {e}")
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """Send an email.

        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content
            html: If True, body is treated as HTML content

        Returns:
            True if email was sent successfully
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to

            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))

            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.sendmail(self.from_email, [to], msg.as_string())

            self.logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to}: {e}")
            return False

    async def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        html: bool = False,
    ) -> dict[str, bool]:
        """Send email to multiple recipients.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject line
            body: Email body content
            html: If True, body is treated as HTML content

        Returns:
            Dictionary mapping email addresses to success status
        """
        results = {}
        for recipient in recipients:
            results[recipient] = await self.send_email(recipient, subject, body, html)
        return results
