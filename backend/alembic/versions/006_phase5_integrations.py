"""Phase 5 — Intégrations OAuth (Strava, Google Calendar, Withings) + mesures corporelles.

Revision ID: 006_phase5
Revises: 005_phase4
Create Date: 2026-02-26
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "006_phase5"
down_revision = "005_phase4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── oauth_tokens ───────────────────────────────────────────────────────────
    op.create_table(
        "oauth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("access_token_enc", sa.Text, nullable=False),
        sa.Column("refresh_token_enc", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scope", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    # Index unique : un token par utilisateur × provider
    op.create_index(
        "uix_oauth_tokens_user_provider", "oauth_tokens",
        ["user_id", "provider"], unique=True,
    )

    # ── body_measurements ─────────────────────────────────────────────────────
    op.create_table(
        "body_measurements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("bmi", sa.Numeric(5, 2), nullable=True),
        sa.Column("fat_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("muscle_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("bone_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("water_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
    )
    op.create_index("ix_body_measurements_user_id", "body_measurements", ["user_id"])
    op.create_index(
        "ix_body_measurements_user_date", "body_measurements",
        ["user_id", "measured_at"],
    )


def downgrade() -> None:
    op.drop_table("body_measurements")
    op.drop_table("oauth_tokens")
