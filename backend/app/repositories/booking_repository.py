"""Repository réservations — B2-11."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BOOKING_STATUSES


async def create(
    db: AsyncSession,
    client_id: uuid.UUID,
    coach_id: uuid.UUID,
    **kwargs: Any,
) -> Booking:
    booking = Booking(
        id=uuid.uuid4(),
        client_id=client_id,
        coach_id=coach_id,
        **kwargs,
    )
    db.add(booking)
    await db.flush()
    return booking


async def get_by_id(db: AsyncSession, booking_id: uuid.UUID) -> Booking | None:
    q = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def update_status(
    db: AsyncSession,
    booking: Booking,
    status: str,
    **extra: Any,
) -> Booking:
    booking.status = status
    for k, v in extra.items():
        setattr(booking, k, v)
    await db.flush()
    return booking


async def get_by_client(
    db: AsyncSession,
    client_id: uuid.UUID,
    *,
    status: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Booking], int]:
    q = select(Booking).where(Booking.client_id == client_id)
    if status:
        q = q.where(Booking.status == status)
    if from_date:
        q = q.where(Booking.scheduled_at >= from_date)
    if to_date:
        q = q.where(Booking.scheduled_at <= to_date)
    count = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = list(
        (await db.execute(q.order_by(Booking.scheduled_at.desc()).offset(offset).limit(limit)))
        .scalars().all()
    )
    return items, count


async def get_by_coach(
    db: AsyncSession,
    coach_id: uuid.UUID,
    *,
    status: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Booking], int]:
    q = select(Booking).where(Booking.coach_id == coach_id)
    if status:
        q = q.where(Booking.status == status)
    if from_date:
        q = q.where(Booking.scheduled_at >= from_date)
    if to_date:
        q = q.where(Booking.scheduled_at <= to_date)
    count = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = list(
        (await db.execute(q.order_by(Booking.scheduled_at.asc()).offset(offset).limit(limit)))
        .scalars().all()
    )
    return items, count


async def get_by_slot(
    db: AsyncSession,
    coach_id: uuid.UUID,
    slot_datetime: datetime,
    *,
    active_only: bool = True,
) -> list[Booking]:
    """Réservations pour un créneau donné (pour compter les slots occupés)."""
    q = select(Booking).where(
        Booking.coach_id == coach_id,
        Booking.scheduled_at == slot_datetime,
    )
    if active_only:
        active_statuses = ["pending_coach_validation", "confirmed"]
        q = q.where(Booking.status.in_(active_statuses))
    result = await db.execute(q)
    return list(result.scalars().all())


async def count_pending_for_client(
    db: AsyncSession, client_id: uuid.UUID, coach_id: uuid.UUID
) -> int:
    q = select(func.count()).where(
        Booking.client_id == client_id,
        Booking.coach_id == coach_id,
        Booking.status == "pending_coach_validation",
    )
    return (await db.execute(q)).scalar_one()


async def get_upcoming(
    db: AsyncSession, user_id: uuid.UUID, role: str, limit: int = 10
) -> list[Booking]:
    now = datetime.now(timezone.utc)
    q = select(Booking).where(
        Booking.scheduled_at >= now,
        Booking.status == "confirmed",
    )
    if role == "coach":
        q = q.where(Booking.coach_id == user_id)
    else:
        q = q.where(Booking.client_id == user_id)
    q = q.order_by(Booking.scheduled_at.asc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_expired_pending(
    db: AsyncSession, older_than_hours: int = 24
) -> list[Booking]:
    """Réservations en pending_coach_validation depuis plus de N heures."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
    q = select(Booking).where(
        Booking.status == "pending_coach_validation",
        Booking.created_at < cutoff,
    )
    result = await db.execute(q)
    return list(result.scalars().all())
