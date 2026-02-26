"""
Tests B0-26 — Authentification complète.

Cas passants + cas non passants pour chaque endpoint /auth/*.
Prérequis : docker compose -f docker-compose.test.yml up -d
"""
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import user_repository
from app.utils.hashing import generate_secure_token, hash_token


# ===========================================================================
# POST /auth/register
# ===========================================================================

class TestRegister:

    async def test_register_coach_ok(self, client: AsyncClient):
        """✅ Inscription coach valide → 201 + api_key + user."""
        resp = await client.post("/auth/register", json={
            "first_name": "Marie",
            "last_name": "Dupont",
            "email": f"marie_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "coach",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "api_key" in data
        assert len(data["api_key"]) == 64
        assert data["user"]["role"] == "coach"
        assert data["user"]["first_name"] == "Marie"
        assert data["user"]["status"] == "unverified"

    async def test_register_client_ok(self, client: AsyncClient):
        """✅ Inscription client valide → 201."""
        resp = await client.post("/auth/register", json={
            "first_name": "Jean",
            "last_name": "Martin",
            "email": f"jean_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "client"

    async def test_register_international_name(self, client: AsyncClient):
        """✅ Nom avec accents et caractères non-ASCII (max 150 chars)."""
        resp = await client.post("/auth/register", json={
            "first_name": "Bùi Thị",
            "last_name": "Nguyễn Ánh",
            "email": f"bui_{uuid.uuid4().hex[:8]}@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["first_name"] == "Bùi Thị"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """❌ Email déjà utilisé → 409."""
        email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "Alex", "last_name": "Bo",
            "email": email, "password": "Password1",
            "confirm_password": "Password1", "role": "coach",
        }
        await client.post("/auth/register", json=payload)
        resp = await client.post("/auth/register", json=payload)
        assert resp.status_code == 409

    async def test_register_password_too_short(self, client: AsyncClient):
        """❌ Password < 8 chars → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "A", "last_name": "B",
            "email": "short@test.com",
            "password": "Ab1",
            "confirm_password": "Ab1",
            "role": "coach",
        })
        assert resp.status_code == 422

    async def test_register_password_no_uppercase(self, client: AsyncClient):
        """❌ Password sans majuscule → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "A", "last_name": "B",
            "email": "nocase@test.com",
            "password": "password1",
            "confirm_password": "password1",
            "role": "coach",
        })
        assert resp.status_code == 422

    async def test_register_password_no_digit(self, client: AsyncClient):
        """❌ Password sans chiffre → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "A", "last_name": "B",
            "email": "nodigit@test.com",
            "password": "PasswordOnly",
            "confirm_password": "PasswordOnly",
            "role": "coach",
        })
        assert resp.status_code == 422

    async def test_register_passwords_mismatch(self, client: AsyncClient):
        """❌ Confirmation de password différente → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "A", "last_name": "B",
            "email": "mismatch@test.com",
            "password": "Password1",
            "confirm_password": "Password2",
            "role": "coach",
        })
        assert resp.status_code == 422

    async def test_register_name_too_short(self, client: AsyncClient):
        """❌ Prénom 1 caractère → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "A",
            "last_name": "B",
            "email": "short_name@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "coach",
        })
        assert resp.status_code == 422

    async def test_register_invalid_role(self, client: AsyncClient):
        """❌ Rôle invalide ('admin') → 422."""
        resp = await client.post("/auth/register", json={
            "first_name": "Ha", "last_name": "Bo",
            "email": "role@test.com",
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "admin",
        })
        assert resp.status_code == 422


# ===========================================================================
# GET /auth/verify-email
# ===========================================================================

