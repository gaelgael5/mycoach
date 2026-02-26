# MyCoach — Patterns de développement & Sécurité

> Document de référence technique pour l'agent IA codeur.
> À lire après `CODING_AGENT.md`. S'applique à chaque ligne de code produite.
> Couvre : patterns d'architecture, patterns Kotlin, patterns Python/FastAPI, OWASP API Top 10, OWASP Mobile Top 10.

---

## PARTIE 1 — BACKEND (Python / FastAPI)

### 1.1 Architecture en couches (obligatoire)

```
HTTP Request
     │
     ▼
┌──────────────┐
│   Router     │  ← Reçoit la requête, valide avec Pydantic, appelle le Service
│  (routers/)  │    Aucune logique métier ici
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Service    │  ← Toute la logique métier ici
│ (services/)  │    Orchestre les Repositories, applique les règles
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Repository   │  ← Accès BDD uniquement, aucune logique métier
│(repositories)│    Requêtes SQLAlchemy, retourne des modèles ORM
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
└──────────────┘
```

**Règle d'or :** une couche ne communique qu'avec la couche immédiatement en dessous.
Un Router n'appelle jamais un Repository directement.

---

### 1.2 Pattern Repository

```python
# repositories/user_repository.py

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        await self.db.flush()   # flush pour obtenir l'ID sans commit
        return user

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.flush()
        return user

    async def list_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        filters: dict | None = None
    ) -> tuple[list[User], int]:
        query = select(User)
        if filters:
            if filters.get("role"):
                query = query.where(User.role == filters["role"])
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        result = await self.db.execute(query.offset(offset).limit(limit))
        return result.scalars().all(), total
```

---

### 1.3 Pattern Service

```python
# services/auth_service.py

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        api_key_repo: ApiKeyRepository,
        notification_service: NotificationService,
    ):
        self.user_repo = user_repo
        self.api_key_repo = api_key_repo
        self.notification_service = notification_service

    async def login_with_email(
        self,
        email: str,
        password: str,
        device_name: str | None,
        locale: str,
    ) -> AuthResult:
        # Règle métier : vérification credentials
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.email_verified:
            raise EmailNotVerifiedError()

        # Génération API Key
        api_key = generate_api_key(f"{email}{user.password_hash}")
        await self.api_key_repo.create(user.id, api_key, device_name)

        return AuthResult(api_key=api_key, user=user)

    async def login_with_google(
        self,
        id_token: str,
        device_name: str | None,
    ) -> AuthResult:
        # Vérification Google ID Token
        google_claims = verify_google_token(id_token)  # lève si invalide
        
        # Upsert utilisateur
        user = await self.user_repo.get_by_email(google_claims["email"])
        is_new = user is None
        if is_new:
            user = await self.user_repo.create_from_google(google_claims)

        # Génération API Key
        api_key = generate_api_key(
            f"{google_claims['sub']}{google_claims['email']}"
        )
        await self.api_key_repo.create(user.id, api_key, device_name)

        return AuthResult(api_key=api_key, user=user, is_new_user=is_new)
```

---

### 1.4 Pattern Router (FastAPI)

```python
# routers/auth.py

router = APIRouter(prefix="/auth", tags=["auth"])

# Injection de dépendances via Depends
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(db),
        api_key_repo=ApiKeyRepository(db),
        notification_service=NotificationService(),
    )

@router.post("/login", response_model=AuthResponse, status_code=200)
async def login(
    body: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    # Le Router ne contient AUCUNE logique métier
    # Il valide (Pydantic), appelle le service, retourne la réponse
    try:
        result = await service.login_with_email(
            email=body.email,
            password=body.password,
            device_name=body.device_name,
            locale=get_locale_from_request(request),
        )
        return AuthResponse.from_result(result)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail=t("error.invalid_credentials", get_locale_from_request(request))
        )
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=403,
            detail=t("error.email_not_verified", get_locale_from_request(request))
        )
```

---

### 1.5 Pattern Schemas Pydantic (Request / Response)

```python
# schemas/auth.py

# ✅ Toujours séparer Request et Response
# ✅ Ne jamais exposer des champs sensibles dans les réponses

class LoginRequest(BaseModel):
    email: EmailStr                          # Validation email auto
    password: str = Field(min_length=8)
    device_name: str | None = Field(None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir une majuscule")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir un chiffre")
        return v

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    locale: str
    # ❌ password_hash : jamais exposé
    # ❌ api_key : jamais dans UserResponse

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    api_key: str       # Exposé UNE SEULE FOIS à la création
    user: UserResponse
    is_new_user: bool = False
```

---

### 1.6 Pattern Error Handling (exceptions métier)

```python
# utils/exceptions.py

# Définir des exceptions métier explicites
class MyCoachException(Exception):
    """Base exception"""

class InvalidCredentialsError(MyCoachException):
    pass

class EmailNotVerifiedError(MyCoachException):
    pass

class ResourceNotFoundError(MyCoachException):
    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id

class ForbiddenError(MyCoachException):
    pass

class LateCancellationError(MyCoachException):
    """Annulation < délai de politique"""
    def __init__(self, hours_before: float, policy_hours: int):
        self.hours_before = hours_before
        self.policy_hours = policy_hours

# Handler global dans main.py
@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(request: Request, exc: ResourceNotFoundError):
    locale = get_locale_from_request(request)
    return JSONResponse(
        status_code=404,
        content={"detail": t("error.not_found", locale, resource=exc.resource)}
    )
```

---

### 1.7 Pattern Transactions BDD

```python
# Toujours utiliser le context manager pour les transactions

async def create_booking_with_payment(
    db: AsyncSession,
    booking_data: BookingCreate,
    client_id: uuid.UUID,
) -> Booking:
    async with db.begin():  # Transaction atomique
        booking = await booking_repo.create(booking_data)
        
        if booking_data.pricing_type == "package":
            package = await package_repo.get_active(client_id, booking.coach_id)
            if not package:
                raise NoActivePackageError()
            # Les deux opérations dans la même transaction
            await package_repo.reserve_session(package.id)
        
        return booking
    # Commit automatique si pas d'exception, rollback sinon
```

---

### 1.8 Pattern Pagination

```python
# schemas/common.py
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
    has_more: bool

    @classmethod
    def from_results(cls, items: list[T], total: int, offset: int, limit: int):
        return cls(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total,
        )

# Usage dans le router
@router.get("/coaches/clients", response_model=PaginatedResponse[ClientSummary])
async def list_clients(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    ...
):
```

---

### 1.9 Pattern Chiffrement des données personnelles (PII)

> **Règle non négociable.** Toute donnée à caractère personnel est chiffrée au repos en base, via un `TypeDecorator` SQLAlchemy. Un dump PostgreSQL brut doit être illisible sans la clé.

#### Infrastructure de chiffrement

```python
# app/core/encryption.py
from cryptography.fernet import Fernet
from functools import lru_cache
from app.core.config import settings


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    """Instancié une seule fois — la clé ne doit jamais changer en prod sans re-chiffrement."""
    return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


def encrypt_field(value: str | None) -> str | None:
    """Chiffre une chaîne → token Fernet (base64-urlsafe)."""
    if value is None:
        return None
    return _get_fernet().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_field(value: str | None) -> str | None:
    """Déchiffre un token Fernet → chaîne originale."""
    if value is None:
        return None
    return _get_fernet().decrypt(value.encode("ascii")).decode("utf-8")


def hash_for_lookup(value: str) -> str:
    """SHA-256 hex digest d'une valeur normalisée — utilisé pour les WHERE/index."""
    import hashlib
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()
```

