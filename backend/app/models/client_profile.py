"""Modèle ClientProfile — B1-12."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, SmallInteger, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.encrypted_type import EncryptedString

# Valeurs valides
GOAL_VALUES = [
    "lose_weight", "muscle_gain", "endurance",
    "well_being", "sport_perf", "rehabilitation", "other",
]
LEVEL_VALUES = ["beginner", "intermediate", "advanced"]


class ClientProfile(Base):
    """Profil d'un client (relation 1-1 avec users)."""

    __tablename__ = "client_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    # PII — date de naissance chiffrée, stockée comme chaîne ISO "YYYY-MM-DD"
    birth_date: Mapped[str | None] = mapped_column(
        EncryptedString, nullable=True,
        comment="Date de naissance ISO 8601 chiffrée (FIELD_ENCRYPTION_KEY)"
    )
    # Données de santé — Phase 4 ajoutera le chiffrement fin des mesures corporelles
    weight_kg: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Poids initial en kg"
    )
    height_cm: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True,
        comment="Taille en cm"
    )
    goal: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Objectif : " + " | ".join(GOAL_VALUES)
    )
    level: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="Niveau : " + " | ".join(LEVEL_VALUES)
    )
    weight_unit: Mapped[str] = mapped_column(
        String(5), nullable=False, default="kg",
        comment="kg | lb — préférence d'affichage"
    )
    country: Mapped[str | None] = mapped_column(
        String(2), nullable=True, comment="ISO 3166-1 alpha-2"
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

    user: Mapped["User"] = relationship("User", back_populates="client_profile")  # type: ignore[name-defined]
