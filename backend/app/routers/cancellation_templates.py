"""Router templates d'annulation — B1-34."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_coach
from app.database import get_db
from app.models.user import User
from app.repositories.cancellation_template_repository import (
    MaxTemplatesReachedError,
    LastTemplateError,
)
from app.schemas.cancellation_template import (
    CancellationTemplateCreate,
    CancellationTemplateUpdate,
    CancellationTemplateResponse,
    CancellationTemplatePreviewRequest,
    CancellationTemplatePreview,
    CancellationTemplateReorderRequest,
)
from app.schemas.common import MessageResponse
from app.services import cancellation_template_service as svc
from app.services.cancellation_template_service import TemplateNotFoundError
from app.services.coach_service import ProfileNotFoundError

router = APIRouter(prefix="/coaches/cancellation-templates", tags=["cancellation-templates"])


@router.get("", response_model=list[CancellationTemplateResponse])
async def list_templates(
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await svc.list_templates(db, current_user)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")


@router.post("", response_model=CancellationTemplateResponse, status_code=201)
async def create_template(
    data: CancellationTemplateCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        tmpl = await svc.create_template(db, current_user, data)
        await db.commit()
        return tmpl
    except MaxTemplatesReachedError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")


@router.put("/{template_id}", response_model=CancellationTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    data: CancellationTemplateUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        tmpl = await svc.update_template(db, current_user, template_id, data)
        await db.commit()
        await db.refresh(tmpl)
        return tmpl
    except TemplateNotFoundError:
        raise HTTPException(status_code=404, detail="Template introuvable")
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")


@router.delete("/{template_id}", response_model=MessageResponse)
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        await svc.delete_template(db, current_user, template_id)
        await db.commit()
        return {"message": "Template supprimé"}
    except LastTemplateError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except TemplateNotFoundError:
        raise HTTPException(status_code=404, detail="Template introuvable")
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")


@router.post("/{template_id}/preview", response_model=CancellationTemplatePreview)
async def preview_template(
    template_id: uuid.UUID,
    data: CancellationTemplatePreviewRequest,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await svc.preview_template(db, current_user, template_id, data)
    except TemplateNotFoundError:
        raise HTTPException(status_code=404, detail="Template introuvable")
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")


@router.post("/reorder", response_model=list[CancellationTemplateResponse])
async def reorder_templates(
    data: CancellationTemplateReorderRequest,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        templates = await svc.reorder_templates(db, current_user, data)
        await db.commit()
        for t in templates:
            await db.refresh(t)
        return templates
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil coach introuvable")
