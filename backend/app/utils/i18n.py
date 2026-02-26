"""
Internationalisation backend — fonction t(key, locale, **kwargs).

Les fichiers JSON sont chargés une seule fois au démarrage.
La locale est extraite du header Accept-Language de chaque requête.
Fallback : fr-FR → fr → en.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path

from fastapi import Request

logger = logging.getLogger(__name__)

LOCALES_DIR = Path(__file__).parent.parent / "locales"
DEFAULT_LOCALE = "fr-FR"
FALLBACK_LOCALE = "en"


@lru_cache(maxsize=20)
def _load_locale(locale_code: str) -> dict:
    """
    Charge et met en cache le fichier JSON d'une locale.
    Essaie : fr-FR → fr → en (dans cet ordre).
    """
    candidates = [
        locale_code,                     # fr-FR
        locale_code.split("-")[0],       # fr
        FALLBACK_LOCALE,                 # en
    ]
    for code in candidates:
        path = LOCALES_DIR / f"{code}.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)

    logger.warning("Aucun fichier de locale trouvé pour '%s'", locale_code)
    return {}


def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    """
    Traduit une clé i18n dans la locale donnée.

    Args:
        key:    Clé pointée (ex: "auth.error.email_already_used")
        locale: Code BCP 47 (ex: "fr-FR", "en-US")
        **kwargs: Variables à interpoler dans le message (ex: name="Jean")

    Returns:
        Message traduit, ou la clé elle-même si non trouvée (jamais d'exception).

    Usage:
        t("auth.error.invalid_credentials", "fr-FR")
        t("booking.notification.confirmed", "en-US", coach="Marie", date="25 fév.")
    """
    strings = _load_locale(locale)

    # Navigation par points : "auth.error.email_already_used"
    value = strings
    for part in key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = None
            break

    if value is None:
        logger.warning("Clé i18n introuvable : '%s' pour locale '%s'", key, locale)
        return key  # Fallback : retourne la clé brute (jamais d'exception)

    if kwargs:
        try:
            return str(value).format(**kwargs)
        except KeyError as e:
            logger.warning("Variable i18n manquante %s dans '%s'", e, key)
            return str(value)

    return str(value)


def get_locale_from_request(request: Request) -> str:
    """
    Extrait la locale depuis le header Accept-Language.
    Format attendu : "fr-FR,fr;q=0.9,en-US;q=0.8"
    Retourne la première locale reconnue, ou DEFAULT_LOCALE.
    """
    accept_lang = request.headers.get("Accept-Language", "")
    if not accept_lang:
        return DEFAULT_LOCALE

    # Prendre le premier segment (avant la virgule ou le point-virgule)
    primary = accept_lang.split(",")[0].split(";")[0].strip()
    if primary:
        # Normaliser : "fr-fr" → "fr-FR"
        parts = primary.split("-")
        if len(parts) == 2:
            return f"{parts[0].lower()}-{parts[1].upper()}"
        return parts[0].lower()

    return DEFAULT_LOCALE
