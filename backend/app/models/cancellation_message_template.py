"""Modèle CancellationMessageTemplate — B1-29."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Variables autorisées dans les templates
TEMPLATE_VARIABLES = ["{prénom}", "{date}", "{heure}", "{coach}"]

# Template par défaut créé automatiquement à la création du profil coach
DEFAULT_TEMPLATE_TITLE = "Maladie"
DEFAULT_TEMPLATE_BODY = (
    "Bonjour {prénom},\n\n"
    "Je suis dans l'obligation d'annuler notre séance du {date} à {heure} "
    "en raison d'un problème de santé.\n\n"
    "Je vous recontacte très prochainement pour replanifier.\n\n"
    "Cordialement,\n{coach}"
)


class CancellationMessageTemplate(Base):
    """Template de message d'annulation du coach.

    Contrainte : max 5 templates par coach (enforced au niveau service).
    Variables supportées dans body : {prénom}, {date}, {heure}, {coach}.
    position : ordre d'affichage (1-5), unique par coach.
    """

    __tablename__ = "cancellation_message_templates"
    __table_args__ = (
        CheckConstraint("position >= 1 AND position <= 5", name="ck_template_position_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(40), nullable=False,
        comment="Titre du template, ex : 'Maladie'"
    )
    body: Mapped[str] = mapped_column(
        String(300), nullable=False,
        comment="Corps du message — max 300 chars (limite SMS)"
    )
    variables_used: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list,
        comment="Liste des variables détectées dans body : ['{prénom}', '{date}', ...]"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Le template 'Maladie' créé automatiquement"
    )
    position: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="Ordre d'affichage (1-5)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="cancellation_templates")  # type: ignore[name-defined]
