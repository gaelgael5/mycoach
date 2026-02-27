"""Repository — Domaines email bloqués."""
from __future__ import annotations
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.blocked_email_domain import BlockedEmailDomain

async def is_blocked(db: AsyncSession, domain: str) -> bool:
    """Retourne True si le domaine est dans la blocklist."""
    result = await db.execute(
        select(BlockedEmailDomain.id).where(BlockedEmailDomain.domain == domain.lower().strip())
    )
    return result.scalar_one_or_none() is not None

async def add(db: AsyncSession, domain: str, reason: str | None = None) -> BlockedEmailDomain:
    """Ajoute un domaine à la blocklist."""
    entry = BlockedEmailDomain(domain=domain.lower().strip(), reason=reason)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry

async def remove(db: AsyncSession, domain: str) -> bool:
    """Supprime un domaine. Retourne True si supprimé."""
    result = await db.execute(
        delete(BlockedEmailDomain)
        .where(BlockedEmailDomain.domain == domain.lower().strip())
        .returning(BlockedEmailDomain.id)
    )
    await db.flush()
    return result.scalar_one_or_none() is not None

async def list_all(db: AsyncSession) -> list[BlockedEmailDomain]:
    result = await db.execute(
        select(BlockedEmailDomain).order_by(BlockedEmailDomain.domain)
    )
    return list(result.scalars().all())
