"""
Middleware d'authentification API Key.

Toutes les routes sauf /auth/* et /health nécessitent X-API-Key.
Les dépendances FastAPI (get_current_user, require_coach, etc.) sont injectées via Depends().
"""
import logging

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.repositories.api_key_repository import api_key_repository
from app.utils.hashing import hash_api_key

logger = logging.getLogger(__name__)


async def get_current_user(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dépendance FastAPI — extrait et valide l'API Key du header X-API-Key.

    Raises:
        401 si la clé est absente, invalide ou révoquée.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="api_key_missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    key_hash = hash_api_key(x_api_key)
    user = await api_key_repository.get_user_by_key_hash(db, key_hash)

    if user is None:
        logger.warning("Tentative d'accès avec clé invalide (hash=%s...)", key_hash[:8])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="api_key_invalid",  # clé i18n — traduite côté client
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account_suspended",
        )

    if user.status == "deletion_pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account_pending_deletion",
        )

    return user


async def require_coach(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dépendance — l'utilisateur courant doit être un coach."""
    if current_user.role != "coach":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
        )
    return current_user


async def require_client(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dépendance — l'utilisateur doit pouvoir utiliser les fonctionnalités client.

    Un coach a TOUTES les fonctionnalités d'un client en plus des siennes.
    Seuls les admins sont exclus des endpoints client.
    """
    if current_user.role not in ("client", "coach"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dépendance — l'utilisateur courant doit être un admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
        )
    return current_user
