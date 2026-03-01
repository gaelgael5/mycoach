"""Tests for conversations & messaging endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_conversations_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_client_creates_conversation(client: AsyncClient, auth_headers: dict):
    # Create a client
    resp = await client.post("/api/v1/clients", json={
        "first_name": "Alice",
        "last_name": "Smith",
    }, headers=auth_headers)
    assert resp.status_code == 201
    client_id = resp.json()["id"]

    # Should have 1 conversation now
    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    assert resp.status_code == 200
    convs = resp.json()
    assert len(convs) == 1
    assert convs[0]["client_id"] == client_id


@pytest.mark.asyncio
async def test_send_message_and_list(client: AsyncClient, auth_headers: dict):
    # Create client -> conversation
    resp = await client.post("/api/v1/clients", json={
        "first_name": "Bob",
        "last_name": "Jones",
    }, headers=auth_headers)
    client_id = resp.json()["id"]

    # Get conversation
    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    conv_id = resp.json()[0]["id"]

    # Send message
    resp = await client.post(f"/api/v1/conversations/{conv_id}/messages", json={
        "content": "Hello Bob!",
    }, headers=auth_headers)
    assert resp.status_code == 201
    msg = resp.json()
    assert msg["content"] == "Hello Bob!"
    assert msg["sender_type"] == "coach"

    # List messages
    resp = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_mark_as_read(client: AsyncClient, auth_headers: dict):
    # Create client -> conversation
    resp = await client.post("/api/v1/clients", json={
        "first_name": "Carol",
        "last_name": "White",
    }, headers=auth_headers)

    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    conv_id = resp.json()[0]["id"]

    # Mark as read (should succeed even if no messages)
    resp = await client.patch(f"/api/v1/conversations/{conv_id}/read", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_conversation_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/v1/conversations/{fake_id}/messages", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/clients", json={
        "first_name": "Dan",
        "last_name": "Brown",
    }, headers=auth_headers)

    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    conv_id = resp.json()[0]["id"]

    # Send 5 messages
    for i in range(5):
        await client.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": f"Message {i}",
        }, headers=auth_headers)

    # Paginate
    resp = await client.get(f"/api/v1/conversations/{conv_id}/messages?limit=2&offset=0", headers=auth_headers)
    data = resp.json()
    assert data["total_count"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_last_message_in_conversation_list(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/clients", json={
        "first_name": "Eve",
        "last_name": "Green",
    }, headers=auth_headers)

    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    conv_id = resp.json()[0]["id"]

    await client.post(f"/api/v1/conversations/{conv_id}/messages", json={
        "content": "Last msg",
    }, headers=auth_headers)

    resp = await client.get("/api/v1/conversations", headers=auth_headers)
    conv = resp.json()[0]
    assert conv["last_message"] is not None
    assert conv["last_message"]["content"] == "Last msg"
