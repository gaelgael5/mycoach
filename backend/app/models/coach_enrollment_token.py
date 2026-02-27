"""Modèle CoachEnrollmentToken — liens d'enrôlement pour associer automatiquement un client à un coach."""
import secrets
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachEnrollmentToken(Base):
    __tablename__ = "coach_enrollment_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True,
        default=lambda: secrets.token_urlsafe(48)
    )
    # Libellé optionnel ex: "Groupe yoga janvier", "Clients VIP"
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # None = illimité
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uses_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    coach: Mapped["User"] = relationship("User", back_populates="enrollment_tokens")  # type: ignore[name-defined]
