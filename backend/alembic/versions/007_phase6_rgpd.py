"""Phase 6 — RGPD : consentements + champ deletion_pending sur users.

Revision ID: 007_phase6
Revises: 006_phase5
Create Date: 2026-02-26
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "007_phase6"
down_revision = "006_phase5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── consents — log immuable des consentements ──────────────────────────────
    op.create_table(
        "consents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("consent_type", sa.String(40), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("accepted", sa.Boolean, nullable=False),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent_hash", sa.String(64), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_consents_user_id", "consents", ["user_id"])
    op.create_index("ix_consents_type", "consents", ["consent_type"])

def downgrade() -> None:
    op.drop_table("consents")
