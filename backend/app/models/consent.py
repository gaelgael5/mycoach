"""Modèle RGPD — Consentements utilisateurs — B6-05.

Log immuable (pas de DELETE ni UPDATE) :
- Chaque consentement = une ligne
- ip_hash = SHA-256(ip) — jamais l'IP en clair
- user_agent_hash = SHA-256(user_agent)
- version = version de la politique de confidentialité (ex: "1.0")
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


CONSENT_TYPES = [
    "terms_of_service",       # CGU
    "privacy_policy",         # Politique de confidentialité
    "marketing_emails",       # Emails marketing
    "analytics",              # Analytics
    "third_party_sharing",    # Partage tiers (Strava, Withings…)
]


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    consent_type: Mapped[str] = mapped_column(String(40), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)  # ex: "1.0", "2.1"
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)   # SHA-256
    user_agent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
