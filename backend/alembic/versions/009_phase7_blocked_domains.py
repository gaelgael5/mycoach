"""Phase 7 — Table blocked_email_domains + seed des domaines jetables connus.

Revision ID: 009_phase7_blocked_domains
Revises: 008_phase7_social_links
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "009_phase7_blocked_domains"
down_revision = "008_phase7_social_links"
branch_labels = None
depends_on = None

# Liste initiale de domaines jetables connus
SEED_DOMAINS = [
    "yopmail.com", "yopmail.fr", "cool.fr.nf", "jetable.fr.nf",
    "nospam.ze.tc", "nomail.xl.cx", "mega.zik.dj", "speed.1s.fr",
    "courriel.fr.nf", "moncourrier.fr.nf", "monemail.fr.nf",
    "monmail.fr.nf", "mailinator.com", "tempmail.com", "temp-mail.org",
    "guerrillamail.com", "guerrillamail.info", "guerrillamail.net",
    "guerrillamail.org", "guerrillamail.de", "guerrillamailblock.com",
    "grr.la", "spam4.me", "10minutemail.com", "10minutemail.net",
    "throwaway.email", "throwam.com", "trashmail.com", "trashmail.at",
    "trashmail.io", "trashmail.me", "trashmail.net", "trashmail.org",
    "sharklasers.com", "guerrillamail.biz", "filzmail.com",
    "maildrop.cc", "spamgourmet.com", "spamgourmet.net", "spamgourmet.org",
    "discard.email", "mailnull.com", "spamspot.com", "dispostable.com",
    "fakeinbox.com", "getnada.com", "mohmal.com", "mytemp.email",
    "tempr.email", "20minutemail.com", "airmail.cc", "mintemail.com",
    "spam4.me", "spamtrap.ro", "crazymailing.com", "mailforspam.com",
]

def upgrade() -> None:
    op.create_table(
        "blocked_email_domains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain", sa.String(100), nullable=False, unique=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_blocked_email_domains_domain", "blocked_email_domains", ["domain"], unique=True)

    # Seed initial
    now = datetime.now(timezone.utc)
    seen = set()
    rows = []
    for domain in SEED_DOMAINS:
        d = domain.lower().strip()
        if d not in seen:
            seen.add(d)
            rows.append({"id": str(uuid.uuid4()), "domain": d, "reason": "Service email jetable", "created_at": now})
    if rows:
        op.bulk_insert(
            sa.table("blocked_email_domains",
                sa.column("id", sa.String),
                sa.column("domain", sa.String),
                sa.column("reason", sa.Text),
                sa.column("created_at", sa.DateTime(timezone=True)),
            ),
            rows,
        )

def downgrade() -> None:
    op.drop_index("ix_blocked_email_domains_domain", table_name="blocked_email_domains")
    op.drop_table("blocked_email_domains")
