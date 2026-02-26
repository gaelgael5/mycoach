"""Service paiements & forfaits — B1-24."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import payment_repository, coach_repository
from app.schemas.payment import PackageCreate, PaymentRecord, HoursSummary


class PackageNotFoundError(Exception):
    pass


class PackageExhaustedError(Exception):
    pass


# ── Forfaits ──────────────────────────────────────────────────────────────────

async def create_package_for_client(
    db: AsyncSession,
    coach: User,
    client_id: uuid.UUID,
    data: PackageCreate,
) -> object:
    return await payment_repository.create_package(
        db,
        client_id=client_id,
        coach_id=coach.id,
        pricing_id=data.pricing_id,
        name=data.name,
        sessions_total=data.sessions_total,
        sessions_remaining=data.sessions_total,  # au départ = total
        price_cents=data.price_cents,
        currency=data.currency,
        valid_until=data.valid_until,
    )


async def deduct_session(
    db: AsyncSession, coach: User, client_id: uuid.UUID
) -> object:
    """Déduit une séance du forfait actif. Appelé après qu'une séance passe en 'done'."""
    pkg = await payment_repository.get_active_package(db, client_id, coach.id)
    if pkg is None:
        raise PackageNotFoundError("Aucun forfait actif pour ce client")
    return await payment_repository.deduct_session(db, pkg)


async def check_package_alerts(
    db: AsyncSession, coach: User, client_id: uuid.UUID
) -> bool:
    """Retourne True si une alerte '2 séances restantes' doit être envoyée."""
    pkg = await payment_repository.get_active_package(db, client_id, coach.id)
    if pkg is None or pkg.alert_sent:
        return False
    if pkg.sessions_remaining <= 2:
        await payment_repository.mark_alert_sent(db, pkg)
        return True
    return False


# ── Paiements ──────────────────────────────────────────────────────────────────

async def record_payment(
    db: AsyncSession,
    coach: User,
    client_id: uuid.UUID,
    data: PaymentRecord,
) -> object:
    return await payment_repository.record_payment(
        db,
        coach_id=coach.id,
        client_id=client_id,
        package_id=data.package_id,
        amount_cents=data.amount_cents,
        currency=data.currency,
        payment_method=data.payment_method,
        reference=data.reference,
        description=data.description,
        paid_at=data.paid_at,
        due_at=data.due_at,
        status="paid" if data.paid_at else "pending",
    )


async def get_hours_summary(
    db: AsyncSession, coach: User, client_id: uuid.UUID
) -> HoursSummary:
    active_pkg = await payment_repository.get_active_package(db, client_id, coach.id)
    remaining = await payment_repository.count_remaining(db, client_id, coach.id)
    done = await payment_repository.count_done_sessions(db, client_id, coach.id)

    return HoursSummary(
        client_id=client_id,
        active_package=active_pkg,  # type: ignore
        sessions_total_all_time=done + remaining,
        sessions_remaining=remaining,
        sessions_done=done,
        sessions_due=0,  # Phase 2 : quand on aura les séances dues (no-show)
        alert_low_sessions=(active_pkg is not None and active_pkg.sessions_remaining <= 2),
    )
