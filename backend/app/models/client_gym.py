"""Modèle ClientGym — B2-02 (M-M : users ↔ gyms pour les clients)."""

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClientGym(Base):
    """Association many-to-many entre un client et ses salles fréquentées."""

    __tablename__ = "client_gyms"
    __table_args__ = (
        UniqueConstraint("client_id", "gym_id", name="uq_client_gyms"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
    gym: Mapped["Gym"] = relationship("Gym")  # type: ignore[name-defined]