```python
# app/core/encrypted_type.py
from sqlalchemy import String, TypeDecorator
from app.core.encryption import encrypt_field, decrypt_field


class EncryptedString(TypeDecorator):
    """
    Type SQLAlchemy transparent : chiffre à l'écriture, déchiffre à la lecture.
    La colonne SQL stocke le token Fernet (texte ASCII).
    Taille SQL = max_length * 1.5 environ (overhead Fernet).
    """
    impl = String
    cache_ok = True

    def __init__(self, plaintext_max_length: int = 255, **kw):
        # Fernet token ~ 1.4× la taille originale + overhead fixe (~60 bytes)
        encrypted_length = plaintext_max_length * 2 + 100
        super().__init__(encrypted_length, **kw)

    def process_bind_param(self, value, dialect):
        return encrypt_field(value)

    def process_result_value(self, value, dialect):
        return decrypt_field(value)
```

#### Modèle User avec champs chiffrés

```python
# app/models/user.py
import hashlib
import unicodedata
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import Index
from app.core.encrypted_type import EncryptedString
from app.db.base import Base


def _normalize_for_search(value: str) -> str:
    """
    Produit un token de recherche non-PII à partir d'un nom.
    Étapes : NFD decompose → strip diacritiques → lowercase → strip → collapse spaces.
    Exemple : "Marie-Hélène Dubois" → "marie-helene dubois"
    Ce token est stocké en clair — ce n'est PAS le nom réel (pas de fuite PII).
    """
    nfd = unicodedata.normalize("NFD", value)
    ascii_only = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return " ".join(ascii_only.lower().split())


class User(Base):
    __tablename__ = "users"

    # --- Colonnes non-PII (pas de chiffrement) ---
    id:         Mapped[UUID]      = mapped_column(primary_key=True, default=uuid4)
    role:       Mapped[str]       = mapped_column(String(20), nullable=False)
    locale:     Mapped[str]       = mapped_column(String(10), default="fr-FR")
    country:    Mapped[str]       = mapped_column(String(2), default="FR")
    timezone:   Mapped[str]       = mapped_column(String(50), default="Europe/Paris")
    status:     Mapped[str]       = mapped_column(String(20), default="unverified")
    created_at: Mapped[datetime]  = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime]  = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Colonnes PII chiffrées ---
    first_name: Mapped[str]        = mapped_column(EncryptedString(150))
    last_name:  Mapped[str]        = mapped_column(EncryptedString(150))
    email:      Mapped[str]        = mapped_column(EncryptedString(255))
    phone:      Mapped[str | None] = mapped_column(EncryptedString(20))
    google_sub: Mapped[str | None] = mapped_column(EncryptedString(255))

    # --- Colonnes de recherche (non-PII, indexées) ---
    # email_hash : SHA-256(lower(email)) → lookup unique sans scan chiffré
    email_hash:   Mapped[str]        = mapped_column(String(64), unique=True, index=True, nullable=False)
    # search_token : unaccent+lower(prénom + ' ' + nom) → recherche fulltext/trigram
    # Exemple : "Marie-Hélène Dubois" → "marie-helene dubois"
    # Index GIN pg_trgm → supporte LIKE '%query%' et similarity() performants
    search_token: Mapped[str]        = mapped_column(String(300), nullable=False, default="")

    __table_args__ = (
        # Index GIN trigram sur search_token — requiert l'extension pg_trgm
        # (déjà activée dans backend/docker/init-db.sql)
        Index(
            "ix_users_search_token_gin",
            "search_token",
            postgresql_using="gin",
            postgresql_ops={"search_token": "gin_trgm_ops"},
        ),
    )

    @validates("email")
    def _sync_email_hash(self, key, value):
        """Synchronise email_hash à chaque modification de email."""
        if value:
            self.email_hash = hashlib.sha256(value.strip().lower().encode()).hexdigest()
        return value

    @validates("first_name", "last_name")
    def _sync_search_token(self, key, value):
        """
        Reconstruit search_token à chaque changement de prénom ou de nom.
        SQLAlchemy appelle @validates avant le chiffrement EncryptedString,
        donc `value` est toujours en clair ici.
        """
        current_first = self.first_name or ""
        current_last  = self.last_name  or ""
        if key == "first_name":
            new_token = _normalize_for_search(f"{value} {current_last}")
        else:
            new_token = _normalize_for_search(f"{current_first} {value}")
        self.search_token = new_token
        return value
```

#### Repository : lookup par email + recherche coach

```python
# app/repositories/user_repository.py
from sqlalchemy import select, func
from app.core.encryption import hash_for_lookup, _normalize_for_search


class UserRepository:

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Lookup via email_hash (index), jamais via scan du champ chiffré."""
        h = hash_for_lookup(email)
        result = await db.execute(select(User).where(User.email_hash == h))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: UserCreate) -> User:
        user = User(
            first_name=data.first_name,   # @validates → search_token mis à jour
            last_name=data.last_name,
            email=data.email,             # @validates → email_hash mis à jour
            role=data.role,
        )
        db.add(user)
        await db.flush()
        return user


class CoachRepository:

    async def search(
        self,
        db: AsyncSession,
        query: str | None = None,
        specialty: str | None = None,
        country: str | None = None,
        max_price_cents: int | None = None,
        discovery_only: bool = False,
        certified_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        """
        Recherche fulltext sur search_token (pg_trgm) + filtres métier.
        La recherche est insensible aux accents et à la casse.
        """
        stmt = (
            select(User)
            .join(CoachProfile, CoachProfile.id == User.id)
            .where(User.role == "coach", User.status == "active")
        )

        # Recherche par nom — trigram similarity sur search_token (non-PII, indexé)
        if query:
            normalized_q = _normalize_for_search(query)
            stmt = stmt.where(User.search_token.ilike(f"%{normalized_q}%"))
            # Alternative : similarity score pour fuzzy matching
            # stmt = stmt.where(func.similarity(User.search_token, normalized_q) > 0.2)
            # stmt = stmt.order_by(func.similarity(User.search_token, normalized_q).desc())

        # Filtres non-PII (colonnes plain, indexables normalement)
        if country:
            stmt = stmt.where(User.country == country)
        if specialty:
            stmt = stmt.join(CoachSpecialty).where(CoachSpecialty.specialty == specialty)
        if max_price_cents:
            stmt = stmt.where(CoachProfile.unit_price_cents <= max_price_cents)
        if discovery_only:
            stmt = stmt.where(CoachProfile.discovery_session_enabled == True)
        if certified_only:
            stmt = stmt.where(CoachProfile.is_certified == True)

        total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
        result = await db.execute(stmt.offset(offset).limit(limit))
        return result.scalars().all(), total
```

#### Schéma Pydantic avec validation longueur

```python
# app/schemas/auth.py
from pydantic import BaseModel, field_validator, EmailStr
from typing import Annotated
from pydantic import Field


class UserRegister(BaseModel):
    first_name: Annotated[str, Field(min_length=2, max_length=150)]
    last_name:  Annotated[str, Field(min_length=2, max_length=150)]
    email:      EmailStr
    password:   Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Minimum 2 caractères")
        return v
```

#### Migration Alembic : taille des colonnes chiffrées + colonnes de recherche

