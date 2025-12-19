"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="FastAPI Skeleton", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://admin:P@ssw0rd123*@localhost:5432/fastapi_skeleton",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="logs", alias="LOG_DIR")
    log_max_bytes: int = Field(default=10485760, alias="LOG_MAX_BYTES")  # 10MB
    log_backup_count: int = Field(default=5, alias="LOG_BACKUP_COUNT")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
