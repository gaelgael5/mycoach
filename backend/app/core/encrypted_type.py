"""
TypeDecorators SQLAlchemy pour le chiffrement transparent des champs sensibles.

EncryptedString → champs PII (FIELD_ENCRYPTION_KEY)
EncryptedToken  → tokens OAuth (TOKEN_ENCRYPTION_KEY)

Les deux TypeDecorators sont interchangeables en interface mais utilisent
des clés Fernet distinctes → périmètres de compromission séparés.
"""
from sqlalchemy import String, TypeDecorator

from app.core.encryption import (
    decrypt_field,
    decrypt_token,
    encrypt_field,
    encrypt_token,
)


class EncryptedString(TypeDecorator):
    """
    Chiffre/déchiffre automatiquement les champs PII à l'écriture/lecture.
    Utilise FIELD_ENCRYPTION_KEY.

    La colonne SQL stocke le token Fernet (texte ASCII).
    Taille SQL = plaintext_max_length * 2 + 100 (overhead Fernet ~1.4×).
    """

    impl = String
    cache_ok = True

    def __init__(self, plaintext_max_length: int = 255, **kw):
        encrypted_length = plaintext_max_length * 2 + 100
        super().__init__(encrypted_length, **kw)

    def process_bind_param(self, value, dialect):
        return encrypt_field(value)

    def process_result_value(self, value, dialect):
        return decrypt_field(value)


class EncryptedToken(TypeDecorator):
    """
    Chiffre/déchiffre les tokens OAuth à l'écriture/lecture.
    Utilise TOKEN_ENCRYPTION_KEY — clé distincte de EncryptedString.

    Taille par défaut plus grande (2048) car les tokens JWT/Bearer sont longs.
    """

    impl = String
    cache_ok = True

    def __init__(self, plaintext_max_length: int = 2048, **kw):
        encrypted_length = plaintext_max_length * 2 + 100
        super().__init__(encrypted_length, **kw)

    def process_bind_param(self, value, dialect):
        return encrypt_token(value)

    def process_result_value(self, value, dialect):
        return decrypt_token(value)
