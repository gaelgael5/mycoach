"""Service RGPD — Art. 15 (accès), Art. 17 (effacement), Art. 20 (portabilité) — B6-02/03/04.

Règles :
- Export JSON/CSV : toutes les données personnelles déchiffrées
- DELETE /users/me → deletion_requested_at = now(), suppression effective J+30
- Export disponible 24h via token signé (HMAC)
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token_crypto import decrypt_token
from app.models.booking import Booking
from app.models.consent import Consent
from app.models.integration import BodyMeasurement, OAuthToken
from app.models.payment import Payment
from app.models.performance_session import PerformanceSession
from app.models.user import User
from app.repositories import integration_repository


# ── Export données ─────────────────────────────────────────────────────────────

async def export_user_data(db: AsyncSession, user: User) -> dict[str, Any]:
    """Art. 15 + 20 — export complet de toutes les données personnelles (JSON)."""

    # Profil coach (eager load séparé pour éviter lazy load MissingGreenlet)
    profile_data: dict = {}
    from app.models.coach_profile import CoachProfile
    cp = (await db.execute(
        select(CoachProfile).where(CoachProfile.user_id == user.id)
    )).scalar_one_or_none()
    if cp:
        profile_data = {
            "bio": cp.bio,
            "specialties": cp.specialties,
            "currency": cp.currency,
        }

    # Séances de performance
    q = select(PerformanceSession).where(PerformanceSession.user_id == user.id)
    sessions = (await db.execute(q)).scalars().all()

    # Réservations (en tant que client)
    q = select(Booking).where(Booking.client_id == user.id)
    bookings = (await db.execute(q)).scalars().all()

    # Paiements
    q = select(Payment).where(Payment.client_id == user.id)
    payments = (await db.execute(q)).scalars().all()

    # Mesures corporelles
    measurements = await integration_repository.list_measurements(db, user.id, limit=1000)

    # Consentements
    q = select(Consent).where(Consent.user_id == user.id).order_by(Consent.accepted_at.desc())
    consents = (await db.execute(q)).scalars().all()

    # Intégrations connectées (sans exposer les tokens)
    tokens = await integration_repository.list_user_tokens(db, user.id)

    return {
        "export_date": datetime.now(tz=timezone.utc).isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,  # déchiffré par le TypeDecorator EncryptedString
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "locale": user.locale,
            "timezone": user.timezone,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "coach_profile": profile_data,
        "performance_sessions": [
            {
                "id": str(s.id),
                "session_date": s.session_date.isoformat(),
                "session_type": s.session_type,
                "feeling": s.feeling,
            }
            for s in sessions
        ],
        "bookings": [
            {
                "id": str(b.id),
                "status": b.status,
                "booking_time": b.booking_time.isoformat() if b.booking_time else None,
            }
            for b in bookings
        ],
        "payments": [
            {
                "id": str(p.id),
                "amount_cents": p.amount_cents,
                "currency": p.currency,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in payments
        ],
        "body_measurements": [
            {
                "measured_at": m.measured_at.isoformat(),
                "weight_kg": float(m.weight_kg) if m.weight_kg else None,
                "fat_pct": float(m.fat_pct) if m.fat_pct else None,
                "source": m.source,
            }
            for m in measurements
        ],
        "consents": [
            {
                "consent_type": c.consent_type,
                "version": c.version,
                "accepted": c.accepted,
                "accepted_at": c.accepted_at.isoformat(),
            }
            for c in consents
        ],
        "integrations_connected": [t.provider for t in tokens],
    }


async def export_user_data_csv(db: AsyncSession, user: User) -> str:
    """Art. 20 — export portabilité en CSV (mesures + séances)."""
    data = await export_user_data(db, user)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["=== PROFIL ==="])
    writer.writerow(["email", "first_name", "last_name", "role", "created_at"])
    u = data["user"]
    writer.writerow([u["email"], u["first_name"], u["last_name"], u["role"], u["created_at"]])
    writer.writerow([])

    writer.writerow(["=== SÉANCES ==="])
    writer.writerow(["id", "session_date", "session_type", "feeling"])
    for s in data["performance_sessions"]:
        writer.writerow([s["id"], s["session_date"], s["session_type"], s["feeling"]])
    writer.writerow([])

    writer.writerow(["=== MESURES CORPORELLES ==="])
    writer.writerow(["measured_at", "weight_kg", "fat_pct", "source"])
    for m in data["body_measurements"]:
        writer.writerow([m["measured_at"], m["weight_kg"], m["fat_pct"], m["source"]])
    writer.writerow([])

    writer.writerow(["=== PAIEMENTS ==="])
    writer.writerow(["id", "amount_cents", "currency", "status", "created_at"])
    for p in data["payments"]:
        writer.writerow([p["id"], p["amount_cents"], p["currency"], p["status"], p["created_at"]])

    return output.getvalue()


# ── Export token signé (24h) ───────────────────────────────────────────────────

def _signing_key() -> str:
    return os.environ.get("SECRET_KEY", "dev_secret")


def generate_export_token(user_id: uuid.UUID, fmt: str = "json") -> str:
    """Génère un token HMAC signé valable 24h pour télécharger l'export."""
    expires = int((datetime.now(tz=timezone.utc) + timedelta(hours=24)).timestamp())
    payload = f"{user_id}:{fmt}:{expires}"
    sig = hmac.new(_signing_key().encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_export_token(token: str) -> tuple[str, str] | None:
    """Vérifie le token et retourne (user_id, fmt) ou None si invalide/expiré."""
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        user_id, fmt, expires_str, sig = parts
        expires = int(expires_str)
        if expires < int(datetime.now(tz=timezone.utc).timestamp()):
            return None
        payload = f"{user_id}:{fmt}:{expires}"
        expected = hmac.new(_signing_key().encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        return user_id, fmt
    except Exception:
        return None


# ── Suppression RGPD ───────────────────────────────────────────────────────────

async def request_deletion(db: AsyncSession, user: User) -> datetime:
    """Art. 17 — marque le compte pour suppression effective J+30."""
    if user.deletion_requested_at is not None:
        return user.deletion_requested_at
    user.deletion_requested_at = datetime.now(tz=timezone.utc)
    await db.flush()
    await db.commit()
    return user.deletion_requested_at


async def anonymize_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Anonymisation effective (à exécuter par cron J+30).

    PII supprimés, données comptables conservées anonymisées.
    """
    q = select(User).where(User.id == user_id)
    user = (await db.execute(q)).scalar_one_or_none()
    if user is None:
        return False
    if user.deletion_requested_at is None:
        return False
    deadline = user.deletion_requested_at + timedelta(days=30)
    if datetime.now(tz=timezone.utc) < deadline:
        return False  # Pas encore le moment

    # Anonymisation : effacement des champs PII
    user.first_name = "Anonyme"
    user.last_name = ""
    user.email = f"deleted_{user_id}@anonymized.invalid"
    user.email_hash = hashlib.sha256(str(user_id).encode()).hexdigest()
    user.phone = None
    user.search_token = ""
    user.status = "deleted"

    # Supprimer les tokens OAuth (données de tiers sensibles)
    from sqlalchemy import delete as sql_delete
    from app.models.integration import OAuthToken
    await db.execute(sql_delete(OAuthToken).where(OAuthToken.user_id == user_id))

    await db.flush()
    await db.commit()
    return True


# ── Consentements ──────────────────────────────────────────────────────────────

def _hash_field(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode()).hexdigest()


async def record_consent(
    db: AsyncSession,
    user_id: uuid.UUID,
    consent_type: str,
    version: str,
    accepted: bool,
    ip: str | None = None,
    user_agent: str | None = None,
) -> Consent:
    """Enregistre un consentement (log immuable)."""
    c = Consent(
        id=uuid.uuid4(),
        user_id=user_id,
        consent_type=consent_type,
        version=version,
        accepted=accepted,
        ip_hash=_hash_field(ip),
        user_agent_hash=_hash_field(user_agent),
    )
    db.add(c)
    await db.flush()
    await db.commit()
    return c


async def list_consents(db: AsyncSession, user_id: uuid.UUID) -> list[Consent]:
    q = (
        select(Consent)
        .where(Consent.user_id == user_id)
        .order_by(Consent.accepted_at.desc())
    )
    return list((await db.execute(q)).scalars().all())
