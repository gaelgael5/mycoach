"""Tests for coach profile endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/coach/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "coach@test.com"
    assert data["first_name"] == "Test"


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, auth_headers: dict):
    resp = await client.patch("/api/v1/coach/me", json={
        "bio": "I am a fitness coach",
        "phone": "+33612345678",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["bio"] == "I am a fitness coach"


@pytest.mark.asyncio
async def test_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/coach/me")
    assert resp.status_code == 401  # No auth header
