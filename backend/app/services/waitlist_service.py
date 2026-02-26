"""Service liste d'attente — B2-15."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.waitlist_entry import WaitlistEntry
from app.repositories import waitlist_repository


class AlreadyInWaitlistError(Exception):
    pass


class WaitlistEntryNotFoundError(Exception):
    pass


class ConfirmationWindowExpiredError(Exception):
    pass


async def join_waitlist(
    db: AsyncSession,
    client: User,
    coach_id: uuid.UUID,
    slot_datetime: datetime,
    booking_id: uuid.UUID | None = None,
) -> WaitlistEntry:
    """Rejoindre la liste d'attente pour un créneau.

    Vérifie que le client n'est pas déjà dans la file pour ce créneau.
    """
    existing = await waitlist_repository.get_by_client(db, client.id)
    for e in existing:
        if e.coach_id == coach_id and e.slot_datetime == slot_datetime:
            raise AlreadyInWaitlistError("Vous êtes déjà dans la liste d'attente pour ce créneau")

    # Position = nombre d'entrées actives + 1
    position = await waitlist_repository.count_waiting(db, coach_id, slot_datetime) + 1
    return await waitlist_repository.add_entry(
        db, coach_id, slot_datetime, client.id, position, booking_id
    )


async def notify_next(
    db: AsyncSession,
    coach_id: uuid.UUID,
    slot_datetime: datetime,
) -> WaitlistEntry | None:
    """Notifie le 1er en attente qu'une place est disponible.

    Lui donne 30 minutes pour confirmer.
    """
    entry = await waitlist_repository.get_first_waiting(db, coach_id, slot_datetime)
    if entry is None:
        return None

    now = datetime.now(timezone.utc)
    entry = await waitlist_repository.update_status(
        db, entry, "notified",
        notified_at=now,
        expires_at=now + timedelta(minutes=30),
    )
    # TODO Phase 2 B2-17 : notification push via notification_service
    return entry


async def confirm_from_waitlist(
    db: AsyncSession, client: User, entry_id: uuid.UUID
) -> WaitlistEntry:
    """Le client confirme depuis la liste d'attente (dans les 30 min)."""
    entry = await waitlist_repository.get_by_id(db, entry_id)
    if entry is None or entry.client_id != client.id:
        raise WaitlistEntryNotFoundError("Entrée introuvable")
    if entry.status != "notified":
        raise ConfirmationWindowExpiredError("Vous n'avez pas reçu de notification pour ce créneau")
    if entry.expires_at and datetime.now(timezone.utc) > entry.expires_at:
        # Fenêtre expirée → passer en expired, notifier le suivant
        await waitlist_repository.update_status(db, entry, "expired")
        await notify_next(db, entry.coach_id, entry.slot_datetime)
        raise ConfirmationWindowExpiredError("La fenêtre de confirmation de 30 minutes a expiré")

    return await waitlist_repository.update_status(db, entry, "confirmed")


async def leave_waitlist(
    db: AsyncSession, client: User, entry_id: uuid.UUID
) -> None:
    entry = await waitlist_repository.get_by_id(db, entry_id)
    if entry is None or entry.client_id != client.id:
        raise WaitlistEntryNotFoundError("Entrée introuvable")
    coach_id = entry.coach_id
    slot_datetime = entry.slot_datetime
    await waitlist_repository.remove_entry(db, entry)
    await waitlist_repository.reorder(db, coach_id, slot_datetime)


async def expire_notified_entries(db: AsyncSession) -> int:
    """Worker : expire les entrées 'notified' dont expires_at est dépassé."""
    from sqlalchemy import select
    from app.models.waitlist_entry import WaitlistEntry
    now = datetime.now(timezone.utc)
    q = select(WaitlistEntry).where(
        WaitlistEntry.status == "notified",
        WaitlistEntry.expires_at < now,
    )
    result = await db.execute(q)
    expired = list(result.scalars().all())
    count = 0
    for entry in expired:
        await waitlist_repository.update_status(db, entry, "expired")
        await notify_next(db, entry.coach_id, entry.slot_datetime)
        count += 1
    return count
