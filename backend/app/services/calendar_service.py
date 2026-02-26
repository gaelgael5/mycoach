"""Service Google Calendar OAuth2 + sync réservations — B5-05.

Flux OAuth :
  1. GET /integrations/calendar → URL d'autorisation Google
  2. GET /integrations/calendar/callback?code=… → échange code → token → stockage
  3. POST /integrations/calendar/sync/{booking_id} → push/update/delete event
  4. POST /integrations/calendar/sync-all → sync toutes les réservations confirmées
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

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GCAL_API_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
GCAL_SCOPE = "https://www.googleapis.com/auth/calendar.events"


def _client_id() -> str:
    return os.environ.get("GOOGLE_CLIENT_ID", "")


def _client_secret() -> str:
    return os.environ.get("GOOGLE_CLIENT_SECRET", "")


def _redirect_uri(base_url: str = "") -> str:
    base = base_url or os.environ.get("APP_BASE_URL", "http://localhost:8000")
    return f"{base}/integrations/calendar/callback"


# ── OAuth ──────────────────────────────────────────────────────────────────────

def build_authorize_url(state: str = "", base_url: str = "") -> str:
    params = {
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(base_url),
        "response_type": "code",
        "scope": GCAL_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v)
    return f"{GOOGLE_AUTH_URL}?{qs}"


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
            GOOGLE_TOKEN_URL,
            data={
                "client_id": _client_id(),
                "client_secret": _client_secret(),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": _redirect_uri(base_url),
            },
        )
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    data = resp.json()
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token")
    from datetime import timedelta
    expires_in = data.get("expires_in", 3600)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    scope = data.get("scope", GCAL_SCOPE)

    await repo.upsert_token(
        db,
        user_id=user_id,
        provider="google_calendar",
        access_token_enc=encrypt_token(access_token),
        refresh_token_enc=encrypt_token(refresh_token) if refresh_token else None,
        expires_at=expires_at,
        scope=scope,
    )
    await db.commit()
    return {"status": "connected", "scope": scope}


async def _get_access_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    token = await repo.get_token(db, user_id, "google_calendar")
    if token is None:
        raise ValueError("Google Calendar non connecté")
    if token.expires_at and token.expires_at < datetime.now(tz=timezone.utc):
        if not token.refresh_token_enc:
            raise ValueError("Token Google Calendar expiré, reconnexion requise")
        refresh = decrypt_token(token.refresh_token_enc)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": _client_id(),
                    "client_secret": _client_secret(),
                    "refresh_token": refresh,
                    "grant_type": "refresh_token",
                },
            )
            resp.raise_for_status()
        data = resp.json()
        new_access = data["access_token"]
        from datetime import timedelta as td
        expires_in = data.get("expires_in", 3600)
        new_expires = datetime.now(tz=timezone.utc) + td(seconds=expires_in)
        await repo.upsert_token(
            db, user_id=user_id, provider="google_calendar",
            access_token_enc=encrypt_token(new_access),
            refresh_token_enc=token.refresh_token_enc,
            expires_at=new_expires, scope=token.scope,
        )
        await db.commit()
        return new_access
    return decrypt_token(token.access_token_enc)


# ── Sync réservation → event Calendar ─────────────────────────────────────────

def _booking_to_event(booking: Any) -> dict:
    """Convertit une réservation en event Google Calendar."""
    from datetime import timedelta
    start: datetime = booking.booking_time
    end = start + timedelta(minutes=getattr(booking, "duration_min", 60))
    return {
        "summary": "Séance MyCoach",
        "description": f"Réservation #{booking.id}",
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
    }


async def sync_booking(
    db: AsyncSession,
    user_id: uuid.UUID,
    booking: Any,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Push ou update l'event Calendar pour une réservation."""
    access_token = await _get_access_token(db, user_id)
    event = _booking_to_event(booking)
    headers = {"Authorization": f"Bearer {access_token}"}

    client = http_client or httpx.AsyncClient()
    try:
        # Vérifier si event_id existe déjà sur le booking
        gcal_event_id = getattr(booking, "gcal_event_id", None)
        if gcal_event_id:
            resp = await client.put(
                f"{GCAL_API_URL}/{gcal_event_id}", json=event, headers=headers
            )
        else:
            resp = await client.post(GCAL_API_URL, json=event, headers=headers)
        resp.raise_for_status()
    finally:
        if http_client is None:
            await client.aclose()

    return resp.json()


async def delete_booking_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    gcal_event_id: str,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> bool:
    access_token = await _get_access_token(db, user_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    client = http_client or httpx.AsyncClient()
    try:
        resp = await client.delete(
            f"{GCAL_API_URL}/{gcal_event_id}", headers=headers
        )
        return resp.status_code in (200, 204)
    finally:
        if http_client is None:
            await client.aclose()