```python
# alembic/versions/xxxx_users_pii_encryption.py
"""
Colonnes PII : chiffrées Fernet → taille SQL ≈ plaintext_max × 2 + 100
  first_name(150) → VARCHAR(400)
  last_name(150)  → VARCHAR(400)
  email(255)      → VARCHAR(610)
  phone(20)       → VARCHAR(150)

Colonnes de recherche plain (non-PII) :
  email_hash    → CHAR(64)      SHA-256 hex
  search_token  → VARCHAR(300)  unaccent+lower(prénom + ' ' + nom)
                  Index GIN pg_trgm pour recherche fulltext rapide
"""
import sqlalchemy as sa
from alembic import op


def upgrade():
    # Colonnes PII chiffrées
    op.add_column("users", sa.Column("first_name",  sa.String(400), nullable=False, server_default=""))
    op.add_column("users", sa.Column("last_name",   sa.String(400), nullable=False, server_default=""))
    op.add_column("users", sa.Column("email",       sa.String(610), nullable=False, server_default=""))
    op.add_column("users", sa.Column("phone",       sa.String(150), nullable=True))
    op.add_column("users", sa.Column("google_sub",  sa.String(610), nullable=True))

    # Colonnes de lookup / recherche (plain, indexées)
    op.add_column("users", sa.Column("email_hash",   sa.String(64),  nullable=False, server_default=""))
    op.add_column("users", sa.Column("search_token", sa.String(300), nullable=False, server_default=""))

    # Index unique sur email_hash (lookup rapide O(1))
    op.create_index("ix_users_email_hash", "users", ["email_hash"], unique=True)

    # Index GIN trigram sur search_token (fulltext sur noms)
    # Requiert : CREATE EXTENSION IF NOT EXISTS pg_trgm (dans init-db.sql)
    op.execute(
        "CREATE INDEX ix_users_search_token_gin ON users "
        "USING gin (search_token gin_trgm_ops)"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_users_search_token_gin")
    op.drop_index("ix_users_email_hash", table_name="users")
    for col in ["first_name", "last_name", "email", "phone", "google_sub",
                "email_hash", "search_token"]:
        op.drop_column("users", col)
```

#### Champs chiffrés par table (référence complète)

| Table | Champs chiffrés (EncryptedString) | Colonnes de recherche plain (non-PII) |
|-------|----------------------------------|--------------------------------------|
| `users` | `first_name`, `last_name`, `email`, `phone`, `google_sub` | `email_hash` SHA-256 · `search_token` unaccent+lower (GIN) |
| `client_profiles` | `injuries_notes` | — |
| `coach_profiles` | `bio` | — |
| `coach_notes` | `content` | — |
| `payments` | `reference`, `notes` | — |
| `sms_logs` | `body`, `phone_to` | — |
| `integration_tokens` | `access_token`, `refresh_token` | — |
| `cancellation_message_templates` | `body` | — |

> **Règle `search_token`** : jamais loggué, jamais retourné dans les réponses API, utilisé uniquement pour les clauses `WHERE` de recherche. Ce token dérivé n'est pas considéré PII car il ne permet pas de retrouver le nom exact (il est irréversible par design — pas de déchiffrement possible).

#### Variable d'environnement

```env
# .env.dev / .env.prod
# Générer avec : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY=<clé Fernet 32 bytes base64-urlsafe>

# ⚠️ Ne jamais commiter cette clé dans git
# ⚠️ En prod : stocker dans un secret manager (Vault, AWS Secrets Manager, etc.)
# ⚠️ La changer nécessite un script de re-chiffrement sur toute la base
```

---

### 1.10 Architecture Sessions multi-participants + Consommation forfaits

> **Trois décisions architecturales fondamentales (26/02/2026) :**
> 1. `sessions` n'a plus de `client_id` — lien sessions ↔ clients via `session_participants`
> 2. Un client peut avoir plusieurs coachs simultanément — traçabilité `coach_id` sur chaque entité
> 3. Table `package_consumptions` — ligne par crédit, traçabilité complète consommé/dû/en attente

#### Modèle `sessions` — version finale (sans client_id)

```python
# app/models/session.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, Boolean, Enum as SAEnum
import enum


class SessionStatus(str, enum.Enum):
    """Statut global de la session (indépendant du statut par participant)."""
    OPEN        = "open"         # Session créée, accepte des participants
    FULL        = "full"         # Toutes les places confirmées
    DONE        = "done"         # Session réalisée
    CANCELLED   = "cancelled"    # Annulée par le coach (tous participants annulés)


class Session(Base):
    __tablename__ = "sessions"

    id:           Mapped[UUID]      = mapped_column(primary_key=True, default=uuid4)
    coach_id:     Mapped[UUID]      = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    session_type: Mapped[str]       = mapped_column(String(20), nullable=False)   # discovery | coached
    status:       Mapped[str]       = mapped_column(String(20), nullable=False, default="open")
    scheduled_at: Mapped[datetime]  = mapped_column(nullable=False, index=True)   # UTC
    duration_min: Mapped[int]       = mapped_column(SmallInteger, nullable=False)  # 30/45/60/90
    gym_id:       Mapped[UUID|None] = mapped_column(ForeignKey("gyms.id"), nullable=True)
    initiated_by: Mapped[str]       = mapped_column(String(10), nullable=False)    # client | coach
    coach_note:   Mapped[str|None]  = mapped_column(String(300), nullable=True)

    # --- Capacité ---
    max_participants: Mapped[int]   = mapped_column(SmallInteger, nullable=False, default=1)

    # --- Tarification standard ---
    unit_price_cents: Mapped[int|None] = mapped_column(Integer, nullable=True)   # null = hérité du profil coach
    currency:         Mapped[str|None] = mapped_column(String(3), nullable=True) # ISO 4217

    # --- Tarification groupe ---
    # Si nb participants confirmés >= group_price_threshold → price_cents par participant = group_price_cents
    group_price_threshold: Mapped[int|None] = mapped_column(SmallInteger, nullable=True)  # ex: 2
    group_price_cents:     Mapped[int|None] = mapped_column(Integer, nullable=True)        # ex: 5000 = 50€

    # --- Annulation globale (coach annule toute la session) ---
    cancellation_reason: Mapped[str|None] = mapped_column(String(500), nullable=True)
    cancelled_at:        Mapped[datetime|None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    participants: Mapped[list["SessionParticipant"]] = relationship(back_populates="session", cascade="all, delete-orphan")
```

#### Modèle `session_participants` — statut et prix par client

```python
# app/models/session_participant.py
import enum


class ParticipantStatus(str, enum.Enum):
    """
    Machine d'état PAR participant (remplace l'ancienne machine d'état de sessions).
    Chaque client dans une session a son propre cycle de vie.
    """
    PENDING_COACH_VALIDATION  = "pending_coach_validation"
    PROPOSED_BY_COACH         = "proposed_by_coach"
    CONFIRMED                 = "confirmed"
    REJECTED                  = "rejected"
    AUTO_REJECTED             = "auto_rejected"        # 24h sans réponse coach
    CANCELLED_BY_CLIENT       = "cancelled_by_client"
    CANCELLED_LATE_BY_CLIENT  = "cancelled_late_by_client"
    CANCELLED_BY_COACH        = "cancelled_by_coach"
    CANCELLED_BY_COACH_LATE   = "cancelled_by_coach_late"
    NO_SHOW                   = "no_show"
    DONE                      = "done"


class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id:         Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    client_id:  Mapped[UUID] = mapped_column(ForeignKey("users.id"),    nullable=False, index=True)

    # Statut individuel de ce participant dans cette session
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending_coach_validation")

    # Prix appliqué à CE participant (peut différer du tarif standard si groupe)
    price_cents: Mapped[int|None] = mapped_column(Integer, nullable=True)
    currency:    Mapped[str|None] = mapped_column(String(3), nullable=True)

    # Communication
    client_message: Mapped[str|None] = mapped_column(EncryptedString(300), nullable=True)
    initiated_by:   Mapped[str]      = mapped_column(String(10), nullable=False)  # client | coach

    # Annulation individuelle
    cancelled_at:        Mapped[datetime|None] = mapped_column(nullable=True)
    is_late_cancellation: Mapped[bool]         = mapped_column(Boolean, nullable=False, default=False)

    # Pénalité
    penalty_waived:        Mapped[bool]         = mapped_column(Boolean, nullable=False, default=False)
    penalty_waived_reason: Mapped[str|None]     = mapped_column(String(200), nullable=True)

    # Crédit compensatoire (si coach annule tardivement)
    compensatory_credit_cents: Mapped[int|None] = mapped_column(Integer, nullable=True)
    compensatory_currency:     Mapped[str|None] = mapped_column(String(3), nullable=True)

    # No-show
    noshow_marked:    Mapped[bool]          = mapped_column(Boolean, nullable=False, default=False)
    noshow_marked_at: Mapped[datetime|None] = mapped_column(nullable=True)

    # Expiration validation automatique
    auto_reject_deadline: Mapped[datetime|None] = mapped_column(nullable=True)  # scheduled_at - 24h

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "client_id", name="uq_session_participant"),
    )

    # Relations
    session:      Mapped["Session"]      = relationship(back_populates="participants")
    consumption:  Mapped["PackageConsumption|None"] = relationship(back_populates="session_participant", uselist=False)
```

