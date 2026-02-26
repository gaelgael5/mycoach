"""
Modèle ApiKey — clé d'authentification par appareil.

La clé elle-même n'est JAMAIS stockée — uniquement son SHA-256 (key_hash).
Au moment de la création, la clé en clair est retournée une seule fois au client.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # SHA-256 de la clé en clair — jamais la clé elle-même
    key_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    device_label: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # ex: "Pixel 8 Pro", "iPhone 15"

    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relation (lazy='noload' pour éviter les N+1 dans les middlewares)
    user: Mapped["User"] = relationship("User", lazy="noload")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<ApiKey id={self.id} user_id={self.user_id} revoked={self.revoked}>"
