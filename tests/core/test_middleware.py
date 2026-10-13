"""Tests for the request-context middleware."""

from __future__ import annotations

from httpx import AsyncClient


async def test_request_id_header_echoed(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={"x-request-id": "abc-123"})
    assert response.headers["x-request-id"] == "abc-123"


async def test_request_id_generated_when_missing(client: AsyncClient) -> None:
    response = await client.get("/health/live")
    assert response.headers.get("x-request-id")