#### Logique de recalcul du tarif groupe (service)

```python
# app/services/session_service.py

async def _recalculate_group_pricing(
    db: AsyncSession,
    session: Session,
) -> None:
    """
    Appelé à chaque fois qu'un participant passe en statut 'confirmed'.
    Si le nombre de participants confirmés atteint group_price_threshold,
    on met à jour price_cents de TOUS les participants confirmés.
    """
    if not session.group_price_threshold or not session.group_price_cents:
        return  # Pas de tarif groupe défini

    confirmed_participants = [
        p for p in session.participants
        if p.status == ParticipantStatus.CONFIRMED
    ]

    if len(confirmed_participants) >= session.group_price_threshold:
        for participant in confirmed_participants:
            participant.price_cents = session.group_price_cents
            participant.currency    = session.currency

    await db.flush()
```

---

#### Modèle `package_consumptions` — traçabilité complète des crédits

```python
# app/models/package_consumption.py
import enum


class ConsumptionStatus(str, enum.Enum):
    PENDING   = "pending"    # Séance planifiée, pas encore réalisée — "En attente de consommation"
    CONSUMED  = "consumed"   # Séance réalisée — "Consommé"
    DUE       = "due"        # Annulation tardive ou no-show — "Due" (crédit débité sans séance)
    WAIVED    = "waived"     # Pénalité exonérée par le coach


class PackageConsumption(Base):
    """
    Une ligne par crédit-séance dans un forfait client.
    Créée à la confirmation d'une session, mise à jour selon le déroulé.

    Structure demandée par le product owner :
      Id_pack · Id_Payment · Id_Client · Temps (min) · Date planif · Status
    """
    __tablename__ = "package_consumptions"

    id:         Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # --- Qui, quoi, d'où ---
    package_id:             Mapped[UUID]      = mapped_column(ForeignKey("client_packages.id"), nullable=False, index=True)
    payment_id:             Mapped[UUID|None] = mapped_column(ForeignKey("payments.id"),        nullable=True)
    client_id:              Mapped[UUID]      = mapped_column(ForeignKey("users.id"),           nullable=False, index=True)
    coach_id:               Mapped[UUID]      = mapped_column(ForeignKey("users.id"),           nullable=False)  # traçabilité multi-coach
    session_id:             Mapped[UUID|None] = mapped_column(ForeignKey("sessions.id"),        nullable=True)
    session_participant_id: Mapped[UUID|None] = mapped_column(ForeignKey("session_participants.id"), nullable=True, unique=True)

    # --- Durée et planning ---
    duration_min: Mapped[int]      = mapped_column(SmallInteger, nullable=False)   # minutes associées
    scheduled_at: Mapped[datetime] = mapped_column(nullable=False, index=True)     # date de planification (UTC)

    # --- Statut ---
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # --- Timestamps d'événements ---
    consumed_at: Mapped[datetime|None] = mapped_column(nullable=True)  # quand session → done
    due_at:      Mapped[datetime|None] = mapped_column(nullable=True)  # quand annulation tardive / no-show
    waived_at:   Mapped[datetime|None] = mapped_column(nullable=True)  # quand exonération coach
    waived_reason: Mapped[str|None]   = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relations
    package:            Mapped["ClientPackage"]             = relationship()
    session_participant: Mapped["SessionParticipant|None"] = relationship(back_populates="consumption")
```

#### Service de gestion des consommations

```python
# app/services/consumption_service.py

async def create_pending_consumption(
    db: AsyncSession,
    participant: SessionParticipant,
    package: ClientPackage,
    payment_id: UUID | None = None,
) -> PackageConsumption:
    """
    Appelé quand un participant est confirmé sur une session.
    Crée une ligne 'pending' dans package_consumptions.
    """
    session = participant.session
    consumption = PackageConsumption(
        package_id             = package.id,
        payment_id             = payment_id,
        client_id              = participant.client_id,
        coach_id               = session.coach_id,
        session_id             = session.id,
        session_participant_id = participant.id,
        duration_min           = session.duration_min,
        scheduled_at           = session.scheduled_at,
        status                 = ConsumptionStatus.PENDING,
    )
    db.add(consumption)
    await db.flush()
    return consumption


async def mark_consumed(db: AsyncSession, consumption: PackageConsumption) -> None:
    """Session terminée (done) → crédit consommé."""
    consumption.status     = ConsumptionStatus.CONSUMED
    consumption.consumed_at = datetime.utcnow()
    await db.flush()


async def mark_due(db: AsyncSession, consumption: PackageConsumption) -> None:
    """Annulation tardive ou no-show → crédit dû (débité sans séance réalisée)."""
    consumption.status = ConsumptionStatus.DUE
    consumption.due_at  = datetime.utcnow()
    await db.flush()


async def mark_waived(
    db: AsyncSession,
    consumption: PackageConsumption,
    reason: str,
) -> None:
    """Exonération de pénalité par le coach."""
    consumption.status        = ConsumptionStatus.WAIVED
    consumption.waived_at     = datetime.utcnow()
    consumption.waived_reason = reason
    await db.flush()


async def get_package_summary(
    db: AsyncSession, package_id: UUID
) -> dict:
    """
    Retourne le récapitulatif comptable d'un forfait :
    - Total crédits
    - Consommés (done)
    - Dus (late cancel / no-show)
    - En attente (scheduled)
    - Exonérés
    - Restants (total - consumed - due)
    """
    rows = await db.execute(
        select(PackageConsumption.status, func.count())
        .where(PackageConsumption.package_id == package_id)
        .group_by(PackageConsumption.status)
    )
    counts = {row.status: row.count for row in rows}
    package = await db.get(ClientPackage, package_id)

    consumed = counts.get("consumed", 0)
    due      = counts.get("due", 0)
    pending  = counts.get("pending", 0)
    waived   = counts.get("waived", 0)

    return {
        "total":     package.session_count_total,
        "consumed":  consumed,
        "due":       due,
        "pending":   pending,
        "waived":    waived,
        "remaining": package.session_count_total - consumed - due,
        # NB : les waived ne sont PAS déduits — exonération = crédit récupéré
    }
```

#### Vue d'ensemble des relations clés

