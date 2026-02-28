"""Tests for client endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_client(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/clients", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "hourly_rate": 50.0,
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["first_name"] == "John"
    assert data["hourly_rate"] == 50.0


@pytest.mark.asyncio
async def test_list_clients(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/clients", json={
        "first_name": "A", "last_name": "Client",
    }, headers=auth_headers)
    resp = await client.get("/api/v1/clients", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_client(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/clients", json={
        "first_name": "Get", "last_name": "Me",
    }, headers=auth_headers)
    cid = create.json()["id"]
    resp = await client.get(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Get"


@pytest.mark.asyncio
async def test_update_client(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/clients", json={
        "first_name": "Old", "last_name": "Name",
    }, headers=auth_headers)
    cid = create.json()["id"]
    resp = await client.patch(f"/api/v1/clients/{cid}", json={
        "first_name": "New",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "New"


@pytest.mark.asyncio
async def test_delete_client(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/clients", json={
        "first_name": "Del", "last_name": "Me",
    }, headers=auth_headers)
    cid = create.json()["id"]
    resp = await client.delete(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_invite_and_register(client: AsyncClient, auth_headers: dict):
    # Create client
    create = await client.post("/api/v1/clients", json={
        "first_name": "Invite", "last_name": "Me",
    }, headers=auth_headers)
    cid = create.json()["id"]

    # Invite
    inv = await client.post("/api/v1/clients/invite", json={
        "client_id": cid,
    }, headers=auth_headers)
    assert inv.status_code == 200
    token = inv.json()["invitation_token"]

    # Register via token
    reg = await client.post("/api/v1/clients/register", json={
        "token": token,
        "email": "invited@client.com",
        "password": "ClientP@ss1",
    })
    assert reg.status_code == 200
    assert reg.json()["email"] == "invited@client.com"
    assert reg.json()["registered_at"] is not None


@pytest.mark.asyncio
async def test_freemium_limit(client: AsyncClient, auth_headers: dict):
    """Free plan should block after 15 clients."""
    for i in range(15):
        resp = await client.post("/api/v1/clients", json={
            "first_name": f"Client{i}", "last_name": "Test",
        }, headers=auth_headers)
        assert resp.status_code == 201

    # 16th should fail
    resp = await client.post("/api/v1/clients", json={
        "first_name": "TooMany", "last_name": "Test",
    }, headers=auth_headers)
    assert resp.status_code == 403
    assert "Free plan" in resp.json()["detail"]
