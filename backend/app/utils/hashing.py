"""
Utilitaires de hachage et génération de clés.
Aucune valeur sensible ne doit apparaître dans les logs.
"""
import hashlib
import hmac
import os
import secrets

import bcrypt

from app.config import get_settings


# ---------------------------------------------------------------------------
# Passwords (bcrypt, coût 12)
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Hache un mot de passe avec bcrypt (coût 12)."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed: str) -> bool:
    """Vérifie un mot de passe en temps constant (protection timing attack)."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------

def generate_api_key() -> tuple[str, str]:
    """
    Génère une API Key et son hash SHA-256.

    Returns:
        (plain_key, key_hash) — stocker uniquement key_hash en base.
        plain_key est retourné une seule fois au client.

    Format : SHA-256(random_token + salt) → hex 64 chars
    """
    settings = get_settings()
    raw = secrets.token_hex(32)  # 256 bits d'entropie
    key_hash = hashlib.sha256(f"{raw}{settings.API_KEY_SALT}".encode()).hexdigest()
    return raw, key_hash


def hash_api_key(plain_key: str) -> str:
    """Calcule le hash d'une clé existante pour la recherche en base."""
    settings = get_settings()
    return hashlib.sha256(f"{plain_key}{settings.API_KEY_SALT}".encode()).hexdigest()


# ---------------------------------------------------------------------------
# Tokens (email verification, password reset)
# ---------------------------------------------------------------------------

def generate_secure_token() -> tuple[str, str]:
    """
    Génère un token URL-safe et son hash SHA-256.

    Returns:
        (plain_token, token_hash)
        plain_token → inclus dans l'URL du lien email
        token_hash  → stocké en base pour la vérification
    """
    plain = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(plain.encode()).hexdigest()
    return plain, token_hash


def hash_token(plain_token: str) -> str:
    """Hash d'un token reçu pour lookup en base."""
    return hashlib.sha256(plain_token.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Comparaison en temps constant
# ---------------------------------------------------------------------------

def compare_digest(a: str, b: str) -> bool:
    """Comparaison en temps constant — protection contre les timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())
