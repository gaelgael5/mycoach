"""Router gyms — B1-26."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import gym_repository

router = APIRouter(prefix="/gyms", tags=["gyms"])


class GymChainResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_url: str | None
    website: str | None
    country: str | None
    active: bool

    model_config = {"from_attributes": True}


class GymResponse(BaseModel):
    id: uuid.UUID
    chain_id: uuid.UUID | None
    name: str
    address: str | None
    zip_code: str | None
    city: str
    country: str
    latitude: float | None
    longitude: float | None
    phone: str | None
    email: str | None
    website_url: str | None
    open_24h: bool
    validated: bool

    model_config = {"from_attributes": True}


class GymListResponse(BaseModel):
    items: list[GymResponse]
    total: int
    offset: int
    limit: int


@router.get("/chains", response_model=list[GymChainResponse])
async def list_chains(
    country: str | None = Query(None, description="ISO 3166-1 alpha-2"),
    db: AsyncSession = Depends(get_db),
):
    return await gym_repository.get_chains(db, country=country)


@router.get("", response_model=GymListResponse)
async def search_gyms(
    chain_id: uuid.UUID | None = Query(None),
    country: str | None = Query(None, description="ISO 3166-1 alpha-2"),
    city: str | None = Query(None),
    zip_code: str | None = Query(None),
    q: str | None = Query(None, description="Recherche libre (nom, ville, adresse)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await gym_repository.search(
        db,
        chain_id=chain_id,
        country=country,
        city=city,
        zip_code=zip_code,
        q=q,
        offset=offset,
        limit=limit,
    )
    return GymListResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/{gym_id}", response_model=GymResponse)
async def get_gym(gym_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    gym = await gym_repository.get_by_id(db, gym_id)
    if gym is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return gym
