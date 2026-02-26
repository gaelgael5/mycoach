"""Modèle CoachingRelation — B1-10."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Statuts valides
RELATION_STATUSES = ["pending", "discovery", "active", "paused", "ended"]


class CoachingRelation(Base):
    """Relation coach ↔ client.

    Un client peut avoir plusieurs coachs simultanément (multi-coach).
    Contrainte UNIQUE (coach_id, client_id) → une seule relation par paire.

    status:
    - pending   → demande envoyée, en attente du coach
    - discovery → séance découverte en cours
    - active    → suivi actif en cours
    - paused    → suivi suspendu temporairement
    - ended     → relation terminée
    """

    __tablename__ = "coaching_relations"
    __table_args__ = (
        UniqueConstraint("coach_id", "client_id", name="uq_coaching_relation"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