```
sessions (1) ─────────────── (N) session_participants
                                        │
                                        │ (1:1)
                                        ▼
                               package_consumptions
                                        │
                              ┌─────────┼──────────┐
                              │         │          │
                         package_id  client_id  coach_id
                              │         │
                              ▼         ▼
                       client_packages  users
                              │
                         payment_id (nullable)
                              │
                              ▼
                           payments
```

#### Traçabilité multi-coach

```python
# Un client peut avoir N coachs simultanément.
# Chaque entité liée à un coach porte un coach_id explicite.

# ✅ Sessions : session.coach_id (le coach qui crée/gère la session)
# ✅ Packages : client_packages.coach_id (le coach qui a créé ce forfait)
# ✅ Consumptions : package_consumptions.coach_id (provenance du crédit)
# ✅ Workout sessions : workout_sessions.input_by (qui a saisi : coach ou client)
# ✅ Coach notes : coach_notes.(coach_id, client_id) — note privée par couple

# Consulter les autres coachs d'un client (lecture seule, pas de restriction) :
async def get_client_coaches(db: AsyncSession, client_id: UUID) -> list[User]:
    result = await db.execute(
        select(User)
        .join(CoachClientRelationship, CoachClientRelationship.coach_id == User.id)
        .where(
            CoachClientRelationship.client_id == client_id,
            CoachClientRelationship.status == "active",
        )
    )
    return result.scalars().all()
    # Retourne tous les coachs actifs — visible par n'importe quel coach du client
```

#### Script de rotation de clé (si nécessaire)

```python
# scripts/rotate_encryption_key.py
"""
Usage : python scripts/rotate_encryption_key.py --old-key OLD --new-key NEW
Re-chiffre tous les champs PII avec la nouvelle clé.
À exécuter en maintenance, avec la base en lecture seule.
"""
from cryptography.fernet import Fernet

def reencrypt_all(old_key: str, new_key: str):
    old = Fernet(old_key.encode())
    new = Fernet(new_key.encode())

    # Pour chaque table/colonne PII : SELECT → decrypt(old) → encrypt(new) → UPDATE
    # ...
```

---

## PARTIE 2 — ANDROID (Kotlin)

### 2.1 Architecture MVVM + Clean Architecture

```
UI Layer          Domain Layer       Data Layer
──────────        ────────────       ──────────
Fragment    ←──── ViewModel  ←────── Repository
Activity           UseCase            ApiService (Retrofit)
Composable                            LocalDao (Room)
                                      DataStore
```

**Règle :** les dépendances vont toujours vers l'intérieur (UI → Domain → Data).
Jamais l'inverse.

---

### 2.2 Pattern UiState (Sealed Class)

```kotlin
// Toujours modéliser l'état UI avec une sealed class
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String, val code: Int? = null) : UiState<Nothing>()
    object Empty : UiState<Nothing>()  // Liste vide, pas une erreur
}

// Dans le ViewModel
class BookingViewModel @Inject constructor(
    private val bookingRepository: BookingRepository
) : ViewModel() {

    private val _bookingsState = MutableStateFlow<UiState<List<Booking>>>(UiState.Loading)
    val bookingsState: StateFlow<UiState<List<Booking>>> = _bookingsState.asStateFlow()

    fun loadBookings() {
        viewModelScope.launch {
            _bookingsState.value = UiState.Loading
            bookingRepository.getUpcomingBookings()
                .onSuccess { _bookingsState.value = UiState.Success(it) }
                .onFailure { _bookingsState.value = UiState.Error(it.localizedMessage ?: "") }
        }
    }
}

// Dans le Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.bookingsState.collectLatest { state ->
        when (state) {
            is UiState.Loading -> showLoader()
            is UiState.Success -> showBookings(state.data)
            is UiState.Error   -> showError(state.message)
            is UiState.Empty   -> showEmptyState()
        }
    }
}
```

---

### 2.3 Pattern Repository Android

```kotlin
// repositories/BookingRepository.kt

class BookingRepositoryImpl @Inject constructor(
    private val api: BookingApiService,
    private val dao: BookingDao,           // Cache Room (optionnel)
) : BookingRepository {

    override suspend fun getUpcomingBookings(): Result<List<Booking>> {
        return runCatching {
            val response = api.getUpcomingBookings()
            if (response.isSuccessful) {
                val bookings = response.body()!!.map { it.toDomain() }
                dao.insertAll(bookings.map { it.toEntity() })  // Cache local
                bookings
            } else {
                throw ApiException(response.code(), response.errorBody()?.string())
            }
        }
    }

    // Fallback offline : retourne le cache si pas de réseau
    override fun getUpcomingBookingsFlow(): Flow<List<Booking>> {
        return dao.getUpcomingBookingsFlow().map { entities ->
            entities.map { it.toDomain() }
        }
    }
}
```

---

### 2.4 Pattern Mapper (Domain ↔ DTO ↔ Entity)

```kotlin
// Ne jamais utiliser les objets réseau (DTO) directement dans l'UI
// Toujours mapper vers des objets Domain

// DTO réseau (auto-généré par Moshi/Gson)
data class BookingDto(
    @Json(name = "id") val id: String,
    @Json(name = "scheduled_at") val scheduledAt: String,  // ISO 8601 UTC
    @Json(name = "price_cents") val priceCents: Int,
    @Json(name = "currency") val currency: String,
    @Json(name = "status") val status: String,
)

// Objet Domain (indépendant de toute couche)
data class Booking(
    val id: UUID,
    val scheduledAt: Instant,   // UTC, type fort
    val priceCents: Int,
    val currency: String,
    val status: BookingStatus,  // Enum typé, pas String
)

// Mapper : DTO → Domain
fun BookingDto.toDomain(): Booking = Booking(
    id = UUID.fromString(id),
    scheduledAt = Instant.parse(scheduledAt),
    priceCents = priceCents,
    currency = currency,
    status = BookingStatus.fromString(status),
)

// Formatter i18n pour l'affichage (dans le Fragment, jamais dans le Domain)
fun Booking.formatPrice(locale: Locale): String =
    PriceFormatter.format(priceCents, currency, locale)

fun Booking.formatDate(timezone: ZoneId, locale: Locale): String =
    DateTimeFormatter
        .ofLocalizedDateTime(FormatStyle.MEDIUM, FormatStyle.SHORT)
        .withLocale(locale)
        .withZone(timezone)
        .format(scheduledAt)
```

---

### 2.5 Pattern Kotlin : Result & Extension Functions

```kotlin
// Utiliser Result<T> pour toutes les opérations qui peuvent échouer
// Ne jamais lancer d'exceptions non catchées dans les ViewModels

// Extension pour mapper les erreurs réseau
suspend fun <T> safeApiCall(call: suspend () -> Response<T>): Result<T> {
    return runCatching {
        val response = call()
        if (response.isSuccessful) {
            response.body() ?: throw EmptyResponseException()
        } else {
            val error = response.errorBody()?.string()?.parseApiError()
            throw ApiException(response.code(), error?.detail ?: "Erreur inconnue")
        }
    }
}

// Usage
override suspend fun confirmBooking(bookingId: UUID): Result<Booking> =
    safeApiCall { api.confirmBooking(bookingId.toString()) }
        .map { it.toDomain() }
```

---

### 2.6 Pattern Kotlin : Sealed Class pour les Actions UI

