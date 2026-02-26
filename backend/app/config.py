"""
Configuration centrale — chargée depuis les variables d'environnement.
Jamais de valeur sensible codée en dur.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Base de données ---
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:port/db

    # --- Chiffrement PII (noms, emails, téléphones, notes...) ---
    FIELD_ENCRYPTION_KEY: str  # Clé Fernet A — générer: Fernet.generate_key().decode()

    # --- Chiffrement tokens OAuth (Strava, Google Calendar, Withings...) ---
    TOKEN_ENCRYPTION_KEY: str  # Clé Fernet B — indépendante de FIELD_ENCRYPTION_KEY

    # --- Auth ---
    API_KEY_SALT: str          # Sel pour la génération des API Keys
    SECRET_KEY: str            # Clé secrète générale (sessions, CSRF...)
    GOOGLE_CLIENT_ID: str      # OAuth2 Google — vérification des ID tokens

    # --- App ---
    ENVIRONMENT: str = "development"  # development | test | production
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    # --- Rate limiting ---
    RATE_LIMIT_AUTH: str = "10/minute"   # login, google

    # --- Email (SMTP — phase 2) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@mycoach.app"

    # --- Firebase (push notifications — phase 2) ---
    FIREBASE_CREDENTIALS_PATH: str = ""

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == "test"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instance unique — chargée une seule fois au démarrage."""
    return Settings()
