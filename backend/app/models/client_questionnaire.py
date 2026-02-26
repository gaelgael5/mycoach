"""Modèle ClientQuestionnaire — B2-01."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.encrypted_type import EncryptedString


class ClientQuestionnaire(Base):
    """Questionnaire de condition physique du client (1-1 avec client_profiles).

    Données de santé : injuries stocké chiffré (EncryptedString).
    """

    __tablename__ = "client_questionnaires"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="1-1 avec users"
    )
    # Objectifs et niveau
    goal: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Objectif principal (libre ou enum)"
    )
    level: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Niveau estimé"
    )
    frequency_per_week: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True, comment="Fréquence souhaitée en séances/semaine"
    )
    session_duration_min: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True, comment="Durée souhaitée par séance"
    )
    # Jsonb arrays
    equipment: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list,
        comment='["haltères","barre","machine",...] — équipement disponible'
    )
    target_zones: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list,
        comment='["dos","jambes","abdos",...] — zones à cibler'
    )
    # Santé — chiffré au repos
    injuries: Mapped[str | None] = mapped_column(
        EncryptedString, nullable=True,
        comment="Blessures / contre-indications médicales — chiffré FIELD_ENCRYPTION_KEY"
    )
    injury_zones: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list,
        comment='["épaule gauche","genou droit",...] — zones à ménager'
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
