"""Tests Phase 6 — RGPD + sécurité — B6-02/03/04/05 + B6-01 (security headers)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSecurityHeaders:
    """B6-01 — Security headers présents sur chaque réponse."""

    async def test_security_headers_present(self, client: AsyncClient, client_api_key: str):
        """✅ Headers de sécurité injectés sur les réponses."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert resp.headers.get("x-xss-protection") == "1; mode=block"
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    async def test_no_server_info_in_errors(self, client: AsyncClient):
        """✅ Les erreurs 404/422 n'exposent pas d'info serveur sensible."""
        resp = await client.get("/endpoint-inexistant-xyzabc")
        assert resp.status_code == 404
        body = resp.json()
        # Pas de stack trace en clair
        assert "traceback" not in str(body).lower()
        assert "exception" not in str(body).lower()


class TestConsentEndpoints:
    """B6-05 — Consentements RGPD."""

    async def test_record_consent_ok(self, client: AsyncClient, client_api_key: str):
        """✅ Enregistrer un consentement."""
        resp = await client.post(
            "/users/me/consents",
            json={"consent_type": "privacy_policy", "version": "1.0", "accepted": True},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["consent_type"] == "privacy_policy"
        assert data["accepted"] is True
        assert data["version"] == "1.0"

    async def test_record_consent_refused(self, client: AsyncClient, client_api_key: str):
        """✅ Refus de consentement enregistré."""
        resp = await client.post(
            "/users/me/consents",
            json={"consent_type": "marketing_emails", "version": "1.0", "accepted": False},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["accepted"] is False

    async def test_record_consent_invalid_type(self, client: AsyncClient, client_api_key: str):
        """❌ Type de consentement inconnu → 422."""
        resp = await client.post(
            "/users/me/consents",
            json={"consent_type": "sell_my_soul", "version": "1.0", "accepted": True},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 422

    async def test_list_consents_empty(self, client: AsyncClient, client_api_key: str):
        """✅ Aucun consentement → []."""
        resp = await client.get("/users/me/consents", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_consents_after_record(self, client: AsyncClient, client_api_key: str):
        """✅ Liste après enregistrement."""
        for consent_type in ["privacy_policy", "terms_of_service"]:
            await client.post(
                "/users/me/consents",
                json={"consent_type": consent_type, "version": "1.0", "accepted": True},
                headers={"X-API-Key": client_api_key},
            )
        resp = await client.get("/users/me/consents", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_consent_log_immutable(self, client: AsyncClient, client_api_key: str):
        """✅ Consentement immuable — enregistrement multiple possible (historique)."""
        # 1er accord
        r1 = await client.post(
            "/users/me/consents",
            json={"consent_type": "analytics", "version": "1.0", "accepted": True},
            headers={"X-API-Key": client_api_key},
        )
        # Retrait du consentement (nouvel enregistrement, pas de modification)
        r2 = await client.post(
            "/users/me/consents",
            json={"consent_type": "analytics", "version": "1.0", "accepted": False},
            headers={"X-API-Key": client_api_key},
        )
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]  # Deux lignes distinctes

        resp = await client.get("/users/me/consents", headers={"X-API-Key": client_api_key})
        assert len(resp.json()) == 2  # Deux entrées historiques

    async def test_consent_types_endpoint(self, client: AsyncClient, client_api_key: str):
        """✅ GET /consents/types retourne la liste des types."""
        resp = await client.get(
            "/users/me/consents/types", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        types = resp.json()
        assert "privacy_policy" in types
        assert "terms_of_service" in types

    async def test_no_auth_blocked(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/users/me/consents")
        assert resp.status_code == 401


class TestDataExport:
    """B6-02 / B6-04 — Export données personnelles Art. 15 + 20."""

    async def test_export_json_ok(self, client: AsyncClient, client_api_key: str):
        """✅ Export JSON complet."""
        resp = await client.get(
            "/users/me/export?format=json",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "user" in data
        assert "export_date" in data
        assert "performance_sessions" in data
        assert "bookings" in data
        assert "payments" in data
        assert "body_measurements" in data
        assert "consents" in data

    async def test_export_json_contains_email(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Export contient l'email déchiffré."""
        resp = await client.get(
            "/users/me/export?format=json",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        user_data = resp.json()["user"]
        assert "@" in user_data.get("email", "")

    async def test_export_csv_ok(self, client: AsyncClient, client_api_key: str):
        """✅ Export CSV Art. 20."""
        resp = await client.get(
            "/users/me/export?format=csv",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        assert "PROFIL" in resp.text
        assert "SÉANCES" in resp.text

    async def test_export_invalid_format(self, client: AsyncClient, client_api_key: str):
        """❌ Format invalide → 422."""
        resp = await client.get(
            "/users/me/export?format=xml",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 422

    async def test_export_requires_auth(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/users/me/export?format=json")
        assert resp.status_code == 401

    async def test_export_token_generate(self, client: AsyncClient, client_api_key: str):
        """✅ Générer un token d'export signé."""
        resp = await client.post(
            "/users/me/export/token?format=json",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["expires_in_hours"] == 24
        assert data["format"] == "json"

    async def test_export_download_by_token(self, client: AsyncClient, client_api_key: str):
        """✅ Téléchargement export via token signé (sans API key)."""
        # Générer le token
        token_resp = await client.post(
            "/users/me/export/token?format=json",
            headers={"X-API-Key": client_api_key},
        )
        token = token_resp.json()["token"]

        # Télécharger sans X-API-Key
        dl_resp = await client.get(f"/users/me/export/download?token={token}")
        assert dl_resp.status_code == 200

    async def test_export_download_invalid_token(self, client: AsyncClient):
        """❌ Token invalide → 401."""
        resp = await client.get("/users/me/export/download?token=invalid_token_xyz")
        assert resp.status_code == 401


class TestAccountDeletion:
    """B6-03 — Droit à l'effacement Art. 17."""

    async def test_request_deletion_ok(self, client: AsyncClient, client_api_key: str):
        """✅ Demande de suppression de compte."""
        resp = await client.delete(
            "/users/me/",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "30 jours" in data["message"]
        assert "deletion_requested_at" in data
        assert "effective_at" in data

    async def test_request_deletion_idempotent(self, client: AsyncClient, client_api_key: str):
        """✅ Double demande de suppression → même date retournée."""
        r1 = await client.delete("/users/me/", headers={"X-API-Key": client_api_key})
        r2 = await client.delete("/users/me/", headers={"X-API-Key": client_api_key})
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["deletion_requested_at"] == r2.json()["deletion_requested_at"]

    async def test_deletion_requires_auth(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.delete("/users/me/")
        assert resp.status_code == 401


class TestExportTokenCrypto:
    """Tests unitaires du service export token."""

    def test_generate_and_verify_token(self):
        """✅ Token généré → vérifié avec succès."""
        from app.services.rgpd_service import generate_export_token, verify_export_token
        uid = uuid.uuid4()
        token = generate_export_token(uid, fmt="json")
        result = verify_export_token(token)
        assert result is not None
        user_id_str, fmt = result
        assert str(uid) == user_id_str
        assert fmt == "json"

    def test_tampered_token_rejected(self):
        """❌ Token falsifié → rejeté."""
        from app.services.rgpd_service import generate_export_token, verify_export_token
        uid = uuid.uuid4()
        token = generate_export_token(uid, fmt="json")
        # Falsifier la signature
        tampered = token[:-4] + "xxxx"
        assert verify_export_token(tampered) is None

    def test_invalid_token_rejected(self):
        """❌ Token malformé → rejeté."""
        from app.services.rgpd_service import verify_export_token
        assert verify_export_token("not:a:valid:token:at:all") is None
        assert verify_export_token("") is None
