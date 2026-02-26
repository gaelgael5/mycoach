"""
Import de tous les modèles SQLAlchemy.
Ce fichier est importé par alembic/env.py pour que target_metadata
contienne toutes les tables lors de la génération des migrations.
"""
from app.models.user import User
from app.models.api_key import ApiKey
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken

__all__ = [
    "User",
    "ApiKey",
    "EmailVerificationToken",
    "PasswordResetToken",
]
