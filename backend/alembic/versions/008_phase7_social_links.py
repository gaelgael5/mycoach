"""Phase 7 — Table user_social_links (liens réseaux sociaux).

Deux types :
  - Standard  : platform slug connu, unique par (user_id, platform) via index partiel
  - Custom    : platform IS NULL, label requis, plusieurs par user, max 20 total

Revision ID: 008_phase7_social_links
Revises: 007_phase6
Create Date: 2026-02-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

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
        # NULL = lien custom ; non-NULL = plateforme standard (instagram, tiktok…)
        sa.Column("platform", sa.String(50), nullable=True),
        # Libellé affiché — obligatoire si platform IS NULL
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("url", sa.Text, nullable=False),
        # 'public' | 'coaches_only'
        sa.Column("visibility", sa.String(20), nullable=False, server_default="public"),
        # Ordre d'affichage
        sa.Column("position", sa.SmallInteger, nullable=False, server_default="0"),
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
    # Index standard sur user_id (pour les requêtes)
    op.create_index(
        "ix_user_social_links_user_id",
        "user_social_links",
        ["user_id"],
    )
    # Index partiel unique : (user_id, platform) WHERE platform IS NOT NULL
    # Permet l'UPSERT pour les plateformes standard, autorise plusieurs custom (platform=NULL)
    op.create_index(
        "uq_user_social_links_user_platform",
        "user_social_links",
        ["user_id", "platform"],
        unique=True,
        postgresql_where=sa.text("platform IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_user_social_links_user_platform", table_name="user_social_links")
    op.drop_index("ix_user_social_links_user_id", table_name="user_social_links")
    op.drop_table("user_social_links")
