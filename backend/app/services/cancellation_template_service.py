"""Service templates de messages d'annulation — B1-33."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import (
    cancellation_template_repository as repo,
    coach_repository,
)
from app.repositories.cancellation_template_repository import (
    MaxTemplatesReachedError,
    LastTemplateError,
)
from app.schemas.cancellation_template import (
    CancellationTemplateCreate,
    CancellationTemplateUpdate,
    CancellationTemplatePreviewRequest,
    CancellationTemplatePreview,
    CancellationTemplateReorderRequest,
)
from app.services.coach_service import ProfileNotFoundError


class TemplateNotFoundError(Exception):
    pass


async def _get_coach_profile_id(db: AsyncSession, user: User) -> uuid.UUID:
    profile = await coach_repository.get_by_user_id(db, user.id, load_relations=False)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    return profile.id


async def list_templates(db: AsyncSession, user: User):
    coach_id = await _get_coach_profile_id(db, user)
    return await repo.list_by_coach(db, coach_id)


async def create_template(
    db: AsyncSession, user: User, data: CancellationTemplateCreate
):
    coach_id = await _get_coach_profile_id(db, user)
    return await repo.create(db, coach_id, title=data.title, body=data.body)


async def update_template(
    db: AsyncSession,
    user: User,
    template_id: uuid.UUID,
    data: CancellationTemplateUpdate,
):
    coach_id = await _get_coach_profile_id(db, user)
    tmpl = await repo.get_by_id_and_coach(db, template_id, coach_id)
    if tmpl is None:
        raise TemplateNotFoundError("Template introuvable")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    return await repo.update(db, tmpl, **updates)


async def delete_template(
    db: AsyncSession, user: User, template_id: uuid.UUID
) -> None:
    coach_id = await _get_coach_profile_id(db, user)
    tmpl = await repo.get_by_id_and_coach(db, template_id, coach_id)
    if tmpl is None:
        raise TemplateNotFoundError("Template introuvable")
    await repo.delete(db, tmpl)


async def reorder_templates(
    db: AsyncSession, user: User, data: CancellationTemplateReorderRequest
):
    coach_id = await _get_coach_profile_id(db, user)
    items = [{"id": i.id, "position": i.position} for i in data.items]
    return await repo.reorder(db, coach_id, items)


async def preview_template(
    db: AsyncSession,
    user: User,
    template_id: uuid.UUID,
    data: CancellationTemplatePreviewRequest,
) -> CancellationTemplatePreview:
    coach_id = await _get_coach_profile_id(db, user)
    tmpl = await repo.get_by_id_and_coach(db, template_id, coach_id)
    if tmpl is None:
        raise TemplateNotFoundError("Template introuvable")

    resolved = (
        tmpl.body
        .replace("{prénom}", data.client_first_name)
        .replace("{date}", data.session_date)
        .replace("{heure}", data.session_time)
        .replace("{coach}", data.coach_name)
    )
    return CancellationTemplatePreview(
        template_id=template_id,
        resolved_body=resolved,
        client_name=data.client_first_name,
    )


async def seed_default_template(db: AsyncSession, coach_id: uuid.UUID) -> None:
    """Appelé lors de la création de profil coach pour créer le template Maladie."""
    templates = await repo.list_by_coach(db, coach_id)
    if not templates:
        await repo.create_default(db, coach_id)
