"""Service réservations — machine d'état complète (B2-14).

Transitions autorisées :
  pending_coach_validation → confirmed       (coach confirme)
  pending_coach_validation → rejected        (coach rejette)
  pending_coach_validation → auto_rejected   (worker 24h)
  confirmed → done                           (coach marque terminée)
  confirmed → cancelled_by_client            (client annule, délai ok)
  confirmed → cancelled_late_by_client       (client annule, trop tard → séance due)
  confirmed → cancelled_by_coach             (coach annule, délai ok)
  confirmed → cancelled_by_coach_late        (coach annule, trop tard)
  confirmed → no_show_client                 (coach marque no-show)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.user import User
from app.repositories import booking_repository, payment_repository, coach_repository
from app.schemas.booking import BookingCreate


# ── Exceptions typées ──────────────────────────────────────────────────────────

class BookingNotFoundError(Exception):
    pass

class InvalidTransitionError(Exception):
    pass

class SlotFullError(Exception):
    pass

class DuplicateBookingError(Exception):
    pass

class NotAuthorizedError(Exception):
    pass


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _get_cancellation_threshold(
    db: AsyncSession, coach_id: uuid.UUID
) -> int:
    """Retourne le seuil d'annulation tardive en heures (défaut 24h).

    Utilise une JOIN directe — pas de lazy loading (interdit en async SQLAlchemy).
    """
    from sqlalchemy import select
    from app.models.cancellation_policy import CancellationPolicy
    from app.models.coach_profile import CoachProfile
    q = (
        select(CancellationPolicy)
        .join(CoachProfile, CancellationPolicy.coach_id == CoachProfile.id)
        .where(CoachProfile.user_id == coach_id)
    )
    result = await db.execute(q)
    policy = result.scalar_one_or_none()
    return policy.threshold_hours if policy else 24


def _is_late(scheduled_at: datetime, threshold_hours: int) -> bool:
    return datetime.now(timezone.utc) > (scheduled_at - timedelta(hours=threshold_hours))


# ── Création ───────────────────────────────────────────────────────────────────

async def create_booking(
    db: AsyncSession, client: User, data: BookingCreate
) -> Booking:
    # Vérifier max_slots du coach
    coach_profile = await coach_repository.get_by_user_id(db, data.coach_id, load_relations=False)
    if coach_profile is None:
        raise BookingNotFoundError("Profil coach introuvable")

    # Compter les bookings actifs sur ce créneau
    occupied = await booking_repository.get_by_slot(db, data.coach_id, data.scheduled_at)
    # max_slots = 1 par défaut (séances individuelles) — à affiner avec availability
    max_slots = 1
    if len(occupied) >= max_slots:
        raise SlotFullError("Ce créneau est complet")

    # Vérifier doublon
    pending = await booking_repository.count_pending_for_client(db, client.id, data.coach_id)
    # Note: accepte plusieurs réservations confirmées (sessions multi-dates)

    booking = await booking_repository.create(
        db,
        client_id=client.id,
        coach_id=data.coach_id,
        scheduled_at=data.scheduled_at,
        duration_min=data.duration_min,
        pricing_id=data.pricing_id,
        package_id=data.package_id,
        gym_id=data.gym_id,
        client_message=data.client_message,
    )
    return booking


# ── Transitions coach ──────────────────────────────────────────────────────────

async def confirm_booking(
    db: AsyncSession, coach: User, booking_id: uuid.UUID
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "pending_coach_validation":
        raise InvalidTransitionError(
            f"Impossible de confirmer une réservation en statut '{booking.status}'"
        )
    return await booking_repository.update_status(
        db, booking, "confirmed",
        confirmed_at=datetime.now(timezone.utc),
    )


async def reject_booking(
    db: AsyncSession, coach: User, booking_id: uuid.UUID, reason: str | None = None
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "pending_coach_validation":
        raise InvalidTransitionError(
            f"Impossible de rejeter une réservation en statut '{booking.status}'"
        )
    return await booking_repository.update_status(
        db, booking, "rejected",
        coach_cancel_reason=reason,
        cancelled_at=datetime.now(timezone.utc),
    )


async def mark_done(
    db: AsyncSession, coach: User, booking_id: uuid.UUID
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "confirmed":
        raise InvalidTransitionError(
            f"Impossible de marquer terminée une réservation en statut '{booking.status}'"
        )
    booking = await booking_repository.update_status(
        db, booking, "done",
        done_at=datetime.now(timezone.utc),
    )
    # Décompter la séance du forfait si applicable
    if booking.package_id:
        pkg = await payment_repository.get_package_by_id(db, booking.package_id)
        if pkg and pkg.sessions_remaining > 0:
            await payment_repository.deduct_session(db, pkg)
    return booking


async def mark_no_show(
    db: AsyncSession, coach: User, booking_id: uuid.UUID
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "confirmed":
        raise InvalidTransitionError(
            f"Impossible de marquer no-show une réservation en statut '{booking.status}'"
        )
    booking = await booking_repository.update_status(
        db, booking, "no_show_client",
        done_at=datetime.now(timezone.utc),
    )
    # Vérifier la politique no-show du coach
    threshold = await _get_cancellation_threshold(db, coach.id)
    from app.models.cancellation_policy import CancellationPolicy
    from app.models.coach_profile import CoachProfile
    from sqlalchemy import select
    q = select(CancellationPolicy).join(
        CoachProfile, CancellationPolicy.coach_id == CoachProfile.id
    ).where(CoachProfile.user_id == coach.id)
    result = await db.execute(q)
    policy = result.scalar_one_or_none()
    if (policy is None or policy.noshow_is_due) and booking.package_id:
        pkg = await payment_repository.get_package_by_id(db, booking.package_id)
        if pkg and pkg.sessions_remaining > 0:
            await payment_repository.deduct_session(db, pkg)
    return booking


async def coach_cancel_booking(
    db: AsyncSession, coach: User, booking_id: uuid.UUID, reason: str | None = None
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "confirmed":
        raise InvalidTransitionError(
            f"Impossible d'annuler une réservation en statut '{booking.status}'"
        )
    threshold = await _get_cancellation_threshold(db, coach.id)
    is_late = _is_late(booking.scheduled_at, threshold)
    new_status = "cancelled_by_coach_late" if is_late else "cancelled_by_coach"
    return await booking_repository.update_status(
        db, booking, new_status,
        coach_cancel_reason=reason,
        cancelled_at=datetime.now(timezone.utc),
    )


async def waive_penalty(
    db: AsyncSession, coach: User, booking_id: uuid.UUID
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.coach_id != coach.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce coach")
    if booking.status != "cancelled_late_by_client":
        raise InvalidTransitionError("Aucune pénalité à exonérer sur cette réservation")
    return await booking_repository.update_status(
        db, booking, "cancelled_late_by_client",
        late_cancel_waived=True,
    )


# ── Transitions client ─────────────────────────────────────────────────────────

async def client_cancel_booking(
    db: AsyncSession, client: User, booking_id: uuid.UUID
) -> Booking:
    booking = await booking_repository.get_by_id(db, booking_id)
    if booking is None:
        raise BookingNotFoundError("Réservation introuvable")
    if booking.client_id != client.id:
        raise NotAuthorizedError("Cette réservation n'appartient pas à ce client")
    if booking.status not in ("pending_coach_validation", "confirmed"):
        raise InvalidTransitionError(
            f"Impossible d'annuler une réservation en statut '{booking.status}'"
        )
    if booking.status == "pending_coach_validation":
        new_status = "cancelled_by_client"
    else:
        threshold = await _get_cancellation_threshold(db, booking.coach_id)
        is_late = _is_late(booking.scheduled_at, threshold)
        new_status = "cancelled_late_by_client" if is_late else "cancelled_by_client"

    return await booking_repository.update_status(
        db, booking, new_status,
        cancelled_at=datetime.now(timezone.utc),
    )


# ── Worker ─────────────────────────────────────────────────────────────────────

async def auto_reject_expired(db: AsyncSession) -> int:
    """Worker : passe en auto_rejected les pending depuis > 24h. Retourne le nb rejeté."""
    expired = await booking_repository.get_expired_pending(db, older_than_hours=24)
    count = 0
    for booking in expired:
        await booking_repository.update_status(
            db, booking, "auto_rejected",
            cancelled_at=datetime.now(timezone.utc),
        )
        count += 1
    return count
