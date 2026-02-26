"""Service Strava OAuth2 + push/import activités — B5-04.

Flux OAuth :
  1. GET /integrations/strava → URL d'autorisation Strava
  2. GET /integrations/strava/callback?code=… → échange code → token → stockage chiffré
  3. POST /integrations/strava/push/{session_id} → push séance en activité Strava
  4. GET /integrations/strava/import → importe les activités Strava en séances
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token_crypto import decrypt_token, encrypt_token
from app.repositories import integration_repository as repo

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/activities"
STRAVA_SCOPE = "activity:write,activity:read_all"


def get_client_id() -> str:
    return os.environ.get("STRAVA_CLIENT_ID", "")


def get_client_secret() -> str:
    return os.environ.get("STRAVA_CLIENT_SECRET", "")


def get_redirect_uri(base_url: str = "") -> str:
    base = base_url or os.environ.get("APP_BASE_URL", "http://localhost:8000")
    return f"{base}/integrations/strava/callback"


# ── OAuth ──────────────────────────────────────────────────────────────────────

def build_authorize_url(state: str = "", base_url: str = "") -> str:
    """Construit l'URL d'autorisation Strava."""
    params = {
        "client_id": get_client_id(),
        "redirect_uri": get_redirect_uri(base_url),
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": STRAVA_SCOPE,
        "state": state,
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v)
    return f"{STRAVA_AUTH_URL}?{qs}"


async def handle_callback(
    db: AsyncSession,
    user_id: uuid.UUID,
    code: str,
    base_url: str = "",
    *,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Échange le code contre un token, stocke chiffré."""
    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": get_client_id(),
                "client_secret": get_client_secret(),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": get_redirect_uri(base_url),
            },
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    data = resp.json()
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token")
    expires_at_ts = data.get("expires_at")
    expires_at = (
        datetime.fromtimestamp(expires_at_ts, tz=timezone.utc) if expires_at_ts else None
    )
    scope = data.get("scope", STRAVA_SCOPE)

    await repo.upsert_token(
        db,
        user_id=user_id,
        provider="strava",
        access_token_enc=encrypt_token(access_token),
        refresh_token_enc=encrypt_token(refresh_token) if refresh_token else None,
        expires_at=expires_at,
        scope=scope,
    )
    await db.commit()
    return {"status": "connected", "scope": scope, "athlete": data.get("athlete", {})}


async def _get_access_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    """Récupère le token d'accès Strava (refresh si expiré)."""
    token = await repo.get_token(db, user_id, "strava")
    if token is None:
        raise ValueError("Compte Strava non connecté")
    if token.expires_at and token.expires_at < datetime.now(tz=timezone.utc):
        # Refresh
        if token.refresh_token_enc is None:
            raise ValueError("Token Strava expiré et pas de refresh token")
        refresh = decrypt_token(token.refresh_token_enc)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                STRAVA_TOKEN_URL,
                data={
                    "client_id": get_client_id(),
                    "client_secret": get_client_secret(),
                    "refresh_token": refresh,
                    "grant_type": "refresh_token",
                },
            )
            resp.raise_for_status()
        data = resp.json()
        new_access = data.get("access_token", "")
        new_refresh = data.get("refresh_token", refresh)
        new_expires = datetime.fromtimestamp(
            data.get("expires_at", 0), tz=timezone.utc
        )
        await repo.upsert_token(
            db,
            user_id=user_id,
            provider="strava",
            access_token_enc=encrypt_token(new_access),
            refresh_token_enc=encrypt_token(new_refresh),
            expires_at=new_expires,
            scope=token.scope,
        )
        await db.commit()
        return new_access
    return decrypt_token(token.access_token_enc)


# ── Push session → Strava ──────────────────────────────────────────────────────

def _session_to_strava_payload(session: Any) -> dict:
    """Convertit une PerformanceSession en payload Strava."""
    sport = "WeightTraining"
    # Estimation durée : 60 min par défaut si non renseignée
    duration_sec = 3600
    return {
        "name": getattr(session, "notes", None) or "Séance MyCoach",
        "type": sport,
        "start_date_local": session.session_date.isoformat(),
        "elapsed_time": duration_sec,
        "description": "Importé depuis MyCoach",
    }


async def push_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    session: Any,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Envoie une séance de performance à Strava."""
    access_token = await _get_access_token(db, user_id)
    payload = _session_to_strava_payload(session)

    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.post(
            STRAVA_ACTIVITIES_URL,
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    return resp.json()


# ── Import activités Strava → séances ─────────────────────────────────────────

async def import_activities(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    per_page: int = 10,
    http_client: httpx.AsyncClient | None = None,
) -> list[dict]:
    """Importe les dernières activités Strava (lecture seule, pour affichage)."""
    access_token = await _get_access_token(db, user_id)

    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.get(
            "https://www.strava.com/api/v3/athlete/activities",
            params={"per_page": per_page},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    return resp.json()
