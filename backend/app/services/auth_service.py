"""
Service d'authentification — logique métier complète.

Implémente : register, verify_email, login_with_email, login_with_google,
             logout, logout_all, forgot_password, reset_password.

Aucun accès direct à la BDD — tout passe par les repositories.
"""
import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import GoogleTokenError, extract_google_user_info, verify_google_token
from app.models.user import User
from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository
from app.utils.hashing import hash_password, hash_token, verify_password

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions métier typées (§ CODING_AGENT.md)
# ---------------------------------------------------------------------------

class EmailAlreadyUsedError(Exception):
    """Email déjà associé à un compte."""
    pass


class InvalidCredentialsError(Exception):
    """Email ou mot de passe incorrect."""
    pass


class AccountNotVerifiedError(Exception):
    """Compte créé mais email non vérifié."""
    pass


class AccountSuspendedError(Exception):
    """Compte suspendu par un admin."""
    pass


class TokenExpiredError(Exception):
    """Token de vérification ou de reset expiré."""
    pass


class TokenInvalidError(Exception):
    """Token introuvable ou déjà utilisé."""
    pass


class GoogleAuthError(Exception):
    """Erreur lors de la vérification du token Google."""
    pass


# ---------------------------------------------------------------------------
# Data classes de retour
# ---------------------------------------------------------------------------

