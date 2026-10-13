"""Tests for application configuration."""

from __future__ import annotations

from core.config import Settings


def test_database_url_is_asyncpg() -> None:
    settings = Settings(
        postgres_user="u",
        postgres_password="p",
        postgres_host="h",
        postgres_port=1234,
        postgres_db="d",
    )
    assert settings.database_url == "postgresql+asyncpg://u:p@h:1234/d"


def test_is_production_flag() -> None:
    assert Settings(environment="production").is_production is True
    assert Settings(environment="local").is_production is False
