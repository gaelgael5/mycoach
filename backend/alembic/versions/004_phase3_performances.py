"""Phase 3 — Exercices, machines, performances.

Revision ID: 004_phase3
Revises: 003_phase2
Create Date: 2026-02-26
"""

from __future__ import annotations

import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "004_phase3"
down_revision = "003_phase2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── exercise_types ──────────────────────────────────────────────────────────
    op.create_table(
        "exercise_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_key", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.String(30), nullable=False, server_default="strength"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="intermediate"),
        sa.Column("video_url", sa.Text, nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("instructions", postgresql.JSONB, nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
    )

    # ── exercise_type_muscles ──────────────────────────────────────────────────
    op.create_table(
        "exercise_type_muscles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "exercise_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_types.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("muscle_group", sa.String(50), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="primary"),
    )
    op.create_index(
        "ix_exercise_type_muscles_exercise_type_id",
        "exercise_type_muscles",
        ["exercise_type_id"],
    )

    # ── machines ───────────────────────────────────────────────────────────────
    op.create_table(
        "machines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type_key", sa.String(50), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("photo_url", sa.Text, nullable=True),
        sa.Column("qr_code_hash", sa.String(64), unique=True, nullable=True),
        sa.Column("validated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "submitted_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "validated_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # ── machine_exercises ──────────────────────────────────────────────────────
    op.create_table(
        "machine_exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "machine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("machines.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exercise_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_types.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_machine_exercises_machine_id",
        "machine_exercises",
        ["machine_id"],
    )

    # ── performance_sessions ───────────────────────────────────────────────────
    op.create_table(
        "performance_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("session_type", sa.String(20), nullable=False, server_default="solo_free"),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "entered_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "gym_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("gyms.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("session_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_min", sa.Integer, nullable=True),
        sa.Column("feeling", sa.Integer, nullable=True),
        sa.Column("strava_activity_id", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_performance_sessions_user_id",
        "performance_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_performance_sessions_session_date",
        "performance_sessions",
        ["session_date"],
    )

    # ── exercise_sets ──────────────────────────────────────────────────────────
    op.create_table(
        "exercise_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("performance_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exercise_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "machine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("machines.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("set_order", sa.Integer, nullable=False, server_default="1"),
        sa.Column("sets_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("reps", sa.Integer, nullable=True),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_pr", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_exercise_sets_session_id", "exercise_sets", ["session_id"])
    # Index partiel pour les PRs (décision archi)
    op.create_index(
        "ix_exercise_sets_is_pr",
        "exercise_sets",
        ["exercise_type_id"],
        postgresql_where=sa.text("is_pr = TRUE"),
    )


def downgrade() -> None:
    op.drop_table("exercise_sets")
    op.drop_table("performance_sessions")
    op.drop_table("machine_exercises")
    op.drop_table("machines")
    op.drop_table("exercise_type_muscles")
    op.drop_table("exercise_types")