@dataclass
class AuthResult:
    """Résultat d'une connexion réussie."""
    api_key: str   # clé en clair — à retourner une seule fois
    user: User


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AuthService:

    async def register(
        self,
        db: AsyncSession,
        *,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role: str,
        locale: str = "fr-FR",
        country: str = "FR",
        device_label: str | None = None,
    ) -> AuthResult:
        """
        Inscription : crée l'utilisateur + génère un token de vérification email.
        Le compte est en statut 'unverified' jusqu'à la vérification.

        Raises:
            EmailAlreadyUsedError: si l'email est déjà utilisé.
        """
        existing = await user_repository.get_by_email(db, email)
        if existing is not None:
            raise EmailAlreadyUsedError(email)

        user = await user_repository.create(
            db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password_plain=password,
            locale=locale,
            country=country,
        )

        # Génère le token de vérification email
        plain_token, _ = await user_repository.create_email_token(db, user.id)

        # TODO (phase 2) : envoyer l'email avec plain_token via email_service
        logger.info(
            "Token vérification email pour user %s : %s [ENV_DEV]", user.id, plain_token
        )

        # Génère l'API Key (l'utilisateur est connecté immédiatement)
        plain_key, _ = await api_key_repository.create(db, user.id, device_label)

        return AuthResult(api_key=plain_key, user=user)

    async def verify_email(
        self,
        db: AsyncSession,
        plain_token: str,
    ) -> User:
        """
        Vérifie le token email et active le compte.

        Raises:
            TokenInvalidError: token introuvable.
            TokenExpiredError: token expiré.
        """
        token_hash = hash_token(plain_token)
        token = await user_repository.get_email_token_by_hash(db, token_hash)

        if token is None or token.is_used:
            raise TokenInvalidError(plain_token)

        if token.is_expired:
            raise TokenExpiredError(plain_token)

        user = await user_repository.get_by_id(db, token.user_id)
        if user is None:
            raise TokenInvalidError("user_not_found")

        await user_repository.consume_email_token(db, token)
        await user_repository.mark_email_verified(db, user)

        return user

    async def login_with_email(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        device_label: str | None = None,
    ) -> AuthResult:
        """
        Connexion par email + mot de passe.

        Raises:
            InvalidCredentialsError: mauvais email ou password.
            AccountNotVerifiedError: compte non vérifié.
            AccountSuspendedError: compte suspendu.
        """
        user = await user_repository.get_by_email(db, email)

        # Vérification en temps constant — même si user est None pour éviter timing attack
        # NB : dummy_hash est un hash bcrypt valide (cost 4 pour la rapidité en test)
        _DUMMY_HASH = "$2b$04$UVdaihXuqAh612dvOfYDIuoszpGv/L2MUZWK7wGYzv/E/Y1nYyMTm"
        valid = verify_password(password, user.password_hash if user and user.password_hash else _DUMMY_HASH)

        if user is None or not valid:
            raise InvalidCredentialsError()

        if user.email_verified_at is None:
            raise AccountNotVerifiedError()

        if user.status == "suspended":
            raise AccountSuspendedError()

        plain_key, _ = await api_key_repository.create(db, user.id, device_label)
        return AuthResult(api_key=plain_key, user=user)

    async def login_with_google(
        self,
        db: AsyncSession,
        *,
        id_token: str,
        device_label: str | None = None,
    ) -> tuple[AuthResult, bool]:
        """
        Connexion Google — vérifie le ID token, crée le compte si nécessaire.

        Returns:
            (AuthResult, is_new_user) — is_new_user=True → rediriger vers RoleSelection.

        Raises:
            GoogleAuthError: token invalide.
        """
        try:
            payload = verify_google_token(id_token)
        except GoogleTokenError as e:
            raise GoogleAuthError(str(e)) from e

        info = extract_google_user_info(payload)

        # Cherche par google_sub d'abord, puis par email (compte déjà créé par email)
        user = await user_repository.get_by_google_sub(db, info["sub"])
        is_new = False

        if user is None:
            user = await user_repository.get_by_email(db, info["email"])
            if user is not None:
                # Lie le compte existant à Google
                await user_repository.update(db, user, google_sub=info["sub"])
            else:
                # Nouvel utilisateur Google — rôle à choisir
                user = await user_repository.create(
                    db,
                    first_name=info["first_name"],
                    last_name=info["last_name"],
                    email=info["email"],
                    role="client",  # temporaire — sera mis à jour après RoleSelection
                    google_sub=info["sub"],
                )
                if info["picture_url"]:
                    await user_repository.update(db, user, avatar_url=info["picture_url"])
                # Email vérifié par Google
                await user_repository.mark_email_verified(db, user)
                is_new = True

        plain_key, _ = await api_key_repository.create(db, user.id, device_label)
        return AuthResult(api_key=plain_key, user=user), is_new

    async def logout(
        self,
        db: AsyncSession,
        plain_key: str,
    ) -> None:
        """Révoque la clé courante."""
        from app.utils.hashing import hash_api_key
        key_hash = hash_api_key(plain_key)
        await api_key_repository.revoke(db, key_hash)

    async def logout_all(
        self,
        db: AsyncSession,
        user_id,
    ) -> int:
        """Révoque toutes les clés de l'utilisateur. Retourne le nombre révoqué."""
        return await api_key_repository.revoke_all_for_user(db, user_id)

    async def forgot_password(
        self,
        db: AsyncSession,
        email: str,
    ) -> None:
        """
        Génère un token de reset si l'email existe.
        Toujours retourner la même réponse (ne pas confirmer l'existence de l'email).
        """
        user = await user_repository.get_by_email(db, email)
        if user is None:
            return  # Réponse identique pour ne pas confirmer l'existence

        plain_token, _ = await user_repository.create_reset_token(db, user.id)

        # TODO (phase 2) : envoyer l'email avec plain_token
        logger.info(
            "Token reset password pour user %s : %s [ENV_DEV]", user.id, plain_token
        )

    async def reset_password(
        self,
        db: AsyncSession,
        plain_token: str,
        new_password: str,
    ) -> User:
        """
        Réinitialise le mot de passe via token.

        Raises:
            TokenInvalidError: token introuvable ou déjà utilisé.
            TokenExpiredError: token expiré.
        """
        token_hash = hash_token(plain_token)
        token = await user_repository.get_reset_token_by_hash(db, token_hash)

        if token is None or token.is_used:
            raise TokenInvalidError(plain_token)

        if token.is_expired:
            raise TokenExpiredError(plain_token)

        user = await user_repository.get_by_id(db, token.user_id)
        if user is None:
            raise TokenInvalidError("user_not_found")

        await user_repository.update(db, user, password_hash=hash_password(new_password))
        await user_repository.consume_reset_token(db, token)

        # Révoque toutes les clés existantes (sécurité après reset)
        await api_key_repository.revoke_all_for_user(db, user.id)

        return user


# Instance singleton
auth_service = AuthService()