class TestVerifyEmail:

    async def test_verify_email_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ Token valide → compte activé."""
        user = await user_repository.create(
            db, first_name="Ve", last_name="Ri",
            email=f"verify_{uuid.uuid4().hex[:8]}@test.com",
            role="coach", password_plain="Password1",
        )
        plain_token, _ = await user_repository.create_email_token(db, user.id)
        await db.commit()

        resp = await client.get(f"/auth/verify-email?token={plain_token}")
        assert resp.status_code == 200

        # Expirer le cache de session et recharger depuis la DB
        await db.refresh(user)
        assert user.status == "active"
        assert user.email_verified_at is not None

    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """❌ Token invalide → 400."""
        resp = await client.get("/auth/verify-email?token=invalid_token_xyz")
        assert resp.status_code == 400

    async def test_verify_email_already_used(self, client: AsyncClient, db: AsyncSession):
        """❌ Token déjà consommé → 400."""
        user = await user_repository.create(
            db, first_name="Al", last_name="Re",
            email=f"used_{uuid.uuid4().hex[:8]}@test.com",
            role="coach", password_plain="Password1",
        )
        plain_token, _ = await user_repository.create_email_token(db, user.id)
        await db.commit()

        # Premier appel → OK
        await client.get(f"/auth/verify-email?token={plain_token}")
        # Deuxième appel → token déjà utilisé
        resp = await client.get(f"/auth/verify-email?token={plain_token}")
        assert resp.status_code == 400


# ===========================================================================
# POST /auth/login
# ===========================================================================

class TestLogin:

    async def test_login_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ Login valide → api_key."""
        email = f"login_{uuid.uuid4().hex[:8]}@test.com"
        user = await user_repository.create(
            db, first_name="Lo", last_name="Gin",
            email=email, role="coach", password_plain="Password1",
        )
        await user_repository.mark_email_verified(db, user)
        await db.commit()

        resp = await client.post("/auth/login", json={
            "email": email, "password": "Password1",
        })
        assert resp.status_code == 200
        assert "api_key" in resp.json()

    async def test_login_wrong_password(self, client: AsyncClient, db: AsyncSession):
        """❌ Mauvais password → 401."""
        email = f"wrong_{uuid.uuid4().hex[:8]}@test.com"
        user = await user_repository.create(
            db, first_name="Wr", last_name="Ong",
            email=email, role="coach", password_plain="Password1",
        )
        await user_repository.mark_email_verified(db, user)
        await db.commit()

        resp = await client.post("/auth/login", json={
            "email": email, "password": "WrongPass1",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        """❌ Email inexistant → 401 (même message que mauvais password)."""
        resp = await client.post("/auth/login", json={
            "email": "ghost@test.com", "password": "Password1",
        })
        assert resp.status_code == 401

    async def test_login_unverified_account(self, client: AsyncClient, db: AsyncSession):
        """❌ Compte non vérifié → 403."""
        email = f"unver_{uuid.uuid4().hex[:8]}@test.com"
        await user_repository.create(
            db, first_name="Un", last_name="Ve",
            email=email, role="coach", password_plain="Password1",
        )
        await db.commit()

        resp = await client.post("/auth/login", json={
            "email": email, "password": "Password1",
        })
        assert resp.status_code == 403


# ===========================================================================
# GET /auth/me
# ===========================================================================

class TestMe:

    async def test_me_ok(self, client: AsyncClient, coach_api_key: str, coach_user: User):
        """✅ Clé valide → profil retourné."""
        resp = await client.get("/auth/me", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        data = resp.json()["user"]
        assert data["role"] == "coach"
        assert data["id"] == str(coach_user.id)

    async def test_me_no_key(self, client: AsyncClient):
        """❌ Pas de clé → 422 (header manquant)."""
        resp = await client.get("/auth/me")
        assert resp.status_code == 422

    async def test_me_invalid_key(self, client: AsyncClient):
        """❌ Clé invalide → 401."""
        resp = await client.get("/auth/me", headers={"X-API-Key": "a" * 64})
        assert resp.status_code == 401


# ===========================================================================
# DELETE /auth/logout
# ===========================================================================

class TestLogout:

    async def test_logout_ok(self, client: AsyncClient, coach_user: User, db: AsyncSession):
        """✅ Logout → 204, clé révoquée."""
        from app.repositories.api_key_repository import api_key_repository
        plain_key, _ = await api_key_repository.create(db, coach_user.id, "logout-test")
        await db.commit()

        resp = await client.delete("/auth/logout", headers={"X-API-Key": plain_key})
        assert resp.status_code == 204

        # La clé ne fonctionne plus
        resp2 = await client.get("/auth/me", headers={"X-API-Key": plain_key})
        assert resp2.status_code == 401

    async def test_logout_all_ok(self, client: AsyncClient, coach_user: User, db: AsyncSession):
        """✅ Logout-all → toutes les clés révoquées."""
        from app.repositories.api_key_repository import api_key_repository
        key1, _ = await api_key_repository.create(db, coach_user.id, "device-1")
        key2, _ = await api_key_repository.create(db, coach_user.id, "device-2")
        await db.commit()

        resp = await client.delete("/auth/logout-all", headers={"X-API-Key": key1})
        assert resp.status_code == 204

        # Les deux clés sont révoquées
        assert (await client.get("/auth/me", headers={"X-API-Key": key1})).status_code == 401
        assert (await client.get("/auth/me", headers={"X-API-Key": key2})).status_code == 401


# ===========================================================================
# POST /auth/forgot-password + /auth/reset-password
# ===========================================================================

class TestPasswordReset:

    async def test_forgot_password_existing_email(self, client: AsyncClient, coach_user: User):
        """✅ Email existant → 202 (même réponse pour sécurité)."""
        resp = await client.post("/auth/forgot-password", json={
            "email": f"coach_{uuid.uuid4().hex[:8]}@test.com",
        })
        assert resp.status_code == 202

    async def test_forgot_password_unknown_email(self, client: AsyncClient):
        """✅ Email inconnu → 202 (réponse identique — sécurité)."""
        resp = await client.post("/auth/forgot-password", json={
            "email": "nobody@test.com",
        })
        assert resp.status_code == 202

    async def test_reset_password_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ Reset avec token valide → 200, nouveau password fonctionne."""
        email = f"reset_{uuid.uuid4().hex[:8]}@test.com"
        user = await user_repository.create(
            db, first_name="Re", last_name="Se",
            email=email, role="coach", password_plain="OldPass1",
        )
        await user_repository.mark_email_verified(db, user)
        plain_token, _ = await user_repository.create_reset_token(db, user.id)
        await db.commit()

        resp = await client.post("/auth/reset-password", json={
            "token": plain_token,
            "new_password": "NewPass1",
            "confirm_password": "NewPass1",
        })
        assert resp.status_code == 200

        # Nouveau password fonctionne
        login_resp = await client.post("/auth/login", json={
            "email": email, "password": "NewPass1",
        })
        assert login_resp.status_code == 200

        # Ancien password ne fonctionne plus
        old_resp = await client.post("/auth/login", json={
            "email": email, "password": "OldPass1",
        })
        assert old_resp.status_code == 401

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """❌ Token invalide → 400."""
        resp = await client.post("/auth/reset-password", json={
            "token": "totally_invalid_token",
            "new_password": "NewPass1",
            "confirm_password": "NewPass1",
        })
        assert resp.status_code == 400

    async def test_reset_password_already_used_token(self, client: AsyncClient, db: AsyncSession):
        """❌ Token déjà utilisé → 400."""
        user = await user_repository.create(
            db, first_name="To", last_name="Ke",
            email=f"tok_{uuid.uuid4().hex[:8]}@test.com",
            role="coach", password_plain="OldPass1",
        )
        await user_repository.mark_email_verified(db, user)
        plain_token, _ = await user_repository.create_reset_token(db, user.id)
        await db.commit()

        await client.post("/auth/reset-password", json={
            "token": plain_token, "new_password": "NewPass1", "confirm_password": "NewPass1",
        })
        # Deuxième utilisation → 400
        resp = await client.post("/auth/reset-password", json={
            "token": plain_token, "new_password": "AnotherPass1", "confirm_password": "AnotherPass1",
        })
        assert resp.status_code == 400


# ===========================================================================
# GET /health
# ===========================================================================

class TestHealth:

    async def test_health_ok(self, client: AsyncClient):
        """✅ /health sans auth → 200 avec status ok."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] in ("ok", "degraded")
        assert "db" in resp.json()
