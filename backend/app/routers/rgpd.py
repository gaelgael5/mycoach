"""Router RGPD — Art. 15/17/20 + consentements — B6-02/03/04/05."""

from __future__ import annotations

from datetime import timedelta, timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.rgpd import (
    ConsentCreate, ConsentResponse,
    DeletionResponse, ExportTokenResponse, UserExportData,
)
from app.services import rgpd_service
from app.models.consent import CONSENT_TYPES

router = APIRouter(prefix="/users/me", tags=["rgpd"])


# ── B6-02 / B6-04 — Export données personnelles ────────────────────────────────

@router.get("/export", response_model=UserExportData)
async def export_my_data(
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Art. 15 + 20 — Télécharger toutes mes données personnelles."""
    if format == "csv":
        csv_data = await rgpd_service.export_user_data_csv(db, current_user)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mycoach_export.csv"},
        )
    data = await rgpd_service.export_user_data(db, current_user)
    return data


@router.post("/export/token", response_model=ExportTokenResponse)
async def generate_export_token(
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
):
    """Génère un lien signé (24h) pour télécharger l'export sans re-authentification."""
    token = rgpd_service.generate_export_token(current_user.id, fmt=format)
    return ExportTokenResponse(token=token, format=format, expires_in_hours=24)


@router.get("/export/download")
async def download_export_by_token(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Télécharger l'export via token signé (sans cookie/API key)."""
    result = rgpd_service.verify_export_token(token)
    if result is None:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    user_id_str, fmt = result

    from sqlalchemy import select
    from app.models.user import User as UserModel
    user = (await db.execute(
        select(UserModel).where(UserModel.id == user_id_str)
    )).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if fmt == "csv":
        csv_data = await rgpd_service.export_user_data_csv(db, user)
        return Response(
            content=csv_data, media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mycoach_export.csv"},
        )
    data = await rgpd_service.export_user_data(db, user)
    import json
    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=mycoach_export.json"},
    )


# ── B6-03 — Suppression RGPD ───────────────────────────────────────────────────

@router.delete("/", response_model=DeletionResponse)
async def request_account_deletion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Art. 17 — Demande de suppression de compte (effective J+30)."""
    requested_at = await rgpd_service.request_deletion(db, current_user)
    effective = requested_at + timedelta(days=30)
    return DeletionResponse(
        message="Votre compte sera supprimé dans 30 jours. Reconnectez-vous pour annuler.",
        deletion_requested_at=requested_at,
        effective_at=effective.date().isoformat(),
    )


# ── B6-05 — Consentements ──────────────────────────────────────────────────────

@router.get("/consents", response_model=list[ConsentResponse])
async def get_my_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les consentements enregistrés."""
    return await rgpd_service.list_consents(db, current_user.id)


@router.post("/consents", response_model=ConsentResponse, status_code=201)
async def record_consent(
    data: ConsentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enregistre un consentement (log immuable — jamais modifiable)."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    consent = await rgpd_service.record_consent(
        db,
        user_id=current_user.id,
        consent_type=data.consent_type,
        version=data.version,
        accepted=data.accepted,
        ip=ip,
        user_agent=ua,
    )
    return ConsentResponse.model_validate(consent)


@router.get("/consents/types", response_model=list[str])
async def consent_types(current_user: User = Depends(get_current_user)):
    """Liste les types de consentements disponibles."""
    return CONSENT_TYPES
