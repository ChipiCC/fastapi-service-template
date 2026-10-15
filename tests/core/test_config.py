"""Tests for application configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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


def test_database_url_encodes_credentials() -> None:
    settings = Settings(
        postgres_user="user",
        postgres_password="p@ss:w/rd",
        postgres_host="h",
        postgres_port=5432,
        postgres_db="d",
    )
    assert settings.database_url == "postgresql+asyncpg://user:p%40ss%3Aw%2Frd@h:5432/d"


def test_database_url_override_wins_and_upgrades_driver() -> None:
    settings = Settings(database_url_override="postgresql://u:p@h/d")
    assert settings.database_url == "postgresql+asyncpg://u:p@h/d"


def test_ssl_mode_is_appended() -> None:
    settings = Settings(postgres_ssl="require")
    assert settings.database_url.endswith("?ssl=require")


def test_is_production_flag() -> None:
    production = Settings(
        environment="production",
        debug=False,
        docs_enabled=False,
        postgres_password="not-the-default",
        api_keys=["prod-key"],
        allowed_hosts=["api.example.com"],
    )
    assert production.is_production is True
    assert Settings(environment="local").is_production is False


def test_production_rejects_insecure_defaults() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production")


def test_list_settings_accept_csv() -> None:
    settings = Settings(api_keys="a, b ,c", cors_origins="http://x,http://y")
    assert settings.api_keys == ["a", "b", "c"]
    assert settings.cors_origins == ["http://x", "http://y"]


def test_list_settings_accept_json() -> None:
    settings = Settings(allowed_hosts='["a.example", "b.example"]')
    assert settings.allowed_hosts == ["a.example", "b.example"]
