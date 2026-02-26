"""Tests Phase 5 — Intégrations OAuth + balance — B5-08.

Les appels HTTP vers Strava/Google/Withings sont mockés via httpx.AsyncClient.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token_crypto import decrypt_token, encrypt_token


# ── Helpers mock ───────────────────────────────────────────────────────────────

def _mock_response(data: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


def _strava_token_response() -> dict:
    return {
        "access_token": "strava_access_123",
        "refresh_token": "strava_refresh_456",
        "expires_at": int(datetime.now(tz=timezone.utc).timestamp()) + 21600,
        "scope": "activity:write,activity:read_all",
        "athlete": {"id": 12345, "firstname": "John"},
    }


def _google_token_response() -> dict:
    return {
        "access_token": "gcal_access_789",
        "refresh_token": "gcal_refresh_abc",
        "expires_in": 3600,
        "scope": "https://www.googleapis.com/auth/calendar.events",
    }


def _withings_token_response() -> dict:
    return {
        "status": 0,
        "body": {
            "access_token": "withings_access_xyz",
            "refresh_token": "withings_refresh_uvw",
            "expires_in": 10800,
            "scope": "user.metrics",
        },
    }


class TestTokenCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        """✅ Chiffrement/déchiffrement Fernet."""
        original = "my_super_secret_token_12345"
        encrypted = encrypt_token(original)
        assert encrypted != original
        assert decrypt_token(encrypted) == original

    def test_encrypt_is_not_deterministic(self):
        """✅ Deux chiffrements du même texte → valeurs différentes (IV aléatoire)."""
        t = "same_token"
        assert encrypt_token(t) != encrypt_token(t)


class TestIntegrationStatus:
    async def test_status_empty(self, client: AsyncClient, client_api_key: str):
        """✅ Aucune intégration connectée."""
        resp = await client.get(
            "/integrations/status", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert all(not p["connected"] for p in data)

    async def test_status_unauthenticated(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/integrations/status")
        assert resp.status_code == 401


class TestStravaIntegration:
    async def test_authorize_url(self, client: AsyncClient, client_api_key: str):
        """✅ GET /integrations/strava → URL d'autorisation."""
        resp = await client.get(
            "/integrations/strava", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "authorize_url" in data
        assert "strava.com/oauth/authorize" in data["authorize_url"]
        assert data["provider"] == "strava"

    async def test_callback_stores_token(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Callback Strava stocke le token chiffré."""
        mock_resp = _mock_response(_strava_token_response())

        with patch("app.services.strava_service.httpx.AsyncClient") as mock_client_cls:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.aclose = AsyncMock()
            mock_client_cls.return_value = instance

            resp = await client.get(
                "/integrations/strava/callback?code=test_code&state=",
                headers={"X-API-Key": client_api_key},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "connected"
        assert data["provider"] == "strava"

        # Vérifier stockage chiffré
        from app.repositories import integration_repository as repo
        from sqlalchemy import select
        from app.models.user import User
        user = (await db.execute(
            select(User).where(User.role == "client")
        )).scalar_one()
        token = await repo.get_token(db, user.id, "strava")
        assert token is not None
        assert decrypt_token(token.access_token_enc) == "strava_access_123"
        assert decrypt_token(token.refresh_token_enc) == "strava_refresh_456"

    async def test_push_strava_no_connection(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """❌ Push sans connexion Strava → 422."""
        # Créer une séance
        from app.models.performance_session import PerformanceSession
        from app.models.user import User
        from sqlalchemy import select
        user = (await db.execute(
            select(User).where(User.role == "client")
        )).scalar_one()
        session = PerformanceSession(
            id=uuid.uuid4(),
            user_id=user.id,
            session_date=datetime.now(tz=timezone.utc),
            session_type="solo",
        )
        db.add(session)
        await db.commit()

        resp = await client.post(
            f"/integrations/strava/push/{session.id}",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 422
        assert "non connecté" in resp.json()["detail"]

    async def test_push_strava_with_mock(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Push activité Strava (token valide + mock HTTP)."""
        # Stocker un token valide
        from app.repositories import integration_repository as repo
        from app.models.user import User
        from app.models.performance_session import PerformanceSession
        from sqlalchemy import select

        user = (await db.execute(select(User).where(User.role == "client"))).scalar_one()
        await repo.upsert_token(
            db, user_id=user.id, provider="strava",
            access_token_enc=encrypt_token("valid_access"),
            refresh_token_enc=None,
            expires_at=None, scope="activity:write",
        )
        session = PerformanceSession(
            id=uuid.uuid4(), user_id=user.id,
            session_date=datetime.now(tz=timezone.utc), session_type="solo",
        )
        db.add(session)
        await db.commit()

        strava_resp = _mock_response(
            {"id": 9999, "name": "Séance MyCoach", "type": "WeightTraining",
             "start_date_local": "2026-02-26T10:00:00"}
        )
        with patch("app.services.strava_service.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=strava_resp)
            instance.aclose = AsyncMock()
            mock_cls.return_value = instance

            resp = await client.post(
                f"/integrations/strava/push/{session.id}",
                headers={"X-API-Key": client_api_key},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pushed"
        assert data["id"] == 9999

    async def test_push_strava_session_not_found(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Push session inexistante → 404."""
        resp = await client.post(
            f"/integrations/strava/push/{uuid.uuid4()}",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 404


class TestGoogleCalendarIntegration:
    async def test_authorize_url(self, client: AsyncClient, client_api_key: str):
        """✅ GET /integrations/calendar → URL d'autorisation Google."""
        resp = await client.get(
            "/integrations/calendar", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "accounts.google.com" in data["authorize_url"]
        assert data["provider"] == "google_calendar"

    async def test_callback_stores_token(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Callback Google Calendar stocke le token chiffré."""
        mock_resp = _mock_response(_google_token_response())

        with patch("app.services.calendar_service.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.aclose = AsyncMock()
            mock_cls.return_value = instance

            resp = await client.get(
                "/integrations/calendar/callback?code=gcal_code&state=",
                headers={"X-API-Key": client_api_key},
            )

        assert resp.status_code == 200
        assert resp.json()["provider"] == "google_calendar"

        from app.repositories import integration_repository as repo
        from app.models.user import User
        from sqlalchemy import select
        user = (await db.execute(select(User).where(User.role == "client"))).scalar_one()
        token = await repo.get_token(db, user.id, "google_calendar")
        assert token is not None
        assert decrypt_token(token.access_token_enc) == "gcal_access_789"


class TestWithingsIntegration:
    async def test_authorize_url(self, client: AsyncClient, client_api_key: str):
        """✅ GET /integrations/scale → URL Withings."""
        resp = await client.get(
            "/integrations/scale", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "withings.com" in data["authorize_url"]
        assert data["provider"] == "withings"

    async def test_callback_stores_token(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Callback Withings stocke le token chiffré."""
        mock_resp = _mock_response(_withings_token_response())

        with patch("app.services.scale_service.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.aclose = AsyncMock()
            mock_cls.return_value = instance

            resp = await client.get(
                "/integrations/scale/callback?code=withings_code&state=",
                headers={"X-API-Key": client_api_key},
            )

        assert resp.status_code == 200
        assert resp.json()["provider"] == "withings"

    async def test_manual_entry_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Saisie manuelle mesure balance."""
        resp = await client.post(
            "/integrations/scale/manual",
            json={
                "measured_at": "2026-02-26T08:00:00Z",
                "weight_kg": "78.5",
                "fat_pct": "18.2",
                "muscle_pct": "42.1",
                "bmi": "24.3",
            },
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["source"] == "manual"
        assert float(data["weight_kg"]) == pytest.approx(78.5, abs=0.01)

    async def test_manual_entry_invalid_weight(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Poids négatif → 422."""
        resp = await client.post(
            "/integrations/scale/manual",
            json={"measured_at": "2026-02-26T08:00:00Z", "weight_kg": "-10"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 422

    async def test_history_empty(self, client: AsyncClient, client_api_key: str):
        """✅ Historique vide → []."""
        resp = await client.get(
            "/integrations/scale/history", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_history_returns_data(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Historique avec données."""
        # Ajouter 2 mesures
        for w in ["72.0", "73.5"]:
            await client.post(
                "/integrations/scale/manual",
                json={"measured_at": "2026-02-26T08:00:00Z", "weight_kg": w},
                headers={"X-API-Key": client_api_key},
            )
        resp = await client.get(
            "/integrations/scale/history", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_import_scale_no_connection(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Import sans connexion Withings → 422."""
        resp = await client.get(
            "/integrations/scale/import", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 422

    async def test_import_scale_with_mock(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Import mesures Withings (mock HTTP)."""
        from app.repositories import integration_repository as repo
        from app.models.user import User
        from sqlalchemy import select

        user = (await db.execute(select(User).where(User.role == "client"))).scalar_one()
        await repo.upsert_token(
            db, user_id=user.id, provider="withings",
            access_token_enc=encrypt_token("valid_withings_token"),
            refresh_token_enc=None, expires_at=None, scope="user.metrics",
        )
        await db.commit()

        withings_data = {
            "status": 0,
            "body": {
                "measuregrps": [
                    {
                        "date": int(datetime(2026, 2, 26, 8, 0, tzinfo=timezone.utc).timestamp()),
                        "measures": [
                            {"type": 1, "value": 785, "unit": -1},   # 78.5 kg
                            {"type": 6, "value": 182, "unit": -1},   # 18.2 %
                        ],
                    }
                ]
            },
        }
        mock_resp = _mock_response(withings_data)

        with patch("app.services.scale_service.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.post = AsyncMock(return_value=mock_resp)
            instance.aclose = AsyncMock()
            mock_cls.return_value = instance

            resp = await client.get(
                "/integrations/scale/import",
                headers={"X-API-Key": client_api_key},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["source"] == "withings"
        assert float(data[0]["weight_kg"]) == pytest.approx(78.5, abs=0.01)


class TestDisconnect:
    async def test_disconnect_ok(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Déconnecter une intégration."""
        from app.repositories import integration_repository as repo
        from app.models.user import User
        from sqlalchemy import select

        user = (await db.execute(select(User).where(User.role == "client"))).scalar_one()
        await repo.upsert_token(
            db, user_id=user.id, provider="strava",
            access_token_enc=encrypt_token("tok"),
            refresh_token_enc=None, expires_at=None, scope=None,
        )
        await db.commit()

        resp = await client.delete(
            "/integrations/disconnect/strava",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200

        # Vérifier déconnecté
        status = await client.get(
            "/integrations/status", headers={"X-API-Key": client_api_key}
        )
        strava = next(p for p in status.json() if p["provider"] == "strava")
        assert not strava["connected"]

    async def test_disconnect_not_found(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Déconnecter une intégration non connectée → 404."""
        resp = await client.delete(
            "/integrations/disconnect/strava",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 404
