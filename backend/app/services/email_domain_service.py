"""Service — Validation domaine email à l'inscription."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import blocked_domain_repository


class BlockedDomainError(Exception):
    """Le domaine de cet email est refusé (liste noire)."""


def extract_domain(email: str) -> str:
    """Extrait le domaine d'une adresse email (partie après @), en minuscules."""
    parts = email.strip().lower().rsplit("@", 1)
    if len(parts) != 2 or not parts[1]:
        raise ValueError(f"Email invalide : {email!r}")
    return parts[1]


async def check_email_domain(db: AsyncSession, email: str) -> None:
    """Lève BlockedDomainError si le domaine de l'email est bloqué."""
    domain = extract_domain(email)
    if await blocked_domain_repository.is_blocked(db, domain):
        raise BlockedDomainError(
            f"Les adresses email '{domain}' ne sont pas acceptées. "
            "Veuillez utiliser une adresse email permanente."
        )
