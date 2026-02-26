"""
Repository ApiKey — accès BDD pur, aucune logique métier.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.api_key import ApiKey
from app.models.user import User
from app.utils.hashing import generate_api_key


class ApiKeyRepository:

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        device_label: str | None = None,
    ) -> tuple[str, ApiKey]:
        """
        Génère et stocke une nouvelle API Key.
        Returns (plain_key, api_key_model) — plain_key retourné une seule fois au client.
        """
        plain_key, key_hash = generate_api_key()
        api_key = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            device_label=device_label,
        )
        db.add(api_key)
        await db.flush()
        return plain_key, api_key

    async def get_by_hash(
        self, db: AsyncSession, key_hash: str
    ) -> ApiKey | None:
        """Lookup par hash — utilisé dans le middleware d'authentification."""
        result = await db.execute(
            select(ApiKey)
            .options(joinedload(ApiKey.user))
            .where(ApiKey.key_hash == key_hash, ApiKey.revoked == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_user_by_key_hash(
        self, db: AsyncSession, key_hash: str
    ) -> User | None:
        """
        Raccourci pour le middleware : retourne directement l'User associé
        à une clé valide (non révoquée).
        Met à jour last_used_at en même temps.
        """
        api_key = await self.get_by_hash(db, key_hash)
        if api_key is None:
            return None

        # Mise à jour last_used_at (sans flush complet — perf)
        api_key.last_used_at = datetime.now(timezone.utc)
        await db.flush()

        return api_key.user

    async def revoke(self, db: AsyncSession, key_hash: str) -> bool:
        """
        Révoque une clé spécifique.
        Returns True si révoquée, False si introuvable/déjà révoquée.
        """
        result = await db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.revoked == False)  # noqa: E712
        )
        api_key = result.scalar_one_or_none()
        if api_key is None:
            return False

        api_key.revoked = True
        api_key.revoked_at = datetime.now(timezone.utc)
        await db.flush()
        return True

    async def revoke_all_for_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> int:
        """
        Révoque toutes les clés actives d'un utilisateur.
        Returns le nombre de clés révoquées.
        """
        result = await db.execute(
            select(ApiKey).where(
                ApiKey.user_id == user_id, ApiKey.revoked == False  # noqa: E712
            )
        )
        keys = result.scalars().all()
        now = datetime.now(timezone.utc)
        for key in keys:
            key.revoked = True
            key.revoked_at = now

        await db.flush()
        return len(keys)

    async def list_for_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[ApiKey]:
        """Liste les clés actives d'un utilisateur (vue multi-appareils)."""
        result = await db.execute(
            select(ApiKey).where(
                ApiKey.user_id == user_id, ApiKey.revoked == False  # noqa: E712
            )
        )
        return list(result.scalars().all())


# Instance singleton
api_key_repository = ApiKeyRepository()
