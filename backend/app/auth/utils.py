"""
Utilitaires d'authentification — vérification Google ID Token, extraction locale.
"""
import logging

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import get_settings

logger = logging.getLogger(__name__)


class GoogleTokenError(Exception):
    """Token Google invalide, expiré ou audience incorrecte."""
    pass


def verify_google_token(token: str) -> dict:
    """
    Vérifie un Google ID Token côté serveur.

    Args:
        token: ID Token obtenu par le SDK Google Sign-In côté Android.

    Returns:
        Payload décodé : { sub, email, name, picture, email_verified, ... }

    Raises:
        GoogleTokenError: Si le token est invalide, expiré, ou mauvaise audience.
    """
    settings = get_settings()
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # Vérifications supplémentaires
        if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise GoogleTokenError("Issuer invalide")

        if not payload.get("email_verified"):
            raise GoogleTokenError("Email Google non vérifié")

        return payload

    except ValueError as e:
        logger.warning("Google token invalide : %s", e)
        raise GoogleTokenError(str(e)) from e


def extract_google_user_info(payload: dict) -> dict:
    """
    Extrait les informations utiles du payload Google.

    Returns:
        { sub, email, first_name, last_name, picture_url }
    """
    full_name = payload.get("name", "")
    parts = full_name.split(" ", 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""

    return {
        "sub": payload["sub"],
        "email": payload["email"],
        "first_name": first_name or "Utilisateur",
        "last_name": last_name or "Google",
        "picture_url": payload.get("picture"),
    }
