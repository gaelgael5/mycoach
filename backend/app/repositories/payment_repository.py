"""Repository paiements & forfaits — B1-22."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.package import Package
from app.models.payment import Payment


# ── Forfaits (Packages) ───────────────────────────────────────────────────────

async def create_package(
    db: AsyncSession,
    client_id: uuid.UUID,
    coach_id: uuid.UUID,
    **kwargs: Any,
) -> Package:
    pkg = Package(
        id=uuid.uuid4(),
        client_id=client_id,
        coach_id=coach_id,
        **kwargs,
    )
    db.add(pkg)
    await db.flush()
    return pkg


async def get_package_by_id(
    db: AsyncSession, package_id: uuid.UUID
) -> Package | None:
    q = select(Package).where(Package.id == package_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def get_active_package(
    db: AsyncSession, client_id: uuid.UUID, coach_id: uuid.UUID
) -> Package | None:
    """Retourne le forfait actif (sessions_remaining > 0) le plus récent."""
    q = (
        select(Package)
        .where(
            Package.client_id == client_id,
            Package.coach_id == coach_id,
            Package.status == "active",
            Package.sessions_remaining > 0,
        )
        .order_by(Package.created_at.desc())
        .limit(1)
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def deduct_session(db: AsyncSession, package: Package) -> Package:
    """Décrémente sessions_remaining et met à jour le statut si épuisé."""
    if package.sessions_remaining <= 0:
        raise ValueError("Le forfait est déjà épuisé")
    package.sessions_remaining -= 1
    if package.sessions_remaining == 0:
        package.status = "exhausted"
    await db.flush()
    return package


async def mark_alert_sent(db: AsyncSession, package: Package) -> Package:
    package.alert_sent = True
    await db.flush()
    return package


async def get_history(
    db: AsyncSession,
    client_id: uuid.UUID,
    coach_id: uuid.UUID,
    *,
    offset: int = 0,
    limit: int = 50,
) -> list[Package]:
    q = (
        select(Package)
        .where(Package.client_id == client_id, Package.coach_id == coach_id)
        .order_by(Package.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def count_remaining(
    db: AsyncSession, client_id: uuid.UUID, coach_id: uuid.UUID
) -> int:
    """Nombre total de séances restantes dans les forfaits actifs."""
    q = select(func.coalesce(func.sum(Package.sessions_remaining), 0)).where(
        Package.client_id == client_id,
        Package.coach_id == coach_id,
        Package.status == "active",
    )
    result = await db.execute(q)
    return int(result.scalar_one())


# ── Paiements ──────────────────────────────────────────────────────────────────

async def record_payment(
    db: AsyncSession,
    coach_id: uuid.UUID,
    client_id: uuid.UUID,
    **kwargs: Any,
) -> Payment:
    pmt = Payment(
        id=uuid.uuid4(),
        coach_id=coach_id,
        client_id=client_id,
        **kwargs,
    )
    db.add(pmt)
    await db.flush()
    return pmt


async def get_payment_by_id(
    db: AsyncSession, payment_id: uuid.UUID
) -> Payment | None:
    q = select(Payment).where(Payment.id == payment_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def get_payment_history(
    db: AsyncSession,
    client_id: uuid.UUID,
    coach_id: uuid.UUID,
    *,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Payment], int]:
    base = select(Payment).where(
        Payment.client_id == client_id, Payment.coach_id == coach_id
    )
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar_one()
    items = list(
        (
            await db.execute(
                base.order_by(Payment.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
    )
    return items, total


async def count_done_sessions(
    db: AsyncSession, client_id: uuid.UUID, coach_id: uuid.UUID
) -> int:
    """Nombre de séances dont la consommation de forfait a été décomptée."""
    from app.models.package import Package
    q = select(
        func.coalesce(
            func.sum(Package.sessions_total - Package.sessions_remaining), 0
        )
    ).where(Package.client_id == client_id, Package.coach_id == coach_id)
    result = await db.execute(q)
    return int(result.scalar_one())
