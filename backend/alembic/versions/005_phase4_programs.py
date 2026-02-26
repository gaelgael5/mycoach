"""Phase 4 — Programmes d'entraînement, vidéos.

Revision ID: 005_phase4
Revises: 004_phase3
Create Date: 2026-02-26
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "005_phase4"
down_revision = "004_phase3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── workout_plans ──────────────────────────────────────────────────────────
    op.create_table(
        "workout_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("duration_weeks", sa.Integer, nullable=False, server_default="4"),
        sa.Column("level", sa.String(20), nullable=False, server_default="beginner"),
        sa.Column("goal", sa.String(30), nullable=False, server_default="well_being"),
        sa.Column(
            "created_by_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("is_ai_generated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("archived", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_workout_plans_created_by", "workout_plans", ["created_by_id"])

    # ── plan_assignments ───────────────────────────────────────────────────────
    op.create_table(
        "plan_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("mode", sa.String(20), nullable=False, server_default="replace_ai"),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_plan_assignments_client_id", "plan_assignments", ["client_id"])
    op.create_index("ix_plan_assignments_plan_id", "plan_assignments", ["plan_id"])

    # ── planned_sessions ───────────────────────────────────────────────────────
    op.create_table(
        "planned_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column("session_name", sa.String(100), nullable=False),
        sa.Column("estimated_duration_min", sa.Integer, nullable=True),
        sa.Column("rest_seconds", sa.Integer, nullable=False, server_default="90"),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index("ix_planned_sessions_plan_id", "planned_sessions", ["plan_id"])

    # ── planned_exercises ──────────────────────────────────────────────────────
    op.create_table(
        "planned_exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("planned_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("planned_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_type_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("exercise_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("target_sets", sa.Integer, nullable=False, server_default="3"),
        sa.Column("target_reps", sa.Integer, nullable=False, server_default="10"),
        sa.Column("target_weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index(
        "ix_planned_exercises_session_id", "planned_exercises", ["planned_session_id"]
    )

    # ── exercise_videos ────────────────────────────────────────────────────────
    op.create_table(
        "exercise_videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exercise_type_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("exercise_types.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("video_url", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("generated_prompt", sa.Text, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_by_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("exercise_videos")
    op.drop_table("planned_exercises")
    op.drop_table("planned_sessions")
    op.drop_table("plan_assignments")
    op.drop_table("workout_plans")
