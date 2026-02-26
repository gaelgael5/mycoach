"""Chiffrement des tokens OAuth via TOKEN_ENCRYPTION_KEY (Fernet)."""

from __future__ import annotations

import os

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    key = os.environ.get("TOKEN_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY non configurée")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token(token: str) -> str:
    return _fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _fernet().decrypt(encrypted.encode()).decode()
