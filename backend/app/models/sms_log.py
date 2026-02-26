"""Modèle SmsLog — B2-27."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

SMS_STATUSES = ["pending", "sent", "failed"]


class SmsLog(Base):
    """Journal d'envoi de SMS (Twilio ou autre provider).

    recipient_phone masqué dans les logs (stocké en clair pour audit coach).
    """

    __tablename__ = "sms_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cancellation_message_templates.id", ondelete="SET NULL"),
        nullable=True
    )
    recipient_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Numéro destinataire E.164"
    )
    message_body: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Corps du SMS envoyé (résolu)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="pending | sent | failed"
    )
    provider_message_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="ID message renvoyé par le provider (ex: Twilio SID)"
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Message d'erreur provider si status=failed"
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    client: Mapped["User | None"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
    template: Mapped["CancellationMessageTemplate | None"] = relationship(  # type: ignore[name-defined]
        "CancellationMessageTemplate"
    )
