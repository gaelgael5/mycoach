"""Modèles Phase 5 — Intégrations OAuth + balance — B5-01, B5-02."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    pass


OAUTH_PROVIDERS = ["strava", "google_calendar", "withings", "garmin"]
MEASUREMENT_SOURCES = ["withings", "xiaomi", "garmin", "manual"]


# ── B5-01 — Tokens OAuth ──────────────────────────────────────────────────────

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)  # OAUTH_PROVIDERS
    # Champs chiffrés via EncryptedToken (Fernet) pour les tokens sensibles
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ── B5-02 — Mesures corporelles ───────────────────────────────────────────────

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    bmi: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    fat_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    muscle_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    bone_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    water_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
