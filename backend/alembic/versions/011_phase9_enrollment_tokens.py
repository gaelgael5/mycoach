"""Phase 9 — Liens d'enrôlement coach.

Revision ID: 011_phase9_enrollment_tokens
Revises: 010_phase8_feedback_health
Create Date: 2026-02-27
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "011_phase9_enrollment_tokens"
down_revision = "010_phase8_feedback_health"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coach_enrollment_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "coach_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("uses_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_coach_enrollment_tokens_token",
        "coach_enrollment_tokens",
        ["token"],
        unique=True,
    )
    op.create_index(
        "ix_coach_enrollment_tokens_coach_id",
        "coach_enrollment_tokens",
        ["coach_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_coach_enrollment_tokens_token", table_name="coach_enrollment_tokens")
    op.drop_index("ix_coach_enrollment_tokens_coach_id", table_name="coach_enrollment_tokens")
    op.drop_table("coach_enrollment_tokens")
