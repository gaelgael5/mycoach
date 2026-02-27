"""Phase 9 — User profile fields: gender, birth_year, phone_verified_at, phone_hash.
   Table phone_verification_tokens.

Revision ID: 012_phase9_user_profile_fields
Revises: 011_phase9_enrollment_tokens
Create Date: 2026-02-27
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "012_phase9_user_profile_fields"
down_revision = "011_phase9_enrollment_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # Nouveaux champs sur la table users
    # -----------------------------------------------------------------------
    op.add_column("users", sa.Column("gender", sa.String(10), nullable=True))
    op.add_column("users", sa.Column("birth_year", sa.SmallInteger(), nullable=True))
    op.add_column("users", sa.Column("phone_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("phone_hash", sa.String(64), nullable=True))
    op.create_index("ix_users_phone_hash", "users", ["phone_hash"], unique=False)

    # -----------------------------------------------------------------------
    # Table phone_verification_tokens
    # -----------------------------------------------------------------------
    op.create_table(
        "phone_verification_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "attempts_count",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_phone_verification_tokens_user_id",
        "phone_verification_tokens",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_phone_verification_tokens_user_id", table_name="phone_verification_tokens")
    op.drop_table("phone_verification_tokens")
    op.drop_index("ix_users_phone_hash", table_name="users")
    op.drop_column("users", "phone_hash")
    op.drop_column("users", "phone_verified_at")
    op.drop_column("users", "birth_year")
    op.drop_column("users", "gender")
