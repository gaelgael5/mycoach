"""Service annulation en masse (bulk cancel) — B2-32."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import booking_repository
from app.services import booking_service


class BulkCancelAuthError(Exception):
    pass


@dataclass
class BulkCancelResult:
    cancelled_count: int = 0
    sms_sent_count: int = 0
    sms_failed_count: int = 0
    failed_clients: list[str] = field(default_factory=list)


async def bulk_cancel_bookings(
    db: AsyncSession,
    coach: User,
    booking_ids: list[uuid.UUID],
    *,
    template_id: uuid.UUID | None = None,
    custom_message: str | None = None,
    send_sms: bool = True,
) -> BulkCancelResult:
    """Annule en masse des séances et envoie les SMS d'annulation.

    Atomique pour les annulations DB (rollback si erreur).
    SMS best-effort : un échec SMS n'annule pas les annulations.
    """
    result = BulkCancelResult()

    # 1. Vérifier que tous les bookings appartiennent au coach
    bookings = []
    for bid in booking_ids:
        booking = await booking_repository.get_by_id(db, bid)
        if booking is None or booking.coach_id != coach.id:
            raise BulkCancelAuthError(
                f"Réservation {bid} introuvable ou n'appartient pas à ce coach"
            )
        bookings.append(booking)

    # 2. Annuler chaque séance (DB) — atomique
    from datetime import datetime, timezone
    for booking in bookings:
        if booking.status in ("confirmed", "pending_coach_validation"):
            await booking_service.coach_cancel_booking(db, coach, booking.id)
            result.cancelled_count += 1

    # 3. Envoyer les SMS (best-effort)
    if send_sms and (template_id or custom_message):
        try:
            from app.core.sms.provider import get_sms_provider
            from app.repositories.sms_log_repository import create_log, update_status
            from app.repositories import cancellation_template_repository as tmpl_repo
            from app.schemas.cancellation_template import _extract_variables
            from sqlalchemy import select
            from app.models.user import User as UserModel

            sms_provider = get_sms_provider()

            # Charger le template si demandé
            template = None
            if template_id:
                from app.models.coach_profile import CoachProfile
                q = select(CoachProfile).where(CoachProfile.user_id == coach.id)
                res = await db.execute(q)
                profile = res.scalar_one_or_none()
                if profile:
                    template = await tmpl_repo.get_by_id_and_coach(db, template_id, profile.id)

            for booking in bookings:
                # Charger les infos client
                q = select(UserModel).where(UserModel.id == booking.client_id)
                client = (await db.execute(q)).scalar_one_or_none()
                if not client or not client.phone:
                    result.sms_failed_count += 1
                    result.failed_clients.append(str(booking.client_id))
                    continue

                # Résoudre le message
                if template:
                    body = (
                        template.body
                        .replace("{prénom}", client.first_name or "")
                        .replace("{date}", booking.scheduled_at.strftime("%d/%m/%Y"))
                        .replace("{heure}", booking.scheduled_at.strftime("%H:%M"))
                        .replace("{coach}", coach.first_name or "")
                    )
                elif custom_message:
                    body = custom_message
                else:
                    continue

                # Créer le log et envoyer
                sms_log = await create_log(
                    db, coach.id, client.phone, body,
                    client_id=client.id, template_id=template_id
                )
                sms_result = await sms_provider.send(client.phone, body)
                if sms_result.success:
                    await update_status(
                        db, sms_log, "sent",
                        provider_message_id=sms_result.provider_message_id
                    )
                    result.sms_sent_count += 1
                else:
                    await update_status(
                        db, sms_log, "failed",
                        error_message=sms_result.error_message
                    )
                    result.sms_failed_count += 1
                    result.failed_clients.append(client.first_name or str(client.id))

        except ImportError:
            # SMS module pas encore disponible (sous-agent pas fini)
            pass

    return result
