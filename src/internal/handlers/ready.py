"""GET /health/ready — readiness probe."""

from __future__ import annotations

from sqlalchemy import text

from core.config import get_settings
from db.session import SessionDep
from internal.models import Readiness

settings = get_settings()


async def readiness(session: SessionDep) -> Readiness:
    """Return OK only if dependencies (database) are reachable."""
    checks: dict[str, str] = {}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:  # pragma: no cover - exercised via failure injection
        checks["database"] = "error"
        return Readiness(status="error", environment=settings.environment, checks=checks)

    return Readiness(status="ok", environment=settings.environment, checks=checks)
