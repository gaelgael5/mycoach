"""
Chiffrement applicatif Fernet (Python) — 2 clés distinctes.

FIELD_ENCRYPTION_KEY → champs PII (noms, emails, téléphones, notes...)
TOKEN_ENCRYPTION_KEY → tokens OAuth (Strava, Google Calendar, Withings...)

La clé n'apparaît jamais dans les requêtes SQL — sécurité supérieure à pgcrypto.
Un dump PostgreSQL sans les clés est entièrement illisible.
"""
import hashlib
import unicodedata
from functools import lru_cache

from cryptography.fernet import Fernet

from app.config import get_settings


@lru_cache(maxsize=1)
def _fernet_fields() -> Fernet:
    """Fernet A — champs PII. Instancié une seule fois."""
    key = get_settings().FIELD_ENCRYPTION_KEY
    return Fernet(key.encode() if isinstance(key, str) else key)


@lru_cache(maxsize=1)
def _fernet_tokens() -> Fernet:
    """Fernet B — tokens OAuth. Instancié une seule fois."""
    key = get_settings().TOKEN_ENCRYPTION_KEY
    return Fernet(key.encode() if isinstance(key, str) else key)


# ---------------------------------------------------------------------------
# PII (FIELD_ENCRYPTION_KEY)
# ---------------------------------------------------------------------------

def encrypt_field(value: str | None) -> str | None:
    """Chiffre un champ PII. None → None."""
    if value is None:
        return None
    return _fernet_fields().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_field(value: str | None) -> str | None:
    """Déchiffre un champ PII. None → None."""
    if value is None:
        return None
    return _fernet_fields().decrypt(value.encode("ascii")).decode("utf-8")


# ---------------------------------------------------------------------------
# Tokens OAuth (TOKEN_ENCRYPTION_KEY)
# ---------------------------------------------------------------------------

def encrypt_token(value: str | None) -> str | None:
    """Chiffre un token OAuth. None → None."""
    if value is None:
        return None
    return _fernet_tokens().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_token(value: str | None) -> str | None:
    """Déchiffre un token OAuth. None → None."""
    if value is None:
        return None
    return _fernet_tokens().decrypt(value.encode("ascii")).decode("utf-8")


# ---------------------------------------------------------------------------
# Helpers de recherche (non-PII, stockés en clair)
# ---------------------------------------------------------------------------

def hash_for_lookup(value: str) -> str:
    """
    SHA-256 hex d'une valeur normalisée.
    Utilisé pour les colonnes *_hash indexées (ex: email_hash).
    Jamais déchiffrable — uniquement pour l'égalité exacte.
    """
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def normalize_for_search(value: str) -> str:
    """
    Produit un token de recherche non-PII.
    NFD decompose → supprime les diacritiques → lowercase → collapse spaces.
    Exemple : 'Marie-Hélène Dubois' → 'marie-helene dubois'

    Ce token est stocké en clair (colonne search_token).
    Il est irréversible — ne permet pas de retrouver le nom exact.
    Il n'est JAMAIS retourné dans les réponses API ni loggué.
    """
    nfd = unicodedata.normalize("NFD", value)
    ascii_only = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return " ".join(ascii_only.lower().split())
