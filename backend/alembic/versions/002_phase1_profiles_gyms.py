"""Phase 1 — profils coach/client, gyms, tarifs, planning, templates annulation.

Revision ID: 002_phase1
Revises: 001_phase0_auth_tables
Create Date: 2026-02-26

Tables créées (B1-01 → B1-14, B1-29, B1-30) :
  gym_chains, gyms, coach_profiles, coach_specialties, coach_certifications,
  coach_gyms, coach_pricing, coach_work_schedule, coach_availability,
  cancellation_policies, coaching_relations, coach_client_notes,
  client_profiles, packages, payments, cancellation_message_templates
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "002_phase1"
down_revision = "001_phase0_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── B1-01 : gym_chains ────────────────────────────────────────────────────
    op.create_table(
        "gym_chains",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column("website", sa.Text, nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("uq_gym_chains_name", "gym_chains", ["name"], unique=True)
    op.create_index("uq_gym_chains_slug", "gym_chains", ["slug"], unique=True)

    # ── B1-02 : gyms ──────────────────────────────────────────────────────────
    op.create_table(
        "gyms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("chain_id", UUID(as_uuid=True), sa.ForeignKey("gym_chains.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website_url", sa.Text, nullable=True),
        sa.Column("open_24h", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("validated", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_gyms_chain_id", "gyms", ["chain_id"])
    op.create_index("ix_gyms_city", "gyms", ["city"])
    op.create_index("ix_gyms_country", "gyms", ["country"])

    # ── B1-03 : coach_profiles ────────────────────────────────────────────────
    op.create_table(
        "coach_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("session_duration_min", sa.SmallInteger, nullable=False, server_default="60"),
        sa.Column("discovery_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("discovery_free", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("discovery_price_cents", sa.Integer, nullable=True),
        sa.Column("booking_horizon_days", sa.SmallInteger, nullable=False, server_default="30"),
        sa.Column("sms_sender_name", sa.String(11), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("uq_coach_profiles_user_id", "coach_profiles", ["user_id"], unique=True)

    # ── B1-04 : coach_specialties ─────────────────────────────────────────────
    op.create_table(
        "coach_specialties",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("specialty", sa.String(50), nullable=False),
    )
    op.create_index("ix_coach_specialties_coach_id", "coach_specialties", ["coach_id"])

    # ── B1-05 : coach_certifications ──────────────────────────────────────────
    op.create_table(
        "coach_certifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("organization", sa.String(150), nullable=True),
        sa.Column("year", sa.SmallInteger, nullable=True),
        sa.Column("document_url", sa.Text, nullable=True),
        sa.Column("verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_coach_certifications_coach_id", "coach_certifications", ["coach_id"])

    # ── B1-06 : coach_gyms (M-M) ──────────────────────────────────────────────
    op.create_table(
        "coach_gyms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gym_id", UUID(as_uuid=True), sa.ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("coach_id", "gym_id", name="uq_coach_gyms"),
    )

    # ── B1-07 : coach_pricing ─────────────────────────────────────────────────
    op.create_table(
        "coach_pricing",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("session_count", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("price_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("validity_months", sa.SmallInteger, nullable=True),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_coach_pricing_coach_id", "coach_pricing", ["coach_id"])

    # ── B1-08 : coach_work_schedule ───────────────────────────────────────────
    op.create_table(
        "coach_work_schedule",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger, nullable=False),
        sa.Column("is_working_day", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("time_slots", JSONB, nullable=False, server_default="[]"),
        sa.UniqueConstraint("coach_id", "day_of_week", name="uq_work_schedule_coach_day"),
    )

    # ── B1-08b : coach_availability ───────────────────────────────────────────
    op.create_table(
        "coach_availability",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("max_slots", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("booking_horizon_days", sa.SmallInteger, nullable=False, server_default="30"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("ix_coach_availability_coach_id", "coach_availability", ["coach_id"])

    # ── B1-09 : cancellation_policies ────────────────────────────────────────
    op.create_table(
        "cancellation_policies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("threshold_hours", sa.SmallInteger, nullable=False, server_default="24"),
        sa.Column("mode", sa.String(10), nullable=False, server_default="auto"),
        sa.Column("noshow_is_due", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("client_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("coach_id", name="uq_cancellation_policies_coach"),
    )

    # ── B1-10 : coaching_relations ────────────────────────────────────────────
    op.create_table(
        "coaching_relations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("coach_id", "client_id", name="uq_coaching_relation"),
    )
    op.create_index("ix_coaching_relations_coach_id", "coaching_relations", ["coach_id"])
    op.create_index("ix_coaching_relations_client_id", "coaching_relations", ["client_id"])

    # ── B1-11 : coach_client_notes ────────────────────────────────────────────
    op.create_table(
        "coach_client_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=True),  # chiffré applicativement
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("coach_id", "client_id", name="uq_coach_client_note"),
    )

    # ── B1-12 : client_profiles ───────────────────────────────────────────────
    op.create_table(
        "client_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("birth_date", sa.Text, nullable=True),  # chiffré applicativement (ISO date)
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("height_cm", sa.SmallInteger, nullable=True),
        sa.Column("goal", sa.String(50), nullable=True),
        sa.Column("level", sa.String(20), nullable=True),
        sa.Column("weight_unit", sa.String(5), nullable=False, server_default="kg"),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_client_profiles_user_id"),
    )

    # ── B1-13 : packages ──────────────────────────────────────────────────────
    op.create_table(
        "packages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("pricing_id", UUID(as_uuid=True), sa.ForeignKey("coach_pricing.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("sessions_total", sa.SmallInteger, nullable=False),
        sa.Column("sessions_remaining", sa.SmallInteger, nullable=False),
        sa.Column("price_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("valid_until", sa.Date, nullable=True),
        sa.Column("alert_sent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_packages_client_id", "packages", ["client_id"])
    op.create_index("ix_packages_coach_id", "packages", ["coach_id"])
    op.create_index("ix_packages_status", "packages", ["status"])

    # ── B1-14 : payments ──────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("payment_method", sa.String(30), nullable=False, server_default="cash"),
        sa.Column("reference", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("paid_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("due_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_payments_coach_id", "payments", ["coach_id"])
    op.create_index("ix_payments_client_id", "payments", ["client_id"])
    op.create_index("ix_payments_package_id", "payments", ["package_id"])

    # ── B1-29/B1-30 : cancellation_message_templates ─────────────────────────
    op.create_table(
        "cancellation_message_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("coach_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(40), nullable=False),
        sa.Column("body", sa.String(300), nullable=False),
        sa.Column("variables_used", JSONB, nullable=False, server_default="[]"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("position", sa.SmallInteger, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("position >= 1 AND position <= 5", name="ck_template_position_range"),
    )
    op.create_index("ix_cancel_templates_coach_id", "cancellation_message_templates", ["coach_id"])


def downgrade() -> None:
    op.drop_table("cancellation_message_templates")
    op.drop_table("payments")
    op.drop_table("packages")
    op.drop_table("client_profiles")
    op.drop_table("coach_client_notes")
    op.drop_table("coaching_relations")
    op.drop_table("cancellation_policies")
    op.drop_table("coach_availability")
    op.drop_table("coach_work_schedule")
    op.drop_table("coach_pricing")
    op.drop_table("coach_gyms")
    op.drop_table("coach_certifications")
    op.drop_table("coach_specialties")
    op.drop_table("coach_profiles")
    op.drop_table("gyms")
    op.drop_table("gym_chains")
