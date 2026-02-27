"""
Modèle User — compte utilisateur commun à tous les rôles.

Champs PII chiffrés via EncryptedString (FIELD_ENCRYPTION_KEY) :
  first_name, last_name, email, phone, google_sub

Colonnes de lookup/recherche stockées en clair (non-PII) :
  email_hash   → SHA-256(lower(email)) — lookup exact O(1)
  search_token → unaccent+lower(prénom + nom) — recherche fulltext GIN pg_trgm
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.encrypted_type import EncryptedString
from app.core.encryption import hash_for_lookup, normalize_for_search
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # -----------------------------------------------------------------------
    # Identifiant & métadonnées système (non-PII, non chiffrés)
    # -----------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # coach | client | admin

    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="unverified"
    )  # unverified | active | suspended | deletion_pending

    # -----------------------------------------------------------------------
    # Champs PII — chiffrés via EncryptedString (FIELD_ENCRYPTION_KEY)
    # -----------------------------------------------------------------------
    first_name: Mapped[str] = mapped_column(EncryptedString(150), nullable=False)
    last_name: Mapped[str] = mapped_column(EncryptedString(150), nullable=False)
    email: Mapped[str] = mapped_column(EncryptedString(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(
        EncryptedString(20), nullable=True
    )  # E.164 : +33612345678
    google_sub: Mapped[str | None] = mapped_column(
        EncryptedString(255), nullable=True
    )  # identifiant Google OAuth2

    # -----------------------------------------------------------------------
    # Colonnes de lookup/recherche — stockées en clair, non-PII
    # -----------------------------------------------------------------------
    # email_hash : SHA-256(lower(email)) → WHERE email_hash = ? (index unique)
    email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    # search_token : unaccent+lower(prénom + ' ' + nom) → ILIKE '%query%' (GIN)
    # Jamais retourné dans les réponses API — uniquement pour les WHERE de recherche
    search_token: Mapped[str] = mapped_column(
        String(300), nullable=False, default=""
    )

    # -----------------------------------------------------------------------
    # Auth (non-PII)
    # -----------------------------------------------------------------------
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # bcrypt — None si compte Google-only

    # -----------------------------------------------------------------------
    # Profil & préférences (non-PII)
    # -----------------------------------------------------------------------
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    locale: Mapped[str] = mapped_column(
        String(10), nullable=False, default="fr-FR"
    )  # BCP 47 : fr-FR, en-US, es-ES...
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Europe/Paris"
    )  # IANA : Europe/Paris, America/New_York...
    country: Mapped[str] = mapped_column(
        String(2), nullable=False, default="FR"
    )  # ISO 3166-1 alpha-2 : FR, BE, US...

    profile_completion_pct: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )  # 0–100

    # -----------------------------------------------------------------------
    # Identité & démographie (non-PII, non chiffrés)
    # -----------------------------------------------------------------------
    gender: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # 'male' | 'female' | 'other'

    birth_year: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )  # Année de naissance ex: 1990

    # -----------------------------------------------------------------------
    # Téléphone — vérification
    # -----------------------------------------------------------------------
    phone_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Hash SHA-256 du numéro de téléphone (lookup, non-PII)
    phone_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    # -----------------------------------------------------------------------
    # Timestamps (non-PII)
    # -----------------------------------------------------------------------
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Suppression effective J+30
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # -----------------------------------------------------------------------
    # Index GIN pg_trgm sur search_token
    # -----------------------------------------------------------------------
    __table_args__ = (
        Index(
            "ix_users_search_token_gin",
            "search_token",
            postgresql_using="gin",
            postgresql_ops={"search_token": "gin_trgm_ops"},
        ),
    )

    # -----------------------------------------------------------------------
    # Validators — synchronisation automatique des colonnes de lookup
    # -----------------------------------------------------------------------

    @validates("email")
    def _sync_email_hash(self, key: str, value: str) -> str:
        """
        Synchronise email_hash à chaque modification de email.
        SQLAlchemy appelle @validates avant process_bind_param (EncryptedString),
        donc value est ici la valeur en clair.
        """
        if value:
            self.email_hash = hash_for_lookup(value)
        return value

    @validates("first_name", "last_name")
    def _sync_search_token(self, key: str, value: str) -> str:
        """
        Reconstruit search_token à chaque changement de prénom ou de nom.
        Le token est irréversible et non-PII.
        """
        current_first = getattr(self, "first_name", "") or ""
        current_last = getattr(self, "last_name", "") or ""
        if key == "first_name":
            self.search_token = normalize_for_search(f"{value} {current_last}")
        else:
            self.search_token = normalize_for_search(f"{current_first} {value}")
        return value

    @validates("phone")
    def _sync_phone_hash(self, key: str, value: str | None) -> str | None:
        """Synchronise phone_hash à chaque modification de phone."""
        if value:
            self.phone_hash = hash_for_lookup(value)
        else:
            self.phone_hash = None
        return value

    def __repr__(self) -> str:
        return f"<User id={self.id} role={self.role} status={self.status}>"

    # Relations Phase 1 (résolues par string après import complet dans models/__init__.py)
    coach_profile: Mapped["CoachProfile | None"] = relationship(  # type: ignore[name-defined]
        "CoachProfile", back_populates="user", uselist=False
    )
    client_profile: Mapped["ClientProfile | None"] = relationship(  # type: ignore[name-defined]
        "ClientProfile", back_populates="user", uselist=False
    )
    social_links: Mapped[list["SocialLink"]] = relationship(  # type: ignore[name-defined]
        "SocialLink", back_populates="user", cascade="all, delete-orphan"
    )

    # Phase 8 — Feedback & Santé
    feedbacks: Mapped[list["UserFeedback"]] = relationship(  # type: ignore[name-defined]
        "UserFeedback", back_populates="user"
    )
    health_logs: Mapped[list["HealthLog"]] = relationship(  # type: ignore[name-defined]
        "HealthLog", back_populates="user", cascade="all, delete-orphan"
    )

    # Phase 9 — Liens d'enrôlement coach
    enrollment_tokens: Mapped[list["CoachEnrollmentToken"]] = relationship(  # type: ignore[name-defined]
        "CoachEnrollmentToken", back_populates="coach", cascade="all, delete-orphan"
    )

    # Phase 9 — Vérification téléphone OTP
    phone_verification_tokens: Mapped[list["PhoneVerificationToken"]] = relationship(  # type: ignore[name-defined]
        "PhoneVerificationToken", back_populates="user", cascade="all, delete-orphan"
    )
