"""Shared pytest fixtures.

Tests run against a **real PostgreSQL database** — there is no SQLite path.
The schema is built by applying the Alembic migrations (in a subprocess), so
the suite exercises the migrations too.

Connection target: the ``TEST_DATABASE_URL`` environment variable, defaulting
to ``postgresql+asyncpg://postgres:postgres@localhost:5432/app_test``.

Start a database first::

    mise run db:up            # Postgres via Docker Compose
    docker compose up -d db   # or directly
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app import app
from db.session import get_session

_ROOT = Path(__file__).resolve().parent.parent

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/app_test",
)


def _alembic(*args: str) -> None:
    subprocess.run(
        ["alembic", "-x", f"db_url={TEST_DATABASE_URL}", *args],
        cwd=_ROOT,
        check=True,
    )


@pytest.fixture(scope="session")
def database_url() -> str:
    """A migrated, empty test database (schema built from the migrations)."""
    _alembic("downgrade", "base")
    _alembic("upgrade", "head")
    return TEST_DATABASE_URL


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    """A PostgreSQL engine bound to the test database."""
    test_engine = create_async_engine(database_url, poolclass=NullPool)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """A database session on a clean ``items`` table."""
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE items"))
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as test_session:
        yield test_session


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """An HTTP client wired to the app with the DB session overridden."""

    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
