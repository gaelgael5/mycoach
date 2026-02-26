"""Phase 0 — Tables d'authentification

Crée : users, api_keys, email_verification_tokens, password_reset_tokens
Extensions : uuid-ossp, unaccent, pg_trgm (requises dans init-db.sql)

Revision ID: 001_phase0_auth
Revises:
Create Date: 2026-02-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001_phase0_auth"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # TABLE : users
    # Champs PII chiffrés Fernet → taille SQL = plaintext_max * 2 + 100
    #   first_name(150) → VARCHAR(400)
    #   last_name(150)  → VARCHAR(400)
    #   email(255)      → VARCHAR(610)
    #   phone(20)       → VARCHAR(140)
    #   google_sub(255) → VARCHAR(610)
    # Colonnes de lookup plain (non-PII) :
    #   email_hash    → CHAR(64)      SHA-256 hex, unique, index
    #   search_token  → VARCHAR(300)  unaccent+lower(prénom + nom), index GIN
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="unverified"),
        # PII chiffrés
        sa.Column("first_name", sa.String(400), nullable=False),
        sa.Column("last_name", sa.String(400), nullable=False),
        sa.Column("email", sa.String(610), nullable=False),
        sa.Column("phone", sa.String(140), nullable=True),
        sa.Column("google_sub", sa.String(610), nullable=True),
        # Lookup / recherche (plain)
        sa.Column("email_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("search_token", sa.String(300), nullable=False, server_default=""),
        # Auth
        sa.Column("password_hash", sa.String(255), nullable=True),
        # Profil
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="fr-FR"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Europe/Paris"),
        sa.Column("country", sa.String(2), nullable=False, server_default="FR"),
        sa.Column("profile_completion_pct", sa.SmallInteger, nullable=False, server_default="0"),
        # Timestamps
        sa.Column("email_verified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deletion_requested_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Index unique sur email_hash (lookup O(1))
    op.create_index("ix_users_email_hash", "users", ["email_hash"], unique=True)

    # Index GIN trigram sur search_token (fulltext sur noms, insensible aux accents)
    # Requiert l'extension pg_trgm (activée dans docker/init-db.sql)
    op.execute(
        "CREATE INDEX ix_users_search_token_gin ON users "
        "USING gin (search_token gin_trgm_ops)"
    )

    # ------------------------------------------------------------------
    # TABLE : api_keys
    # ------------------------------------------------------------------
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("device_label", sa.String(100), nullable=True),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)

    # ------------------------------------------------------------------
    # TABLE : email_verification_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_email_tokens_user_id", "email_verification_tokens", ["user_id"])
    op.create_index(
        "ix_email_tokens_hash", "email_verification_tokens", ["token_hash"], unique=True
    )

    # ------------------------------------------------------------------
    # TABLE : password_reset_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index(
        "ix_reset_tokens_hash", "password_reset_tokens", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_table("api_keys")
    op.execute("DROP INDEX IF EXISTS ix_users_search_token_gin")
    op.drop_index("ix_users_email_hash", table_name="users")
    op.drop_table("users")
