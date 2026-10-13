"""FastAPI application factory and ASGI entrypoint.

Run locally with::

    uv run uvicorn app:app --reload
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import get_settings
from core.exceptions import register_exception_handlers
from core.logging import configure_logging, get_logger
from core.middleware import RequestContextMiddleware
from core.version import __version__
from db.session import dispose_engine
from internal.router import router as internal_router
from items.router import router as items_router

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    configure_logging(log_level=settings.log_level, json_logs=settings.log_json)
    logger.info(
        "app_startup",
        app=settings.app_name,
        version=__version__,
        environment=settings.environment,
    )
    try:
        yield
    finally:
        await dispose_engine()
        logger.info("app_shutdown", app=settings.app_name)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Production-ready FastAPI microservice template.",
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    # internal routes (metadata, probes) live at the root, outside versioning
    app.include_router(internal_router)
    app.include_router(items_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