```kotlin
// Modéliser les actions utilisateur comme des events
sealed class BookingAction {
    data class Confirm(val bookingId: UUID) : BookingAction()
    data class Cancel(val bookingId: UUID, val reason: String?) : BookingAction()
    data class JoinWaitlist(val slotRef: String) : BookingAction()
    object Refresh : BookingAction()
}

// Dans le ViewModel : un seul point d'entrée
fun handleAction(action: BookingAction) {
    when (action) {
        is BookingAction.Confirm     -> confirmBooking(action.bookingId)
        is BookingAction.Cancel      -> cancelBooking(action.bookingId, action.reason)
        is BookingAction.JoinWaitlist -> joinWaitlist(action.slotRef)
        BookingAction.Refresh        -> loadBookings()
    }
}
```

---

### 2.7 Pattern Hilt — Injection de dépendances

```kotlin
// di/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides @Singleton
    fun provideApiKeyStore(@ApplicationContext ctx: Context): ApiKeyStore =
        ApiKeyStore(ctx)

    @Provides @Singleton
    fun provideOkHttpClient(apiKeyStore: ApiKeyStore): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(ApiKeyInterceptor(apiKeyStore))
            .addInterceptor(LocaleInterceptor(apiKeyStore))
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
}

// di/RepositoryModule.kt
@Module
@InstallIn(ViewModelComponent::class)
object RepositoryModule {

    @Provides
    fun provideBookingRepository(
        api: BookingApiService,
        dao: BookingDao,
    ): BookingRepository = BookingRepositoryImpl(api, dao)
}
```

---

### 2.8 Pattern Navigation (Navigation Component)

```kotlin
// Toujours passer par des Actions typées, jamais de strings

// nav_graph.xml définit les destinations et les actions
// Dans le Fragment :
findNavController().navigate(
    BookingListFragmentDirections.actionBookingListToBookingDetail(
        bookingId = booking.id.toString()
    )
)

// Réception des arguments (type-safe)
val args: BookingDetailFragmentArgs by navArgs()
val bookingId = UUID.fromString(args.bookingId)

// Deep links depuis les notifications
// Dans AndroidManifest.xml :
// <deepLink app:uri="mycoach://booking/{bookingId}" />
```

---

### 2.9 Pattern Coroutines — Bonnes pratiques

```kotlin
// ✅ Toujours utiliser viewModelScope dans les ViewModels
// ✅ Toujours utiliser lifecycleScope dans les Fragments
// ❌ Ne jamais utiliser GlobalScope
// ❌ Ne jamais bloquer le thread principal

// ✅ Annulation propre avec structured concurrency
class BookingViewModel : ViewModel() {
    private var refreshJob: Job? = null

    fun refresh() {
        refreshJob?.cancel()  // Annule le job précédent
        refreshJob = viewModelScope.launch {
            // ...
        }
    }
}

// ✅ Parallélisme avec async/await
suspend fun loadDashboard(): Dashboard {
    return coroutineScope {
        val bookings = async { bookingRepo.getUpcoming() }
        val stats    = async { statsRepo.getWeekStats() }
        val alerts   = async { alertRepo.getAlerts() }
        Dashboard(
            bookings = bookings.await().getOrDefault(emptyList()),
            stats    = stats.await().getOrNull(),
            alerts   = alerts.await().getOrDefault(emptyList()),
        )
    }
}
```

---

## PARTIE 3 — OWASP API Security Top 10

Application obligatoire sur **chaque endpoint** du backend.

---

### API1 — Broken Object Level Authorization (BOLA)

**Risque :** Un utilisateur accède aux données d'un autre en changeant l'ID dans l'URL.

```python
# ❌ Vulnérable
@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await booking_repo.get(booking_id)  # N'importe qui peut accéder

# ✅ Sécurisé : toujours vérifier que la ressource appartient à l'utilisateur courant
@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    booking = await booking_repo.get(booking_id)
    if not booking:
        raise HTTPException(404)
    # Vérification ownership
    if booking.client_id != current_user.id and booking.coach_id != current_user.id:
        raise HTTPException(403)  # Forbidden, pas 404 (ne pas révéler l'existence)
    return booking
```

**Règle :** Sur **chaque** endpoint avec un ID en paramètre, vérifier que l'utilisateur courant a le droit d'accéder à cette ressource.

---

### API2 — Broken Authentication

**Risque :** API Key prévisible, pas de rate limiting, pas de révocation.

```python
# ✅ Génération API Key avec sel secret (non prévisible)
def generate_api_key(unique_input: str) -> str:
    salt = settings.API_KEY_SALT  # Variable d'env, min 32 chars aléatoires
    raw = f"{unique_input}{salt}"
    return hashlib.sha256(raw.encode()).hexdigest()

# ✅ Rate limiting sur les endpoints d'auth
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("10/minute")  # Max 10 tentatives/min par IP
async def login(request: Request, body: LoginRequest):
    ...

# ✅ Vérification constante en temps (pas de timing attack)
def verify_api_key(provided: str, stored: str) -> bool:
    return secrets.compare_digest(provided, stored)  # Constant time comparison
```

---

### API3 — Broken Object Property Level Authorization

**Risque :** Un client peut modifier des champs qu'il ne devrait pas (ex: `role`, `verified`).

```python
# ✅ Schémas Pydantic distincts selon le rôle
class ClientProfileUpdate(BaseModel):
    # Seuls les champs que le CLIENT peut modifier
    name: str | None = None
    locale: str | None = None
    weight_unit: WeightUnit | None = None
    # ❌ role, verified, admin : pas dans ce schéma

class AdminUserUpdate(BaseModel):
    role: UserRole | None = None
    verified: bool | None = None

# Utiliser le bon schéma selon l'appelant
@router.put("/clients/profile")
async def update_profile(
    body: ClientProfileUpdate,      # Pas AdminUserUpdate
    current_user: User = Depends(get_current_user),
):
    ...
```

---

### API4 — Unrestricted Resource Consumption

**Risque :** Pagination non limitée, uploads illimités, requêtes coûteuses sans garde-fous.

```python
# ✅ Pagination obligatoire avec limite max
@router.get("/coaches")
async def list_coaches(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),  # Max 100 par page
):
    ...

# ✅ Limite de taille des uploads
@router.post("/profiles/photo")
async def upload_photo(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    if file.size > 5 * 1024 * 1024:  # 5 MB max
        raise HTTPException(413, "Fichier trop volumineux (max 5 MB)")
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(415, "Format non supporté")
    ...

# ✅ Timeout sur les opérations longues
async with asyncio.timeout(30):  # Max 30s pour une opération
    result = await slow_operation()
```

---

### API5 — Broken Function Level Authorization

**Risque :** Un client accède à des endpoints réservés au coach ou à l'admin.

```python
# ✅ Dépendances de rôle réutilisables
async def require_coach(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.COACH:
        raise HTTPException(403, "Réservé aux coachs")
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Réservé aux administrateurs")
    return user

# Appliquer sur chaque route sensible
@router.post("/coaches/programs/{id}/assign")
async def assign_program(
    id: uuid.UUID,
    body: AssignProgramRequest,
    coach: User = Depends(require_coach),  # ← Vérification de rôle
):
    ...

@router.get("/admin/machines/pending")
async def list_pending_machines(
    admin: User = Depends(require_admin),  # ← Vérification admin
):
    ...
```

---

### API6 — Unrestricted Access to Sensitive Business Flows

**Risque :** Un bot peut épuiser les créneaux, spammer les réservations, etc.

