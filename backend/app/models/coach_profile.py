"""Modèle CoachProfile — B1-03."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachProfile(Base):
    """Profil professionnel d'un coach (relation 1-1 avec users)."""

    __tablename__ = "coach_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    bio: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Description professionnelle publique — non chiffré"
    )
    verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Profil vérifié par un admin"
    )
    country: Mapped[str | None] = mapped_column(
        String(2), nullable=True, comment="ISO 3166-1 alpha-2"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR",
        comment="ISO 4217 — devise par défaut du coach"
    )
    session_duration_min: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=60,
        comment="Durée par défaut d'une séance en minutes"
    )
    discovery_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Le coach propose des séances découverte"
    )
    discovery_free: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="La séance découverte est gratuite"
    )
    discovery_price_cents: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Prix en centimes si discovery_free=False"
    )
    booking_horizon_days: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=30,
        comment="Horizon de réservation max en jours"
    )
    sms_sender_name: Mapped[str | None] = mapped_column(
        String(11), nullable=True,
        comment="Nom alphanumérique affiché dans les SMS (max 11 chars)"
    )
    activity_sector: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Secteur d'activité du coach (fitness, yoga, crossfit…)"
    )
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="coach_profile")  # type: ignore[name-defined]
    specialties: Mapped[list["CoachSpecialty"]] = relationship("CoachSpecialty", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    certifications: Mapped[list["CoachCertification"]] = relationship("CoachCertification", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    coach_gyms: Mapped[list["CoachGym"]] = relationship("CoachGym", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    pricing: Mapped[list["CoachPricing"]] = relationship("CoachPricing", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    work_schedule: Mapped[list["CoachWorkSchedule"]] = relationship("CoachWorkSchedule", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    availability: Mapped[list["CoachAvailability"]] = relationship("CoachAvailability", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
    cancellation_policy: Mapped["CancellationPolicy | None"] = relationship("CancellationPolicy", back_populates="coach", uselist=False, cascade="all, delete-orphan")  # type: ignore[name-defined]
    cancellation_templates: Mapped[list["CancellationMessageTemplate"]] = relationship("CancellationMessageTemplate", back_populates="coach", cascade="all, delete-orphan")  # type: ignore[name-defined]
