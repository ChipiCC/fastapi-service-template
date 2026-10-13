"""Application configuration.

Settings are read from environment variables (optionally from a `.env` file).
Nested values can be provided with a double underscore, e.g. `POSTGRES__HOST`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "staging", "production"]


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "FastAPI Service"
    environment: Environment = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    docs_enabled: bool = True

    # --- HTTP server ---
    host: str = "0.0.0.0"  # noqa: S104 - containers bind all interfaces
    port: int = 8000

    # --- Observability ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = True

    # --- Database ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"  # noqa: S105 - local-only placeholder default
    postgres_db: str = "app"
    db_echo: bool = False
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Async SQLAlchemy connection URL (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance (safe to use as a FastAPI dependency)."""
    return Settings()
