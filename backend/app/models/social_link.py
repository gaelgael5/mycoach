"""Modèle SocialLink — liens réseaux sociaux des utilisateurs (Phase 7).

Deux types de liens :
  - Standard  : platform est un slug connu (instagram, tiktok…), 1 seul par user
  - Custom    : platform IS NULL, label requis, plusieurs autorisés, max 20 total

Visibilité par lien :
  - 'public'        : visible par tous
  - 'coaches_only'  : visible uniquement par les coachs avec relation active
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger, String, Text, func, text
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
    # NULL = lien custom ; slug connu = lien standard (1 par user, upsert)
    platform: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    # Libellé affiché — requis si platform IS NULL, facultatif sinon
    label: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    # Visibilité : 'public' | 'coaches_only'
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default="public"
    )
    # Ordre d'affichage (tri croissant)
    position: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # Index partiel : unicité (user_id, platform) UNIQUEMENT pour les plateformes standard
    __table_args__ = (
        Index(
            "uq_user_social_links_user_platform",
            "user_id",
            "platform",
            unique=True,
            postgresql_where=text("platform IS NOT NULL"),
        ),
    )

    # Relation vers User
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="social_links"
    )

    def __repr__(self) -> str:
        kind = self.platform or f"custom({self.label})"
        return f"<SocialLink user_id={self.user_id} {kind}>"
