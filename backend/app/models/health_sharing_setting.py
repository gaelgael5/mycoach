"""Modèle HealthSharingSetting — préférences de partage santé par coach."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HealthSharingSetting(Base):
    """Préférence de partage d'un paramètre de santé avec un coach.

    Absence de ligne = partagé par défaut (opt-out model).
    shared=False = paramètre masqué pour ce coach.
    """

    __tablename__ = "health_sharing_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parameter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("health_parameters.id", ondelete="CASCADE"), nullable=False
    )
    shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "coach_id", "parameter_id",
            name="uq_health_sharing_user_coach_param",
        ),
    )
