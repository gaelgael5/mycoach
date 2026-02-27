"""Phase 7 — Table user_social_links (liens réseaux sociaux).

Revision ID: 008_phase7_social_links
Revises: 007_phase6
Create Date: 2026-02-27

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision = "008_phase7_social_links"
down_revision = "007_phase6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_social_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
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
        sa.UniqueConstraint("user_id", "platform", name="uq_user_social_links_user_platform"),
    )
    op.create_index(
        "ix_user_social_links_user_id",
        "user_social_links",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_user_social_links_user_id", table_name="user_social_links")
    op.drop_table("user_social_links")