```python
# ✅ Rate limiting sur les actions métier sensibles
@router.post("/bookings")
@limiter.limit("20/hour")  # Max 20 réservations par heure par user
async def create_booking(...):
    ...

@router.post("/waitlist/{slot_ref}")
@limiter.limit("50/hour")
async def join_waitlist(...):
    ...

# ✅ Vérification de cohérence métier
async def create_booking_service(client_id, coach_id, slot_datetime):
    # Un client ne peut pas réserver 2 fois le même créneau
    existing = await booking_repo.get_by_slot(client_id, coach_id, slot_datetime)
    if existing:
        raise DuplicateBookingError()
    
    # Un client ne peut pas avoir plus de N réservations en attente
    pending_count = await booking_repo.count_pending(client_id)
    if pending_count >= 5:
        raise TooManyPendingBookingsError()
```

---

### API7 — Server Side Request Forgery (SSRF)

**Risque :** L'app appelle des URLs fournies par l'utilisateur (ex: intégrations).

```python
# ✅ Valider et whitelist les URLs externes
ALLOWED_OAUTH_HOSTS = {
    "accounts.google.com",
    "www.strava.com",
    "account.withings.com",
    "connect.garmin.com",
}

def validate_callback_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_OAUTH_HOSTS:
        raise ValueError(f"Host non autorisé : {parsed.hostname}")
    return url

# Ne jamais faire de requête HTTP vers une URL fournie directement par l'utilisateur
# sans validation préalable
```

---

### API8 — Security Misconfiguration

```python
# ✅ CORS strict (jamais de wildcard en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Pas de "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-API-Key", "Content-Type", "Accept-Language"],
)

# ✅ Headers de sécurité
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Cache-Control"] = "no-store"  # Pour les endpoints sensibles
    return response

# ✅ Ne pas exposer les stack traces en production
if not settings.DEBUG:
    @app.exception_handler(Exception)
    async def generic_handler(request, exc):
        logger.exception("Unhandled error", exc_info=exc)  # Log complet côté serveur
        return JSONResponse(status_code=500, content={"detail": "Erreur interne"})
        # Pas de traceback dans la réponse client !
```

---

### API9 — Improper Inventory Management

```python
# ✅ Versionner les APIs dès le départ
app = FastAPI(title="MyCoach API", version="1.0")
api_v1 = APIRouter(prefix="/v1")

# ✅ Documenter et supprimer les endpoints de debug en production
if settings.DEBUG:
    @router.get("/debug/users")
    async def debug_list_users():
        ...
# En production (DEBUG=False) : cet endpoint n'existe pas

# ✅ Endpoint /health sans informations sensibles
@app.get("/health")
async def health():
    return {"status": "ok"}  # Pas de version DB, pas de config interne
```

---

### API10 — Unsafe Consumption of APIs

```python
# ✅ Valider les réponses des APIs tierces (Google, Strava, Withings)
async def verify_google_token(id_token: str) -> dict:
    try:
        # Ne pas faire confiance au token sans vérification
        claims = id_token_lib.verify_oauth2_token(
            id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        # Vérifier les claims critiques
        if claims["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Émetteur invalide")
        if claims["aud"] != settings.GOOGLE_CLIENT_ID:
            raise ValueError("Audience invalide")
        return claims
    except Exception:
        raise InvalidGoogleTokenError()

# ✅ Timeout sur tous les appels HTTP externes
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get("https://api.strava.com/v3/athlete")
```

---

## PARTIE 4 — OWASP Mobile Top 10 (Android)

---

### M1 — Improper Credential Usage

```kotlin
// ❌ Ne jamais stocker de données sensibles en clair
// SharedPreferences classique = INTERDIT pour les secrets
sharedPrefs.edit().putString("api_key", key).apply()  // ❌

// ✅ EncryptedSharedPreferences obligatoire
class ApiKeyStore @Inject constructor(@ApplicationContext context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "mycoach_secure_prefs",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    fun storeApiKey(key: String) = prefs.edit().putString("api_key", key).apply()
    fun getApiKey(): String? = prefs.getString("api_key", null)
    fun clear() = prefs.edit().clear().apply()
}

// ❌ Ne jamais loguer de données sensibles
Log.d("Auth", "API Key: $apiKey")  // ❌

// ✅ Logs uniquement en DEBUG, jamais de données sensibles
if (BuildConfig.DEBUG) Log.d("Auth", "Login successful for user: ${user.id}")
```

---

### M2 — Inadequate Supply Chain Security

```kotlin
// ✅ Vérifier les dépendances (Gradle dependency verification)
// gradle/verification-metadata.xml

// ✅ Utiliser uniquement des versions stables et maintenues
// ❌ Dépendances abandonnées ou avec CVE connues

// ✅ BuildConfig pour les URLs et configs (jamais en dur)
buildConfigField("String", "API_BASE_URL", "\"${properties["API_BASE_URL"]}\"")

// Usage
val baseUrl = BuildConfig.API_BASE_URL  // ✅
val baseUrl = "http://192.168.1.1:8000" // ❌ Jamais en dur
```

---

### M3 — Insecure Authentication / Authorization

```kotlin
// ✅ Certificate Pinning en production (empêche le MITM)
val certificatePinner = CertificatePinner.Builder()
    .add("api.mycoach.app", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()

// ✅ Biométrie pour les actions sensibles (paiements, suppression compte)
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle(getString(R.string.biometric_confirm_title))
    .setNegativeButtonText(getString(R.string.cancel))
    .build()

val biometricPrompt = BiometricPrompt(this, executor, object : BiometricPrompt.AuthenticationCallback() {
    override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
        viewModel.confirmSensitiveAction()
    }
    override fun onAuthenticationFailed() {
        showError(getString(R.string.error_biometric_failed))
    }
})
```

---

### M4 — Insufficient Input/Output Validation

```kotlin
// ✅ Valider les inputs côté client (en complément de la validation serveur)
fun validateEmail(email: String): String? {
    return if (!Patterns.EMAIL_ADDRESS.matcher(email).matches())
        getString(R.string.error_invalid_email)
    else null
}

fun validatePassword(password: String): String? {
    return when {
        password.length < 8 -> getString(R.string.error_password_too_short)
        !password.any { it.isUpperCase() } -> getString(R.string.error_password_uppercase)
        !password.any { it.isDigit() } -> getString(R.string.error_password_digit)
        else -> null
    }
}

// ✅ Sanitize les inputs avant affichage (prévenir XSS dans les WebViews)
fun sanitizeText(input: String): String =
    input.replace("<", "&lt;").replace(">", "&gt;")

// ✅ Valider les données reçues du serveur avant affichage
// Ne pas assumer que le serveur retourne des données valides
val weight = response.weightKg?.takeIf { it > 0 && it < 500 }
    ?: throw InvalidServerDataException("Poids invalide")
```

---

### M5 — Insecure Communication

```kotlin
// ✅ HTTPS obligatoire, HTTP interdit en production
// res/xml/network_security_config.xml
/*
<network-security-config>
    <base-config cleartextTrafficPermitted="false">  <!-- Interdit HTTP -->
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />  <!-- Charles Proxy en debug uniquement -->
        </trust-anchors>
    </debug-overrides>
</network-security-config>
*/

// AndroidManifest.xml
// android:networkSecurityConfig="@xml/network_security_config"
```

---

### M6 — Inadequate Privacy Controls

```kotlin
// ✅ Demander les permissions au moment opportun, pas au démarrage
// Caméra : uniquement lors du scan QR ou de l'upload photo
private val cameraPermissionLauncher = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted ->
    if (granted) openCamera()
    else showPermissionRationale()
}

// ✅ Déclarer uniquement les permissions nécessaires dans le Manifest
// ❌ ACCESS_FINE_LOCATION si seul le pays est nécessaire (utiliser le profil user)

// ✅ Effacer les données sensibles à la déconnexion
fun logout() {
    apiKeyStore.clear()
    database.clearAllTables()  // Room
    // Vider les caches Retrofit/Glide
    Glide.get(context).clearMemory()
    viewModelScope.launch { Glide.get(context).clearDiskCache() }
}
```

