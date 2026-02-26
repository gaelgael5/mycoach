"""Phase 2 — réservations, file d'attente, push tokens, SMS.

Revision ID: 003_phase2
Revises: 002_phase1
Create Date: 2026-02-26

Tables créées (B2-01 → B2-06, B2-27, B2-28) :
  client_questionnaires, client_gyms, coaching_requests,
  bookings, waitlist_entries, push_tokens, sms_logs
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "003_phase2"
down_revision = "002_phase1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── B2-01 : client_questionnaires ─────────────────────────────────────────
    op.create_table(
        "client_questionnaires",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal", sa.Text, nullable=True),
        sa.Column("level", sa.Text, nullable=True),
        sa.Column("frequency_per_week", sa.SmallInteger, nullable=True),
        sa.Column("session_duration_min", sa.SmallInteger, nullable=True),
        sa.Column("equipment", JSONB, nullable=False, server_default="[]"),
        sa.Column("target_zones", JSONB, nullable=False, server_default="[]"),
        sa.Column("injuries", sa.Text, nullable=True),  # chiffré applicativement
        sa.Column("injury_zones", JSONB, nullable=False, server_default="[]"),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("client_id", name="uq_client_questionnaires_client"),
    )

    # ── B2-02 : client_gyms (M-M) ─────────────────────────────────────────────
    op.create_table(
        "client_gyms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gym_id", UUID(as_uuid=True), sa.ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("client_id", "gym_id", name="uq_client_gyms"),
    )
    op.create_index("ix_client_gyms_client_id", "client_gyms", ["client_id"])

    # ── B2-03 : coaching_requests ─────────────────────────────────────────────
    op.create_table(
        "coaching_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("client_message", sa.Text, nullable=True),
        sa.Column("coach_message", sa.Text, nullable=True),
        sa.Column("discovery_slot", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_coaching_requests_client_id", "coaching_requests", ["client_id"])
    op.create_index("ix_coaching_requests_coach_id", "coaching_requests", ["coach_id"])

    # ── B2-04 : bookings ──────────────────────────────────────────────────────
    op.create_table(
        "bookings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("pricing_id", UUID(as_uuid=True), sa.ForeignKey("coach_pricing.id", ondelete="SET NULL"), nullable=True),
        sa.Column("package_id", UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("gym_id", UUID(as_uuid=True), sa.ForeignKey("gyms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scheduled_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("duration_min", sa.SmallInteger, nullable=False, server_default="60"),
        sa.Column("status", sa.String(40), nullable=False, server_default="pending_coach_validation"),
        sa.Column("price_cents", sa.Integer, nullable=True),
        sa.Column("client_message", sa.Text, nullable=True),
        sa.Column("coach_cancel_reason", sa.Text, nullable=True),
        sa.Column("late_cancel_waived", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("confirmed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("done_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_bookings_client_id", "bookings", ["client_id"])
    op.create_index("ix_bookings_coach_id", "bookings", ["coach_id"])
    op.create_index("ix_bookings_scheduled_at", "bookings", ["scheduled_at"])
    op.create_index("ix_bookings_status", "bookings", ["status"])

    # ── B2-05 : waitlist_entries ──────────────────────────────────────────────
    op.create_table(
        "waitlist_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot_datetime", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="waiting"),
        sa.Column("notified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_waitlist_coach_slot", "waitlist_entries", ["coach_id", "slot_datetime"])
    op.create_index("ix_waitlist_client_id", "waitlist_entries", ["client_id"])

    # ── B2-06 : push_tokens ───────────────────────────────────────────────────
    op.create_table(
        "push_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("platform", sa.String(10), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_push_tokens_user_id", "push_tokens", ["user_id"])

    # ── B2-27/B2-28 : sms_logs ────────────────────────────────────────────────
    op.create_table(
        "sms_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("coach_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("client_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("template_id", UUID(as_uuid=True), sa.ForeignKey("cancellation_message_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recipient_phone", sa.String(20), nullable=False),
        sa.Column("message_body", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("provider_message_id", sa.String(100), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_sms_logs_coach_id", "sms_logs", ["coach_id"])
    op.create_index("ix_sms_logs_status", "sms_logs", ["status"])


def downgrade() -> None:
    op.drop_table("sms_logs")
    op.drop_table("push_tokens")
    op.drop_table("waitlist_entries")
    op.drop_table("bookings")
    op.drop_table("coaching_requests")
    op.drop_table("client_gyms")
    op.drop_table("client_questionnaires")
