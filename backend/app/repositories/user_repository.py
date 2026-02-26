"""
Repository User — accès BDD pur, aucune logique métier.
Toutes les requêtes passent par ce fichier.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import hash_for_lookup
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.utils.hashing import generate_secure_token, hash_password


class UserRepository:

    # -----------------------------------------------------------------------
    # Lecture
    # -----------------------------------------------------------------------

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Lookup via email_hash (index unique) — jamais via scan du champ chiffré."""
        h = hash_for_lookup(email)
        result = await db.execute(select(User).where(User.email_hash == h))
        return result.scalar_one_or_none()

    async def get_by_google_sub(self, db: AsyncSession, google_sub: str) -> User | None:
        """
        Lookup par google_sub chiffré.
        Nécessite un scan complet + déchiffrement côté Python.
        Acceptable car utilisé uniquement au login Google (rare).
        Optimisation possible en phase 2 : ajouter google_sub_hash.
        """
        result = await db.execute(select(User))
        for user in result.scalars():
            if user.google_sub == google_sub:
                return user
        return None

    # -----------------------------------------------------------------------
    # Écriture
    # -----------------------------------------------------------------------

    async def create(
        self,
        db: AsyncSession,
        *,
        first_name: str,
        last_name: str,
        email: str,
        role: str,
        password_plain: str | None = None,
        google_sub: str | None = None,
        locale: str = "fr-FR",
        timezone: str = "Europe/Paris",
        country: str = "FR",
    ) -> User:
        """
        Crée un utilisateur.
        Hache le password si fourni.
        email_hash et search_token sont synchronisés automatiquement via @validates.
        """
        user = User(
            role=role,
            first_name=first_name,
            last_name=last_name,
            email=email,          # @validates → email_hash + search_token mis à jour
            google_sub=google_sub,
            locale=locale,
            timezone=timezone,
            country=country,
            status="unverified",
        )
        if password_plain:
            user.password_hash = hash_password(password_plain)

        db.add(user)
        await db.flush()  # génère l'id sans commit
        return user

    async def update(
        self,
        db: AsyncSession,
        user: User,
        **fields,
    ) -> User:
        """Met à jour les champs fournis sur l'utilisateur."""
        for key, value in fields.items():
            setattr(user, key, value)
        await db.flush()
        return user

    async def mark_email_verified(self, db: AsyncSession, user: User) -> User:
        user.status = "active"
        user.email_verified_at = datetime.now(timezone.utc)
        await db.flush()
        return user

    async def request_deletion(self, db: AsyncSession, user: User) -> User:
        """Marque le compte pour suppression dans 30 jours."""
        user.status = "deletion_pending"
        user.deletion_requested_at = datetime.now(timezone.utc)
        await db.flush()
        return user

    # -----------------------------------------------------------------------
    # Email verification tokens
    # -----------------------------------------------------------------------

    async def create_email_token(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> tuple[str, EmailVerificationToken]:
        """Crée un token de vérification email. Retourne (plain_token, model)."""
        plain_token, token_hash = generate_secure_token()
        token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(token)
        await db.flush()
        return plain_token, token

    async def get_email_token_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> EmailVerificationToken | None:
        result = await db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def consume_email_token(
        self, db: AsyncSession, token: EmailVerificationToken
    ) -> None:
        token.used_at = datetime.now(timezone.utc)
        await db.flush()

    # -----------------------------------------------------------------------
    # Password reset tokens
    # -----------------------------------------------------------------------

    async def create_reset_token(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> tuple[str, PasswordResetToken]:
        """Crée un token de réinitialisation. Retourne (plain_token, model)."""
        plain_token, token_hash = generate_secure_token()
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(token)
        await db.flush()
        return plain_token, token

    async def get_reset_token_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> PasswordResetToken | None:
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def consume_reset_token(
        self, db: AsyncSession, token: PasswordResetToken
    ) -> None:
        token.used_at = datetime.now(timezone.utc)
        await db.flush()


# Instance singleton — importée dans les services et le middleware
user_repository = UserRepository()