---

### M7 — Insufficient Binary Protections

```kotlin
// ✅ Activer ProGuard/R8 en release
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

// ✅ Règles ProGuard pour les modèles Retrofit/Moshi
// proguard-rules.pro
// -keep class com.mycoach.app.data.remote.dto.** { *; }
// -keepattributes Signature, *Annotation*
```

---

### M8 — Security Misconfiguration

```kotlin
// ✅ Désactiver le backup automatique des données sensibles
// AndroidManifest.xml
// android:allowBackup="false"
// android:fullBackupContent="@xml/backup_rules"

// backup_rules.xml : exclure les données chiffrées
/*
<full-backup-content>
    <exclude domain="sharedpref" path="mycoach_secure_prefs.xml" />
    <exclude domain="database" path="mycoach.db" />
</full-backup-content>
*/

// ✅ Pas de logs en production
// Utiliser Timber avec des Trees conditionnels
Timber.plant(
    if (BuildConfig.DEBUG) Timber.DebugTree()
    else CrashReportingTree()  // Envoie uniquement les erreurs critiques à Crashlytics
)
```

---

### M9 — Insecure Data Storage

```kotlin
// ✅ Règle absolue de stockage selon la sensibilité

// DONNÉES SENSIBLES (API Key, tokens OAuth) → EncryptedSharedPreferences
// DONNÉES UTILISATEUR NON-PII (IDs, statuts, timestamps) → Room plain
// DONNÉES PII (prénom, nom, email, téléphone) → NE PAS cacher en local
// DONNÉES NON SENSIBLES (préférences UI, thème) → DataStore plain
// FICHIERS TEMPORAIRES (photos avant upload) → getCacheDir() + suppression après

// ✅ Règle PII Android : les champs personnels ne sont JAMAIS stockés en clair dans Room
// Les champs PII (first_name, last_name, email, phone) sont toujours re-fetchés depuis l'API.
// Si un cache de profil est absolument nécessaire (mode offline), chiffrer avant insertion :

class EncryptedProfileCache(context: Context) {
    // Utiliser SQLCipher pour Room ou chiffrement au niveau colonne via Android Keystore
    private val keyAlias = "mycoach_profile_key"

    fun encryptPiiField(value: String): String {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val key = keyStore.getKey(keyAlias, null) as SecretKey
        cipher.init(Cipher.ENCRYPT_MODE, key)
        val iv = cipher.iv
        val encrypted = cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        // Stocker iv + encrypted concaténés en base64
        return Base64.encodeToString(iv + encrypted, Base64.NO_WRAP)
    }

    fun decryptPiiField(stored: String): String {
        val raw = Base64.decode(stored, Base64.NO_WRAP)
        val iv = raw.sliceArray(0 until 12)
        val encrypted = raw.sliceArray(12 until raw.size)
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, keyStore.getKey(keyAlias, null) as SecretKey, GCMParameterSpec(128, iv))
        return String(cipher.doFinal(encrypted), Charsets.UTF_8)
    }
}

// ✅ Validation de longueur prénom / nom (international : max 150 chars)
// Dans le Fragment / Activity :
val nameFilter = InputFilter.LengthFilter(150)
binding.etFirstName.filters = arrayOf(nameFilter)
binding.etLastName.filters = arrayOf(nameFilter)

// ✅ Validation Kotlin côté ViewModel :
fun validateName(name: String): String? {
    return when {
        name.isBlank()    -> getString(R.string.error_name_required)
        name.length < 2   -> getString(R.string.error_name_too_short)
        name.length > 150 -> getString(R.string.error_name_too_long)
        else              -> null  // valide
    }
}

// ✅ Ne pas logger l'écran sur les écrans sensibles (clavier, paiement)
override fun onResume() {
    super.onResume()
    // Sur l'écran de paiement ou de login
    window.setFlags(
        WindowManager.LayoutParams.FLAG_SECURE,
        WindowManager.LayoutParams.FLAG_SECURE
    )
    // Empêche les screenshots et l'apparition dans le task switcher
}
```

---

### M10 — Insufficient Cryptography

```kotlin
// ✅ Utiliser uniquement des algorithmes modernes
// AES-256-GCM pour le chiffrement symétrique (via Android Keystore)
// SHA-256 minimum pour les hashs
// RSA-2048 ou ECDSA-P256 pour les signatures

// ❌ Ne jamais utiliser :
// MD5, SHA-1 (deprecated)
// ECB mode pour AES (pas de IV = déterministe = vulnérable)
// Random() au lieu de SecureRandom() pour les valeurs cryptographiques

// ✅ Android Keystore pour les clés cryptographiques
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_AES,
    "AndroidKeyStore"  // Stockage matériel si disponible (TEE/StrongBox)
)
keyGenerator.init(
    KeyGenParameterSpec.Builder("mycoach_key", KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
        .setKeySize(256)
        .setUserAuthenticationRequired(false)
        .build()
)
```

---

## PARTIE 5 — CHECKLIST SÉCURITÉ PAR ENDPOINT

À appliquer sur **chaque endpoint backend** avant de le considérer terminé :

```
□ Middleware API Key appliqué (sauf /auth/* et /health)
□ Vérification BOLA : la ressource appartient bien à l'utilisateur courant
□ Vérification rôle : Coach / Client / Admin selon le cas
□ Validation Pydantic sur le body (pas de champ manquant ou non typé)
□ Schéma de réponse explicite (pas de retour direct du modèle ORM)
□ Rate limiting sur les endpoints à risque
□ Pas de stack trace dans les réponses d'erreur
□ Pas de données sensibles dans les logs
□ Pagination avec limite max sur les listes
□ Validation des fichiers uploadés (MIME + taille)
□ Champs PII écrits via EncryptedString (jamais en clair en base)
□ Lookup email via email_hash (jamais WHERE email = ?)
□ FIELD_ENCRYPTION_KEY chargée depuis l'environnement, jamais hardcodée
```

## CHECKLIST SÉCURITÉ PAR ÉCRAN ANDROID

À appliquer sur **chaque écran** avant de le considérer terminé :

```
□ Aucune string UI codée en dur (tout dans strings.xml)
□ Aucune donnée sensible dans les logs (pas en release)
□ Aucun appel réseau depuis le thread principal
□ État UI modélisé avec UiState<T>
□ Erreurs affichées via strings.xml (i18n)
□ FLAG_SECURE activé si l'écran contient des données sensibles
□ Permissions demandées au moment opportun (pas au démarrage)
□ API Key et tokens OAuth dans EncryptedSharedPreferences uniquement
□ Champs PII (prénom, nom, email, téléphone) jamais stockés en clair dans Room
□ Validation longueur prénom/nom : min 2, max 150 chars (InputFilter + ViewModel)
□ Formatage des montants / dates / poids via les formatters i18n
□ Données effacées à la déconnexion (EncryptedSharedPreferences + Room.clearAllTables)
```

---

*Version 1.2 — 26/02/2026 — §1.10 Architecture sessions multi-participants : session_participants (statut/prix par client), tarif groupe (seuil N → recalcul), package_consumptions (pending/consumed/due/waived), multi-coach traçabilité coach_id*
*Version 1.1 — 26/02/2026 — §1.9 PII Encryption + search_token + M9 Android PII rules + checklists*
*Version 1.0 — 25/02/2026 — Document initial*
*À relire avant chaque session de développement*
