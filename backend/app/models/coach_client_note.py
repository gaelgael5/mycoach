"""Modèle CoachClientNote — B1-11."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.core.encrypted_type import EncryptedString


class CoachClientNote(Base):
    """Notes confidentielles du coach sur un client (1-1 par paire coach/client).

    content est chiffré au repos (notes potentiellement sensibles).
    """

    __tablename__ = "coach_client_notes"
    __table_args__ = (
        UniqueConstraint("coach_id", "client_id", name="uq_coach_client_note"),
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
    content: Mapped[str | None] = mapped_column(
        EncryptedString, nullable=True,
        comment="Notes confidentielles chiffrées (Fernet FIELD_ENCRYPTION_KEY)"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
