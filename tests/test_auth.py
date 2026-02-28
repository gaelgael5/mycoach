"""Tests for auth endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@coach.com",
        "password": "Test1234!",
        "first_name": "New",
        "last_name": "Coach",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    payload = {
        "email": "dup@coach.com",
        "password": "Test1234!",
        "first_name": "Dup",
        "last_name": "Coach",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@coach.com",
        "password": "Test1234!",
        "first_name": "Login",
        "last_name": "Coach",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@coach.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_bad_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "bad@coach.com",
        "password": "Test1234!",
        "first_name": "Bad",
        "last_name": "Coach",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "bad@coach.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "refresh@coach.com",
        "password": "Test1234!",
        "first_name": "Ref",
        "last_name": "Coach",
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
