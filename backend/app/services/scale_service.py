"""Service Withings OAuth2 + import mesures balance + saisie manuelle — B5-06.

Flux OAuth Withings :
  1. GET /integrations/scale → URL Withings
  2. GET /integrations/scale/callback?code=… → échange → stockage
  3. GET /integrations/scale/import → import depuis Withings
  4. POST /integrations/scale/manual → saisie manuelle
  5. GET /integrations/scale/history → historique
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token_crypto import decrypt_token, encrypt_token
from app.repositories import integration_repository as repo

WITHINGS_AUTH_URL = "https://account.withings.com/oauth2_user/authorize2"
WITHINGS_TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"
WITHINGS_MEASURE_URL = "https://wbsapi.withings.net/measure"
WITHINGS_SCOPE = "user.metrics"


def _client_id() -> str:
    return os.environ.get("WITHINGS_CLIENT_ID", "")


def _client_secret() -> str:
    return os.environ.get("WITHINGS_CLIENT_SECRET", "")


def _redirect_uri(base_url: str = "") -> str:
    base = base_url or os.environ.get("APP_BASE_URL", "http://localhost:8000")
    return f"{base}/integrations/scale/callback"


# ── OAuth ──────────────────────────────────────────────────────────────────────

def build_authorize_url(state: str = "", base_url: str = "") -> str:
    params = {
        "response_type": "code",
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(base_url),
        "scope": WITHINGS_SCOPE,
        "state": state,
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v)
    return f"{WITHINGS_AUTH_URL}?{qs}"


async def handle_callback(
    db: AsyncSession,
    user_id: uuid.UUID,
    code: str,
    base_url: str = "",
    *,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.post(
            WITHINGS_TOKEN_URL,
            data={
                "action": "requesttoken",
                "client_id": _client_id(),
                "client_secret": _client_secret(),
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _redirect_uri(base_url),
            },
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    body = resp.json()
    data = body.get("body", {})
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token")
    from datetime import timedelta
    expires_in = data.get("expires_in", 10800)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    scope = data.get("scope", WITHINGS_SCOPE)

    await repo.upsert_token(
        db,
        user_id=user_id,
        provider="withings",
        access_token_enc=encrypt_token(access_token),
        refresh_token_enc=encrypt_token(refresh_token) if refresh_token else None,
        expires_at=expires_at,
        scope=scope,
    )
    await db.commit()
    return {"status": "connected", "scope": scope}


async def _get_access_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    token = await repo.get_token(db, user_id, "withings")
    if token is None:
        raise ValueError("Balance Withings non connectée")
    if token.expires_at and token.expires_at < datetime.now(tz=timezone.utc):
        if not token.refresh_token_enc:
            raise ValueError("Token Withings expiré, reconnexion requise")
        refresh = decrypt_token(token.refresh_token_enc)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                WITHINGS_TOKEN_URL,
                data={
                    "action": "requesttoken",
                    "client_id": _client_id(),
                    "client_secret": _client_secret(),
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                },
            )
            resp.raise_for_status()
        body = resp.json().get("body", {})
        new_access = body["access_token"]
        new_refresh = body.get("refresh_token", refresh)
        expires_in = body.get("expires_in", 10800)
        new_expires = datetime.now(tz=timezone.utc)
        await repo.upsert_token(
            db, user_id=user_id, provider="withings",
            access_token_enc=encrypt_token(new_access),
            refresh_token_enc=encrypt_token(new_refresh),
            expires_at=new_expires, scope=token.scope,
        )
        await db.commit()
        return new_access
    return decrypt_token(token.access_token_enc)


# ── Import mesures Withings ────────────────────────────────────────────────────

WITHINGS_MEASURE_TYPES = {
    1: "weight_kg",
    6: "fat_pct",
    76: "muscle_pct",
    88: "bone_kg",
    77: "water_pct",
}


def _parse_withings_measure(group: dict) -> dict:
    """Parse un groupe de mesure Withings."""
    result: dict[str, Decimal | None] = {
        "weight_kg": None, "bmi": None, "fat_pct": None,
        "muscle_pct": None, "bone_kg": None, "water_pct": None,
    }
    for m in group.get("measures", []):
        mtype = m.get("type")
        field = WITHINGS_MEASURE_TYPES.get(mtype)
        if field:
            value = Decimal(str(m["value"])) * Decimal(str(10 ** m.get("unit", 0)))
            result[field] = value
    return result


async def import_measurements(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> list[dict]:
    """Importe les mesures Withings en base."""
    access_token = await _get_access_token(db, user_id)

    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.post(
            WITHINGS_MEASURE_URL,
            data={"action": "getmeas", "meastypes": "1,6,76,88,77", "lastupdate": 0},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    body = resp.json().get("body", {})
    groups = body.get("measuregrps", [])
    imported = []
    for group in groups:
        measured_at = datetime.fromtimestamp(group.get("date", 0), tz=timezone.utc)
        values = _parse_withings_measure(group)
        m = await repo.add_measurement(
            db,
            user_id=user_id,
            measured_at=measured_at,
            source="withings",
            **values,
        )
        imported.append(m)
    await db.commit()
    return imported


# ── Saisie manuelle ────────────────────────────────────────────────────────────

async def manual_entry(
    db: AsyncSession,
    user_id: uuid.UUID,
    measured_at: datetime,
    weight_kg: Decimal | None = None,
    fat_pct: Decimal | None = None,
    muscle_pct: Decimal | None = None,
    bone_kg: Decimal | None = None,
    water_pct: Decimal | None = None,
    bmi: Decimal | None = None,
) -> Any:
    m = await repo.add_measurement(
        db,
        user_id=user_id,
        measured_at=measured_at,
        source="manual",
        weight_kg=weight_kg,
        fat_pct=fat_pct,
        muscle_pct=muscle_pct,
        bone_kg=bone_kg,
        water_pct=water_pct,
        bmi=bmi,
    )
    await db.commit()
    return m
