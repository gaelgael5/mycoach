"""Tests — Vérification du numéro de téléphone par OTP SMS.

Couvre :
1.  test_request_otp_ok             POST /auth/verify-phone/request → 204
2.  test_confirm_otp_ok             request puis confirm avec bon code → 204, phone_verified_at set
3.  test_confirm_wrong_code         mauvais code → 400
4.  test_confirm_expired_otp        OTP créé avec expires_at dans le passé → 400
5.  test_max_attempts               3 mauvais codes → 400 (OtpMaxAttemptsError)
6.  test_already_verified           demander OTP si phone déjà vérifié → 400
7.  test_no_phone                   user sans phone demande OTP → 400
8.  test_no_auth                    sans api key → 401
9.  test_otp_format                 generate_otp() retourne exactement 6 chars [0-9a-z]
10. test_rate_limit                 3 OTPs en < 1h → 4ème → 429
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.phone_verification_token import PhoneVerificationToken
from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository
from app.utils.otp import OTP_ALPHABET, OTP_LENGTH, generate_otp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_user_with_phone(
    db: AsyncSession,
    role: str = "coach",
    phone: str = "+33612345678",
) -> tuple:
    """Crée un utilisateur vérifié avec un numéro de téléphone."""
    user = await user_repository.create(
        db,
        first_name="Test",
        last_name="Phone",
        email=f"{role}_otp_{uuid.uuid4().hex[:8]}@test.com",
        role=role,
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    user.phone = phone
    await db.flush()
    plain_key, _ = await api_key_repository.create(db, user.id, "test-device")
    await db.commit()
    await db.refresh(user)
    return user, plain_key


async def _get_latest_token(db: AsyncSession, user_id: uuid.UUID) -> PhoneVerificationToken:
    """Récupère le dernier token OTP depuis la DB."""
    result = await db.execute(
        select(PhoneVerificationToken)
        .where(PhoneVerificationToken.user_id == user_id)
        .order_by(PhoneVerificationToken.created_at.desc())
    )
    return result.scalars().first()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_request_otp_ok(client: AsyncClient, db: AsyncSession):
    """1. POST /auth/verify-phone/request → 204."""
    user, key = await _make_user_with_phone(db)
    resp = await client.post(
        "/auth/verify-phone/request",
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_confirm_otp_ok(client: AsyncClient, db: AsyncSession):
    """2. request puis confirm avec bon code → 204, phone_verified_at set."""
    user, key = await _make_user_with_phone(db)

    # Request OTP
    resp = await client.post(
        "/auth/verify-phone/request",
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 204

    # Récupérer le code depuis la DB
    token = await _get_latest_token(db, user.id)
    assert token is not None
    code = token.code

    # Confirm avec le bon code
    resp = await client.post(
        "/auth/verify-phone/confirm",
        json={"code": code},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 204

    # Vérifier que phone_verified_at est bien défini
    await db.refresh(user)
    assert user.phone_verified_at is not None


@pytest.mark.asyncio
async def test_confirm_wrong_code(client: AsyncClient, db: AsyncSession):
    """3. mauvais code → 400."""
    user, key = await _make_user_with_phone(db)

    # Request OTP
    await client.post("/auth/verify-phone/request", headers={"X-API-Key": key})

    # Confirm avec un mauvais code
    resp = await client.post(
        "/auth/verify-phone/confirm",
        json={"code": "xxxxxx"},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_confirm_expired_otp(client: AsyncClient, db: AsyncSession):
    """4. OTP créé avec expires_at dans le passé → 400."""
    user, key = await _make_user_with_phone(db)

    # Créer directement un token expiré en DB
    expired_token = PhoneVerificationToken(
        id=uuid.uuid4(),
        user_id=user.id,
        phone=user.phone,
        code="abc123",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        attempts_count=0,
    )
    db.add(expired_token)
    await db.commit()

    resp = await client.post(
        "/auth/verify-phone/confirm",
        json={"code": "abc123"},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_max_attempts(client: AsyncClient, db: AsyncSession):
    """5. 3 mauvais codes → OtpMaxAttemptsError → 400."""
    user, key = await _make_user_with_phone(db)

    # Request OTP
    await client.post("/auth/verify-phone/request", headers={"X-API-Key": key})

    # 3 mauvais codes
    for _ in range(3):
        resp = await client.post(
            "/auth/verify-phone/confirm",
            json={"code": "badxxx"},
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_already_verified(client: AsyncClient, db: AsyncSession):
    """6. demander OTP si phone déjà vérifié → 400."""
    user, key = await _make_user_with_phone(db)
    user.phone_verified_at = datetime.now(timezone.utc)
    await db.commit()

    resp = await client.post(
        "/auth/verify-phone/request",
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 400
    assert "vérifié" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_no_phone(client: AsyncClient, db: AsyncSession):
    """7. user sans phone demande OTP → 400."""
    user = await user_repository.create(
        db,
        first_name="No",
        last_name="Phone",
        email=f"nophone_{uuid.uuid4().hex[:8]}@test.com",
        role="client",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "device")
    await db.commit()

    resp = await client.post(
        "/auth/verify-phone/request",
        headers={"X-API-Key": plain_key},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_no_auth(client: AsyncClient):
    """8. sans api key → 401."""
    resp = await client.post("/auth/verify-phone/request")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_otp_format():
    """9. generate_otp() retourne exactement 6 chars [0-9a-z]."""
    for _ in range(100):
        otp = generate_otp()
        assert len(otp) == OTP_LENGTH, f"OTP length wrong: {otp!r}"
        assert all(c in OTP_ALPHABET for c in otp), f"OTP contains invalid chars: {otp!r}"


@pytest.mark.asyncio
async def test_rate_limit(client: AsyncClient, db: AsyncSession):
    """10. 3 OTPs en < 1h → 4ème → 429."""
    user, key = await _make_user_with_phone(db)

    # Envoyer 3 OTPs (max autorisés)
    for _ in range(3):
        resp = await client.post(
            "/auth/verify-phone/request",
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 204

    # Le 4ème doit être rejeté
    resp = await client.post(
        "/auth/verify-phone/request",
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 429
