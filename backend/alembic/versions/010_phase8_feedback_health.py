"""Phase 8 — Feedback utilisateur + Paramètres de santé.

Revision ID: 010_phase8_feedback_health
Revises: 009_phase7_blocked_domains
Create Date: 2026-02-27
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "010_phase8_feedback_health"
down_revision = "009_phase7_blocked_domains"
branch_labels = None
depends_on = None

SEED_HEALTH_PARAMS = [
    {"slug": "weight_kg", "label": {"fr": "Poids", "en": "Weight"}, "unit": "kg", "data_type": "float", "category": "morphology", "position": 1},
    {"slug": "body_fat_pct", "label": {"fr": "% Masse grasse", "en": "Body Fat %"}, "unit": "%", "data_type": "float", "category": "morphology", "position": 2},
    {"slug": "muscle_mass_kg", "label": {"fr": "Masse musculaire", "en": "Muscle Mass"}, "unit": "kg", "data_type": "float", "category": "morphology", "position": 3},
    {"slug": "bmi", "label": {"fr": "IMC", "en": "BMI"}, "unit": None, "data_type": "float", "category": "morphology", "position": 4},
    {"slug": "resting_heart_rate_bpm", "label": {"fr": "FC au repos", "en": "Resting Heart Rate"}, "unit": "bpm", "data_type": "int", "category": "cardiovascular", "position": 5},
    {"slug": "blood_pressure_systolic", "label": {"fr": "Tension systolique", "en": "Systolic BP"}, "unit": "mmHg", "data_type": "int", "category": "cardiovascular", "position": 6},
    {"slug": "blood_pressure_diastolic", "label": {"fr": "Tension diastolique", "en": "Diastolic BP"}, "unit": "mmHg", "data_type": "int", "category": "cardiovascular", "position": 7},
    {"slug": "spo2_pct", "label": {"fr": "Saturation O₂", "en": "SpO₂"}, "unit": "%", "data_type": "float", "category": "cardiovascular", "position": 8},
    {"slug": "vo2max", "label": {"fr": "VO₂max", "en": "VO₂max"}, "unit": "mL/kg/min", "data_type": "float", "category": "fitness", "position": 9},
    {"slug": "sleep_hours", "label": {"fr": "Heures de sommeil", "en": "Sleep Hours"}, "unit": "h", "data_type": "float", "category": "sleep", "position": 10},
    {"slug": "sleep_quality", "label": {"fr": "Qualité du sommeil", "en": "Sleep Quality"}, "unit": "/10", "data_type": "int", "category": "sleep", "position": 11},
    {"slug": "stress_level", "label": {"fr": "Niveau de stress", "en": "Stress Level"}, "unit": "/10", "data_type": "int", "category": "other", "position": 12},
    {"slug": "water_intake_ml", "label": {"fr": "Hydratation", "en": "Water Intake"}, "unit": "mL", "data_type": "int", "category": "nutrition", "position": 13},
    {"slug": "steps_daily", "label": {"fr": "Pas quotidiens", "en": "Daily Steps"}, "unit": "pas", "data_type": "int", "category": "fitness", "position": 14},
]


def upgrade() -> None:
    # 1. user_feedback
    op.create_table(
        "user_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("app_version", sa.String(30), nullable=True),
        sa.Column("platform", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("admin_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 2. health_parameters
    op.create_table(
        "health_parameters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("slug", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("label", postgresql.JSONB, nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("data_type", sa.String(10), nullable=False, server_default="float"),
        sa.Column("category", sa.String(30), nullable=False, server_default="other"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("position", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 3. health_logs
    op.create_table(
        "health_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("parameter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("health_parameters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Numeric(10, 3), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 4. health_sharing_settings
    op.create_table(
        "health_sharing_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("coach_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parameter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("health_parameters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shared", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "coach_id", "parameter_id", name="uq_health_sharing_user_coach_param"),
    )

    # 5. Seed des paramètres de santé
    health_params_table = sa.table(
        "health_parameters",
        sa.column("id", postgresql.UUID),
        sa.column("slug", sa.String),
        sa.column("label", postgresql.JSONB),
        sa.column("unit", sa.String),
        sa.column("data_type", sa.String),
        sa.column("category", sa.String),
        sa.column("active", sa.Boolean),
        sa.column("position", sa.SmallInteger),
    )
    op.bulk_insert(
        health_params_table,
        [
            {
                "id": str(uuid.uuid4()),
                "slug": p["slug"],
                "label": p["label"],
                "unit": p["unit"],
                "data_type": p["data_type"],
                "category": p["category"],
                "active": True,
                "position": p["position"],
            }
            for p in SEED_HEALTH_PARAMS
        ],
    )


def downgrade() -> None:
    op.drop_table("health_sharing_settings")
    op.drop_table("health_logs")
    op.drop_table("health_parameters")
    op.drop_table("user_feedback")
