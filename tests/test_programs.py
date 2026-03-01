"""Tests for Programs, Sessions, Exercises, and Tracking endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def program_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/v1/programs", json={
        "name": "PPL Program",
        "description": "Push Pull Legs",
        "duration_weeks": 8,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest_asyncio.fixture
async def session_id(client: AsyncClient, auth_headers: dict, program_id: str) -> str:
    resp = await client.post(f"/api/v1/programs/{program_id}/sessions", json={
        "day_number": 1,
        "name": "Push Day",
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest_asyncio.fixture
async def exercise_id(client: AsyncClient, auth_headers: dict, session_id: str) -> str:
    resp = await client.post(f"/api/v1/sessions/{session_id}/exercises", json={
        "name": "Bench Press",
        "sets": 4,
        "reps": "8-10",
        "weight": 80.0,
        "rest_seconds": 120,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest_asyncio.fixture
async def client_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/v1/clients", json={
        "first_name": "John",
        "last_name": "Doe",
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["id"]


# --- Program CRUD ---

class TestPrograms:
    @pytest.mark.asyncio
    async def test_create_program(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/programs", json={
            "name": "Strength",
            "duration_weeks": 12,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Strength"
        assert resp.json()["duration_weeks"] == 12

    @pytest.mark.asyncio
    async def test_list_programs(self, client: AsyncClient, auth_headers: dict, program_id: str):
        resp = await client.get("/api/v1/programs", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_program_detail(self, client: AsyncClient, auth_headers: dict, program_id: str):
        resp = await client.get(f"/api/v1/programs/{program_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == program_id
        assert "sessions" in resp.json()

    @pytest.mark.asyncio
    async def test_update_program(self, client: AsyncClient, auth_headers: dict, program_id: str):
        resp = await client.patch(f"/api/v1/programs/{program_id}", json={
            "name": "Updated PPL",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated PPL"

    @pytest.mark.asyncio
    async def test_delete_program(self, client: AsyncClient, auth_headers: dict, program_id: str):
        resp = await client.delete(f"/api/v1/programs/{program_id}", headers=auth_headers)
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_duplicate_program(self, client: AsyncClient, auth_headers: dict, program_id: str, session_id: str, exercise_id: str):
        resp = await client.post(f"/api/v1/programs/{program_id}/duplicate", headers=auth_headers)
        assert resp.status_code == 201
        assert "(copy)" in resp.json()["name"]
        # Verify the duplicate has sessions
        detail = await client.get(f"/api/v1/programs/{resp.json()['id']}", headers=auth_headers)
        assert len(detail.json()["sessions"]) == 1
        assert len(detail.json()["sessions"][0]["exercises"]) == 1

    @pytest.mark.asyncio
    async def test_assign_program(self, client: AsyncClient, auth_headers: dict, program_id: str, client_id: str):
        resp = await client.post(f"/api/v1/programs/{program_id}/assign", json={
            "client_ids": [client_id],
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/programs/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert resp.status_code == 404


# --- Sessions ---

class TestSessions:
    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient, auth_headers: dict, program_id: str):
        resp = await client.post(f"/api/v1/programs/{program_id}/sessions", json={
            "day_number": 2,
            "name": "Pull Day",
        }, headers=auth_headers)
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_update_session(self, client: AsyncClient, auth_headers: dict, session_id: str):
        resp = await client.patch(f"/api/v1/sessions/{session_id}", json={
            "name": "Heavy Push",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Heavy Push"

    @pytest.mark.asyncio
    async def test_delete_session(self, client: AsyncClient, auth_headers: dict, session_id: str):
        resp = await client.delete(f"/api/v1/sessions/{session_id}", headers=auth_headers)
        assert resp.status_code == 204


# --- Exercises ---

class TestExercises:
    @pytest.mark.asyncio
    async def test_create_exercise(self, client: AsyncClient, auth_headers: dict, session_id: str):
        resp = await client.post(f"/api/v1/sessions/{session_id}/exercises", json={
            "name": "Squat",
            "sets": 5,
            "reps": "5",
            "weight": 100.0,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Squat"

    @pytest.mark.asyncio
    async def test_update_exercise(self, client: AsyncClient, auth_headers: dict, exercise_id: str):
        resp = await client.patch(f"/api/v1/exercises/{exercise_id}", json={
            "weight": 85.0,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["weight"] == 85.0

    @pytest.mark.asyncio
    async def test_delete_exercise(self, client: AsyncClient, auth_headers: dict, exercise_id: str):
        resp = await client.delete(f"/api/v1/exercises/{exercise_id}", headers=auth_headers)
        assert resp.status_code == 204


# --- Tracking ---

class TestTracking:
    @pytest.mark.asyncio
    async def test_create_metric(self, client: AsyncClient, auth_headers: dict, client_id: str):
        resp = await client.post("/api/v1/tracking/metrics", json={
            "client_id": client_id,
            "date": "2026-03-01",
            "metric_type": "weight",
            "value": 82.5,
            "unit": "kg",
        }, headers=auth_headers)
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_get_client_metrics(self, client: AsyncClient, auth_headers: dict, client_id: str):
        # Create a metric first
        await client.post("/api/v1/tracking/metrics", json={
            "client_id": client_id,
            "date": "2026-03-01",
            "metric_type": "weight",
            "value": 82.5,
            "unit": "kg",
        }, headers=auth_headers)
        resp = await client.get(f"/api/v1/tracking/clients/{client_id}/metrics", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_dashboard(self, client: AsyncClient, auth_headers: dict, client_id: str):
        resp = await client.get(f"/api/v1/tracking/clients/{client_id}/dashboard", headers=auth_headers)
        assert resp.status_code == 200
        assert "total_sessions_logged" in resp.json()
        assert "completion_rate" in resp.json()

    @pytest.mark.asyncio
    async def test_log_session(self, client: AsyncClient, auth_headers: dict, session_id: str, client_id: str):
        resp = await client.post(f"/api/v1/tracking/sessions/{session_id}/log", json={
            "client_id": client_id,
            "completed": True,
            "actual_weights": {"Bench Press": 82.5},
            "notes": "Good session",
        }, headers=auth_headers)
        # May be 201 or fail if client loading issue with SQLite - we accept both
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_get_client_logs(self, client: AsyncClient, auth_headers: dict, client_id: str):
        resp = await client.get(f"/api/v1/tracking/clients/{client_id}/logs", headers=auth_headers)
        assert resp.status_code == 200


# --- Auth protection ---

class TestAuthProtection:
    @pytest.mark.asyncio
    async def test_programs_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/programs")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_tracking_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/tracking/clients/00000000-0000-0000-0000-000000000000/metrics")
        assert resp.status_code in (401, 403)
