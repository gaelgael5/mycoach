"""Repository liste d'attente — B2-12."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.waitlist_entry import WaitlistEntry


async def add_entry(
    db: AsyncSession,
    coach_id: uuid.UUID,
    slot_datetime: datetime,
    client_id: uuid.UUID,
    position: int,
    booking_id: uuid.UUID | None = None,
) -> WaitlistEntry:
    entry = WaitlistEntry(
        id=uuid.uuid4(),
        booking_id=booking_id,
        coach_id=coach_id,
        slot_datetime=slot_datetime,
        client_id=client_id,
        position=position,
        status="waiting",
    )
    db.add(entry)
    await db.flush()
    return entry


async def get_first_waiting(
    db: AsyncSession, coach_id: uuid.UUID, slot_datetime: datetime
) -> WaitlistEntry | None:
    q = (
        select(WaitlistEntry)
        .where(
            WaitlistEntry.coach_id == coach_id,
            WaitlistEntry.slot_datetime == slot_datetime,
            WaitlistEntry.status == "waiting",
        )
        .order_by(WaitlistEntry.position)
        .limit(1)
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def get_all_for_slot(
    db: AsyncSession, coach_id: uuid.UUID, slot_datetime: datetime
) -> list[WaitlistEntry]:
    q = (
        select(WaitlistEntry)
        .where(
            WaitlistEntry.coach_id == coach_id,
            WaitlistEntry.slot_datetime == slot_datetime,
        )
        .order_by(WaitlistEntry.position)
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_by_client(
    db: AsyncSession, client_id: uuid.UUID, *, active_only: bool = True
) -> list[WaitlistEntry]:
    q = select(WaitlistEntry).where(WaitlistEntry.client_id == client_id)
    if active_only:
        q = q.where(WaitlistEntry.status.in_(["waiting", "notified"]))
    q = q.order_by(WaitlistEntry.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, entry_id: uuid.UUID
) -> WaitlistEntry | None:
    q = select(WaitlistEntry).where(WaitlistEntry.id == entry_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def count_waiting(
    db: AsyncSession, coach_id: uuid.UUID, slot_datetime: datetime
) -> int:
    q = select(func.count()).where(
        WaitlistEntry.coach_id == coach_id,
        WaitlistEntry.slot_datetime == slot_datetime,
        WaitlistEntry.status.in_(["waiting", "notified"]),
    )
    return (await db.execute(q)).scalar_one()


async def update_status(
    db: AsyncSession, entry: WaitlistEntry, status: str, **kwargs: Any
) -> WaitlistEntry:
    entry.status = status
    for k, v in kwargs.items():
        setattr(entry, k, v)
    await db.flush()
    return entry


async def remove_entry(db: AsyncSession, entry: WaitlistEntry) -> None:
    await db.delete(entry)
    await db.flush()


async def reorder(
    db: AsyncSession, coach_id: uuid.UUID, slot_datetime: datetime
) -> None:
    """Recalcule les positions après suppression d'une entrée."""
    entries = await get_all_for_slot(db, coach_id, slot_datetime)
    waiting = [e for e in entries if e.status in ("waiting", "notified")]
    for i, entry in enumerate(sorted(waiting, key=lambda x: x.position), start=1):
        entry.position = i
    await db.flush()
