"""Modèle SocialLink — liens réseaux sociaux des utilisateurs (Phase 7)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SocialLink(Base):
    __tablename__ = "user_social_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # instagram | tiktok | youtube | linkedin | x | facebook | strava | website
    url: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "platform", name="uq_user_social_links_user_platform"),
    )

    # Relation vers User
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="social_links"
    )

    def __repr__(self) -> str:
        return f"<SocialLink user_id={self.user_id} platform={self.platform}>"
