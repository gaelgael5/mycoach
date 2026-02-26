# MyCoach — Guide Méthodologique pour Agent IA Codeur

> Ce document est destiné à un agent IA qui va implémenter l'application MyCoach de A à Z.
> Il définit la méthodologie stricte à suivre, l'ordre des tâches, les standards de code et les règles non négociables.
> **Ne jamais commencer une tâche sans avoir lu et compris ce document en entier.**

---

## 0. AVANT DE COMMENCER — LECTURES OBLIGATOIRES

Dans cet ordre strict :

1. `docs/FUNCTIONAL_SPECS.md` — Vue d'ensemble fonctionnelle, modèle de données, intégrations
2. `docs/FUNCTIONAL_SPECS_DETAILED.md` — Détail de chaque écran, action, validation, règle métier
3. `docs/DEV_ROADMAP.md` — Phases de développement, stack technique, décisions arrêtées
4. `docs/DEV_PATTERNS.md` — Patterns d'architecture, design patterns Python/Kotlin, OWASP API Top 10, OWASP Mobile Top 10
5. `docs/CODING_AGENT.md` — Ce fichier (méthodologie d'exécution)

**Tu ne peux pas commencer à coder avant d'avoir lu les 4 documents.**
Si un document manque ou est incomplet, signale-le avant de continuer.

---

## 1. PRINCIPES FONDAMENTAUX

### 1.1 Une tâche à la fois
- Traite **une seule tâche** de la liste à la fois
- Ne passe à la suivante qu'après avoir **terminé, testé et validé** la courante
- Chaque tâche doit produire du code qui **fonctionne** — pas un squelette, pas un placeholder

### 1.2 Toujours dans l'ordre
- Respecte **scrupuleusement l'ordre des phases** (Phase 0 → 1 → 2 → … → 6)
- Au sein d'une phase, respecte l'ordre des tâches tel que défini dans la liste ci-dessous
- Ne saute jamais une tâche en te disant "je la ferai plus tard"

### 1.3 Zéro dette technique dès le départ
- Chaque fichier produit doit respecter les standards de code définis en §3
- **Pas de TODO**, pas de `// fix this later`, pas de `pass` non justifié
- Si quelque chose est complexe et doit attendre, documente-le dans `docs/BACKLOG.md` (crée-le si nécessaire)

### 1.4 L'i18n n'est pas optionnelle
- **Aucune chaîne de caractères codée en dur** dans le code Android ou Backend
- Dès le premier fichier `.kt` ou `.py` produit, i18n est en place
- Voir §4 pour les règles détaillées

### 1.5 Chaque tâche = un commit Git propre (avec les tests)

> **Règle absolue : une tâche n'existe que si ses tests existent et passent.**
> Le commit n'est valide que s'il contient à la fois le code de la feature ET ses tests.

- Format du message de commit : `[PHASE-X][TASK-Y] Description courte`
- Exemple : `[PHASE-0][TASK-3] Auth API Key - Google OAuth flow + tests`
- Le suffixe `+ tests` est obligatoire pour rappeler que les tests font partie du commit
- **Ne jamais séparer** le code d'une feature et ses tests dans deux commits distincts
- Ne pas regrouper plusieurs tâches dans un seul commit
- Branche : `main` (projet solo) ou créer des branches feature si spécifié

**Ce qui doit être dans chaque commit :**
```
✅ Code de la feature (models, schemas, repo, service, router / ViewModel, UI)
✅ Tests couvrant les cas passants (happy path)
✅ Tests couvrant les cas non passants (erreurs, invalide, limites)
✅ Mise à jour de docs/PROGRESS.md (tâche = ✅)
```

**Ce qui ne doit PAS être dans un commit :**
```
❌ Code fonctionnel sans tests associés
❌ Tests seuls sans le code qu'ils testent
❌ Tâche marquée ✅ dans PROGRESS.md si les tests ne passent pas à 100%
```

---

## 2. MÉTHODOLOGIE D'EXÉCUTION PAR TÂCHE

Pour chaque tâche de la liste, applique **exactement** ces étapes dans l'ordre :

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 — LIRE                                             │
│  Lis la section correspondante dans FUNCTIONAL_SPECS_       │
│  DETAILED.md. Comprends toutes les règles métier, les       │
│  validations, les cas d'erreur, les notifications.          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 2 — PLANIFIER                                        │
│  Identifie les fichiers à créer/modifier.                   │
│  Identifie les dépendances (tables BDD, endpoints, etc.)    │
│  Note les cas limites (edge cases) à gérer.                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 3 — IMPLÉMENTER                                      │
│  Code la fonctionnalité complète, selon les standards §3.   │
│  Backend d'abord (modèle → repository → service → route),   │
│  puis Android (ViewModel → Repository → UI).                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 4 — TESTER  ← OBLIGATOIRE, NON NÉGOCIABLE           │
│                                                             │
│  Pour chaque fonction/endpoint/écran implémenté,            │
│  tu dois écrire DES DEUX types de tests :                   │
│                                                             │
│  ✅ CAS PASSANTS (happy path)                               │
│    - L'appel nominal fonctionne et retourne le bon résultat │
│    - Chaque chemin logique "succès" est couvert             │
│    - Les données retournées sont conformes au schéma        │
│                                                             │
│  ❌ CAS NON PASSANTS (error cases)                          │
│    - Champ obligatoire manquant → erreur attendue           │
│    - Valeur invalide (type, format, plage) → erreur         │
│    - Doublon / contrainte unicité → erreur                  │
│    - Accès non autorisé (autre user, rôle insuffisant)      │
│    - Ressource inexistante (404)                            │
│    - Limite métier dépassée (ex: max 5 templates)           │
│    - Règle temporelle violée (ex: annulation < 24h)         │
│                                                             │
│  RÈGLE : au minimum 1 test passant + 1 test non passant     │
│  par fonction de service / endpoint / ViewModel             │
│                                                             │
│  Backend : pytest + pytest-asyncio, base PostgreSQL test    │
│  Android : JUnit5 + MockK/Mockito, coroutines test          │
│                                                             │
│  Lance : pytest (backend) ou ./gradlew test (Android)       │
│  ⛔ Si un test échoue → corriger le code, pas le test       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 5 — VALIDER                                          │
│  Relis le code produit et vérifie :                         │
│  ✓ i18n respectée (aucune string codée en dur)              │
│  ✓ Standards de code §3 respectés                           │
│  ✓ Tous les cas d'erreur des specs sont couverts            │
│  ✓ Le modèle de données correspond aux specs                │
│  ✓ Tous les tests passent (0 failure, 0 error)              │
│  ✓ Couverture : au moins 1 cas passant + 1 non passant      │
│    par fonction de service / par endpoint / par ViewModel   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 6 — COMMITER (code + tests ensemble)                 │
│  `git add .`                                                │
│  `git commit -m "[PHASE-X][TASK-Y] Description + tests"`    │
│  Mets à jour `docs/PROGRESS.md` (tâche = ✅)               │
│                                                             │
│  ⛔ Commit INTERDIT si :                                    │
│    - Tests manquants pour la feature committée              │
│    - Un test échoue (rouge)                                 │
│    - PROGRESS.md non mis à jour                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. STANDARDS DE CODE

### 3.1 Backend (FastAPI / Python)

**Structure des dossiers :**
```
backend/
├── alembic/              ← migrations de schéma
├── app/
│   ├── main.py           ← point d'entrée FastAPI
│   ├── config.py         ← variables d'environnement (pydantic-settings)
│   ├── database.py       ← session AsyncSession + engine
│   ├── auth/             ← middleware API Key, routes /auth/*
│   ├── models/           ← modèles SQLAlchemy (1 fichier par entité)
│   ├── schemas/          ← schémas Pydantic (request + response, 1 fichier par domaine)
│   ├── repositories/     ← accès BDD (1 fichier par entité, aucune logique métier)
│   ├── services/         ← logique métier (1 fichier par domaine)
│   ├── routers/          ← routes FastAPI (1 fichier par domaine)
│   ├── locales/          ← fichiers i18n JSON (fr.json, en.json, es.json…)
│   └── utils/            ← helpers (hashing, date conversion, etc.)
├── tests/                ← tests pytest (miroir de app/)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

**Règles Python :**
- Python 3.12+
- Type hints sur toutes les fonctions (pas d'`Any` sauf justification)
- Docstrings sur les services et repositories
- `async/await` partout (pas de code synchrone bloquant)
- Pas de logique métier dans les routers (uniquement validation + appel service)
- Pas d'accès BDD dans les services (uniquement via repositories)
- Variables d'environnement via `pydantic-settings` — jamais en dur dans le code
- Toutes les réponses d'erreur : `{"detail": i18n_message(locale, "error.key")}`

**Nommage :**
- Fichiers : `snake_case.py`
- Classes : `PascalCase`
- Fonctions/variables : `snake_case`
- Constantes : `UPPER_SNAKE_CASE`
- Tables BDD : `snake_case` au pluriel (`api_keys`, `coach_profiles`)
- Colonnes BDD : `snake_case`

**Modèles SQLAlchemy :**
```python
# Toujours : id UUID, timestamps, soft delete si applicable
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
```

**Montants monétaires :**
- Toujours en **centimes** (entier) en base : `price_cents: Mapped[int]`
- Toujours avec **code devise ISO 4217** : `currency: Mapped[str]`  (ex: `"EUR"`)
- Jamais de `float` pour les montants

**Dates :**
- Toujours UTC en base : `datetime.utcnow()` ou `func.now()`
- Conversion vers timezone utilisateur uniquement dans les réponses API (via `user.timezone`)

---

### 3.2 Android (Kotlin)

**Structure des dossiers :**
```
android/app/src/main/
├── kotlin/com/mycoach/app/
│   ├── MyCoachApplication.kt     ← init DI, Hilt
│   ├── MainActivity.kt           ← NavHost, bottom nav
│   ├── auth/                     ← login, register, role selection
│   ├── coach/                    ← tous les écrans coach
│   │   ├── dashboard/
│   │   ├── clients/
│   │   ├── agenda/
│   │   ├── programs/
│   │   └── payments/
│   ├── client/                   ← tous les écrans client
│   │   ├── dashboard/
│   │   ├── search/
│   │   ├── booking/
│   │   ├── performances/
│   │   └── solo/
│   ├── shared/                   ← composants partagés coach+client
│   │   ├── ui/                   ← design system (couleurs, typo, composants)
│   │   ├── network/              ← ApiClient, ApiKeyInterceptor
│   │   ├── data/                 ← Room, DataStore, repositories
│   │   └── utils/                ← extensions, formatters i18n
│   └── backoffice/               ← écrans admin (si dans la même app)
├── res/
│   ├── values/strings.xml        ← langue par défaut (EN)
│   ├── values-fr/strings.xml     ← Français
│   ├── values-es/strings.xml     ← Espagnol
│   └── values-pt/strings.xml     ← Portugais BR
└── AndroidManifest.xml
```

**Règles Kotlin :**
- Architecture MVVM : `Screen → ViewModel → Repository → ApiService`
- Un `ViewModel` par écran, pas de logique dans les Fragments/Activities
- Coroutines + Flow pour tout ce qui est async
- Hilt pour l'injection de dépendances
- `StateFlow<UiState>` pour l'état UI : `Loading | Success(data) | Error(message)`
- Jamais d'appel réseau dans un Fragment ou Activity

**Nommage :**
- Fichiers : `PascalCase.kt`
- Classes/Interfaces : `PascalCase`
- Fonctions/variables : `camelCase`
- Constantes : `UPPER_SNAKE_CASE`
- Resources XML : `snake_case`
- IDs XML : `camelCase` (ex: `android:id="@+id/btnConfirm"`)

**i18n Android — règle absolue :**
```kotlin
// ❌ JAMAIS
Text("Confirmer la réservation")
Toast.makeText(context, "Erreur réseau", Toast.LENGTH_SHORT).show()

// ✅ TOUJOURS
Text(stringResource(R.string.booking_confirm_button))
Toast.makeText(context, getString(R.string.error_network), Toast.LENGTH_SHORT).show()
```

**API Key — intercepteur Retrofit :**
```kotlin
class ApiKeyInterceptor(private val keyStore: ApiKeyStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val key = keyStore.getApiKey() ?: throw UnauthorizedException()
        val request = chain.request().newBuilder()
            .addHeader("X-API-Key", key)
            .addHeader("Accept-Language", keyStore.getUserLocale())
            .build()
        return chain.proceed(request)
    }
}
```

**Formatage des données selon locale :**
```kotlin
// Devise
fun formatPrice(cents: Int, currency: String, locale: Locale): String {
    val amount = cents / 100.0
    val format = NumberFormat.getCurrencyInstance(locale)
    format.currency = Currency.getInstance(currency)
    return format.format(amount)
}

// Poids (kg ou lb)
fun formatWeight(kg: Double, unit: WeightUnit, locale: Locale): String {
    return if (unit == WeightUnit.LB) "${(kg * 2.20462).roundToInt()} lb"
    else "${kg} kg"
}

// Dates (toujours depuis UTC vers timezone user)
fun formatDateTime(utc: Instant, timezone: ZoneId, locale: Locale): String {
    return DateTimeFormatter
        .ofLocalizedDateTime(FormatStyle.MEDIUM, FormatStyle.SHORT)
        .withLocale(locale)
        .withZone(timezone)
        .format(utc)
}
```

---

## 4. RÈGLES i18n NON NÉGOCIABLES

Ces règles s'appliquent à **chaque ligne de code produite**, sans exception.

| # | Règle | Backend | Android |
|---|-------|---------|---------|
| 1 | Zéro string UI codée en dur | Messages d'erreur dans `locales/*.json` | Tout dans `strings.xml` |
| 2 | Locale transmise dans chaque requête | Header `Accept-Language` lu côté backend | Intercepteur Retrofit |
| 3 | Montants = centimes + devise ISO 4217 | `price_cents INT + currency VARCHAR(3)` | Formater avec `NumberFormat` |
| 4 | Dates = UTC en base | `datetime` PostgreSQL TIMESTAMPTZ | Afficher avec `ZoneId` user |
| 5 | Poids = kg en base | `weight_kg NUMERIC(5,2)` | Convertir selon `weight_unit` user |
| 6 | Pays = ISO 3166-1 alpha-2 | `country VARCHAR(2)` | Sélecteur avec libellés localisés |
| 7 | Premiers jours de semaine | Géré via locale | `WeekFields.of(locale)` |
| 8 | Notifications traduits | Utiliser `user.locale` pour les push | Firebase locale dans payload |

---

## 5. RÈGLES DE SÉCURITÉ

- **API Key** : jamais loguée, jamais exposée dans les réponses (sauf au moment de la création)
- **`SECRET_SALT`** : uniquement depuis variable d'environnement `API_KEY_SALT`, jamais en dur
- **Passwords** : hashés avec bcrypt (coût ≥ 12), jamais stockés en clair, jamais loggués
- **Uploads (photos)** : validation MIME type + taille max côté serveur, pas seulement côté client
- **Endpoints sensibles** : middleware API Key sur **tous** les routes sauf `/auth/*` et `/health`
- **CORS** : configurer strictement les origines autorisées (pas de `*` en production)
- **Rate limiting** : activer sur `/auth/google` et `/auth/login` (max 10 req/min par IP)
- **SQL Injection** : utiliser uniquement les paramètres SQLAlchemy, jamais de f-string en SQL

### 5.1 Chiffrement des données personnelles (PII) — Règle non négociable

**Toute donnée à caractère personnel (PII) doit être chiffrée au repos en base de données.**

> Le chiffrement est applicatif (Python), pas au niveau PostgreSQL — l'agent n'a jamais accès aux données en clair même avec un dump SQL.

**Champs PII obligatoirement chiffrés côté backend :**

| Entité | Champs chiffrés |
|--------|----------------|
| `users` | `first_name`, `last_name`, `email`, `phone`, `google_sub` |
| `client_profiles` | `injuries_notes` |
| `coach_profiles` | `bio` |
| `coach_notes` | `content` |
| `payments` | `reference`, `notes` |
| `sms_logs` | `body`, `phone_to` |
| `integration_tokens` | `access_token`, `refresh_token` |
| `cancellation_message_templates` | `body` |

**Champs NON chiffrés (données opérationnelles, non-PII) :**
- IDs, statuts, timestamps, montants (centimes), codes pays/devise, booléens
- `email` dans `api_keys` : remplacé par `key_hash` (SHA-256, pas de PII)

**Implémentation backend — `EncryptedType` SQLAlchemy :**

```python
# app/core/encryption.py
from cryptography.fernet import Fernet
from app.core.config import settings

_fernet = Fernet(settings.FIELD_ENCRYPTION_KEY)  # clé AES-128 Fernet, env var

def encrypt(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet.encrypt(value.encode()).decode()

def decrypt(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet.decrypt(value.encode()).decode()
```

```python
# app/core/encrypted_type.py
from sqlalchemy import String, TypeDecorator
from app.core.encryption import encrypt, decrypt

class EncryptedString(TypeDecorator):
    """Chiffre/déchiffre automatiquement à l'écriture/lecture SQLAlchemy."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt(value)

    def process_result_value(self, value, dialect):
        return decrypt(value)
```

```python
# app/models/user.py — utilisation
from app.core.encrypted_type import EncryptedString

class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True, ...)
    first_name: Mapped[str] = mapped_column(EncryptedString(300))  # 150 chars → ~300 chiffrés
    last_name:  Mapped[str] = mapped_column(EncryptedString(300))
    email:      Mapped[str] = mapped_column(EncryptedString(500))
    phone:      Mapped[str | None] = mapped_column(EncryptedString(100))
    # ...
```

**Contraintes de ce choix et solutions adoptées :**
- ❌ Impossible de faire `WHERE email = ?` directement
  → ✅ **`email_hash`** = `SHA256(lower(email))`, stocké en clair, index unique, utilisé pour tous les lookups
- ❌ Impossible de faire `WHERE first_name LIKE ?` ou tri SQL par nom
  → ✅ **`search_token`** = `unaccent(lower(prénom + ' ' + nom))`, stocké en clair, index **GIN pg_trgm** → supporte `ILIKE '%query%'` et `similarity()` performants (voir DEV_PATTERNS.md §1.9)
- ✅ Dump SQL = illisible sans la clé `FIELD_ENCRYPTION_KEY`
- ✅ Rotation de clé possible avec script de re-chiffrement (voir DEV_PATTERNS.md §1.9)

**`search_token` — règle d'usage :**
- Jamais retourné dans les réponses API
- Jamais loggué
- Utilisé uniquement dans les clauses `WHERE` de recherche
- Pas considéré PII : token dérivé irréversible, ne permet pas de retrouver le nom exact

**Pattern email avec hash de recherche :**

```python
# users table : 2 colonnes pour l'email
email:      Mapped[str] = mapped_column(EncryptedString(500))  # valeur lisible
email_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # SHA-256 pour lookup

# À l'insertion :
import hashlib
user.email = email_address          # chiffré via EncryptedString
user.email_hash = hashlib.sha256(email_address.lower().encode()).hexdigest()

# À la recherche :
lookup_hash = hashlib.sha256(email_input.lower().encode()).hexdigest()
user = await db.execute(select(User).where(User.email_hash == lookup_hash))
```

**Variables d'environnement requises (2 clés distinctes) :**
```env
# .env.dev
FIELD_ENCRYPTION_KEY=<clé Fernet A — champs PII (noms, emails, notes...)>
TOKEN_ENCRYPTION_KEY=<clé Fernet B — tokens OAuth (Strava, Google Calendar, Withings...)>
# Générer chaque clé avec : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Pourquoi 2 clés ?** Compromission d'une clé n'expose pas l'autre catégorie. Rotation indépendante (les tokens OAuth ont une durée de vie courte — on peut les re-fetcher via re-OAuth si nécessaire).

**Implémentation Android — pas de PII en clair dans Room :**
- Room : les tables locales ne cachent **jamais** les champs PII en clair
- Seules les données non-sensibles sont cachées localement (IDs, statuts, timestamps)
- Les champs PII (prénom, nom, email, téléphone) → toujours re-fetchés depuis l'API
- Si cache de profil nécessaire → chiffrer la valeur via Android Keystore avant insertion Room (voir DEV_PATTERNS.md §M9)

**Longueur des champs prénom / nom :**
- **max 150 caractères** (noms internationaux, noms composés, caractères Unicode)
- Colonne `EncryptedString(300)` en base (le chiffrement Fernet augmente la taille ~1.3–1.5×)
- Validation Pydantic : `min_length=2, max_length=150`
- Validation Android : `InputFilter.LengthFilter(150)` + message d'erreur i18n

---

## 6. LISTES DE TÂCHES

Les tâches sont réparties dans deux fichiers dédiés, un par plateforme :

| Fichier | Plateforme | Répertoire cible |
|---------|-----------|-----------------|
| `docs/TASKS_BACKEND.md` | Python / FastAPI | `backend/` |
| `docs/TASKS_ANDROID.md` | Kotlin / Android | `android/` |

**Règles d'utilisation :**
- Chaque tâche est numérotée (`B0-01`, `A0-01`…) et référence ses dépendances
- Chaque tâche a une priorité : 🔴 Bloquant / 🟡 Important / 🟢 Optionnel
- Traiter les tâches 🔴 dans l'ordre avant toute tâche 🟡
- Mettre à jour `docs/PROGRESS.md` après chaque tâche complétée
- Statuts : `⬜ À faire` | `🔄 En cours` | `✅ Terminé` | `⛔ Bloqué`

**Ordre de développement inter-plateformes :**
```
Phase 0 Back (B0-01→B0-26)
       │
       ├──► Phase 0 Android (A0-01→A0-31)    ← peut démarrer en parallèle (UI mocks)
       │
Phase 1 Back (B1-01→B1-28)
       │
       ├──► Phase 1 Android (A1-01→A1-20)
       │
Phase 2 Back (B2-01→B2-26)
       │
       └──► Phase 2 Android (A2-01→A2-26)
                     ...
```

---

> 📋 **Les tâches détaillées sont dans :**
> - `docs/TASKS_BACKEND.md` — toutes les tâches Python/FastAPI (B0-xx → B6-xx)
> - `docs/TASKS_ANDROID.md` — toutes les tâches Kotlin/Android (A0-xx → A6-xx)

---

### Résumé des phases (vue d'ensemble)

| Phase | Back (TASKS_BACKEND.md) | Android (TASKS_ANDROID.md) | Sem. |
|-------|------------------------|---------------------------|------|
| 0 — Fondations | B0-01 → B0-26 (infra, auth, API Key, i18n) | A0-01 → A0-31 (setup, design, login) | 1–2 |
| 1 — Coach | B1-01 → B1-28 (profil, tarifs, clients, paiements) | A1-01 → A1-20 (onboarding, dashboard, clients) | 3–5 |
| 2 — Client & Résa | B2-01 → B2-26 (questionnaire, réservation, annulation, waitlist) | A2-01 → A2-26 (questionnaire, recherche, booking, agenda) | 6–8 |
| 3 — Performances | B3-01 → B3-15 (QR, exercices, séances, stats, PRs) | A3-01 → A3-20 (session, scanner, graphiques) | 9–11 |
| 4 — IA & Programmes | B4-01 → B4-13 (génération programme, progression, vidéos) | A4-01 → A4-17 (séance guidée, builder programme) | 12–14 |
| 5 — Intégrations | B5-01 → B5-08 (Strava, Calendar, Balance, Firebase) | A5-01 → A5-12 (OAuth, balance, notifications) | 15–17 |
| 6 — Launch | B6-01 → B6-06 (audit, RGPD, perf, Docker hardening) | A6-01 → A6-12 (polish, Espresso, Play Store) | 18–20 |

> ⚠️ Toujours commencer par les tâches 🔴 (bloquantes) dans l'ordre indiqué dans chaque fichier.

---

#### SUPPRIMÉ — voir TASKS_BACKEND.md et TASKS_ANDROID.md pour le détail complet
---

## 7. FICHIER DE PROGRESSION

À chaque tâche terminée, mets à jour `docs/PROGRESS.md` avec :

```markdown
## Progression MyCoach

Dernière mise à jour : [DATE]

### Phase 0 — Fondations
| Tâche | Statut | Notes |
|-------|--------|-------|
| B0-1 | ✅ | FastAPI init OK |
| B0-2 | ✅ | Docker Compose opérationnel |
| B0-3 | 🔄 | En cours |
...

### Prochaine tâche : B0-4 — Alembic setup
```

---

## 8. QUESTIONS À POSER AVANT DE CODER

Si l'une de ces situations se présente, **arrête et pose la question** avant de continuer :

- Un cas non couvert dans les specs (comportement ambigu)
- Une dépendance technique non résolue (clé API externe manquante, etc.)
- Un conflit entre deux règles dans les specs
- Une décision d'architecture qui n'est pas dans le roadmap
- Un écart de performance important par rapport aux estimations

Ne jamais improviser sur un point non spécifié — toujours demander.

---

## 9. CE QUE TU NE DOIS PAS FAIRE

**Architecture & données :**
- ❌ Commencer la Phase 1 sans que tous les tests de la Phase 0 passent
- ❌ Utiliser SQLite (même pour les tests — utiliser PostgreSQL avec un container de test)
- ❌ Stocker des montants en float (toujours en centimes entiers)
- ❌ Coder une string UI en dur dans le code Android ou Backend
- ❌ Stocker des secrets dans le code source (utiliser `.env`, jamais commiter `.env`)
- ❌ Créer un endpoint sans middleware d'authentification (sauf `/auth/*` et `/health`)
- ❌ Écrire de la logique métier dans un Router ou un Fragment/Activity
- ❌ Faire des appels réseau depuis le thread UI Android
- ❌ Utiliser `!!` (null assertion) en Kotlin sans justification dans un commentaire

**Tests (règles absolues) :**
- ❌ **Commiter une feature sans ses tests** — interdit sans exception
- ❌ **N'écrire que des cas passants** — les cas non passants sont obligatoires
- ❌ Commiter si un test est rouge — corriger le code, jamais le test
- ❌ Marquer une tâche ✅ dans PROGRESS.md si les tests ne passent pas à 100%
- ❌ Séparer le code d'une feature et ses tests dans des commits différents
- ❌ Utiliser des mocks pour masquer un vrai bug — les mocks servent à isoler, pas à cacher

---

## 10. DÉFINITION DU DONE (DoD)

> Une tâche est **terminée** si et seulement si **tous** ces critères sont satisfaits :

```
CRITÈRES FONCTIONNELS
□ La feature correspond exactement aux specs (FUNCTIONAL_SPECS_DETAILED.md)
□ Tous les cas d'erreur des specs sont gérés (pas de comportement indéfini)
□ Les messages d'erreur sont i18n (jamais de string codée en dur)

CRITÈRES DE QUALITÉ CODE
□ Structure en couches respectée (Router → Service → Repository)
□ Aucune logique métier dans le Router (backend) ou Fragment/Activity (Android)
□ Les exceptions métier sont typées (ex: LateCancellationError, DuplicateBookingError)

CRITÈRES DE TEST — OBLIGATOIRES
□ Au moins 1 test unitaire "cas passant" par fonction de service / endpoint / ViewModel
□ Au moins 1 test unitaire "cas non passant" par règle métier implémentée
□ Tous les tests existants passent (0 failure, 0 error, 0 skip non justifié)
□ Les cas non passants testent bien un comportement attendu (erreur, rejet, exception)
  et non une absence de comportement

CRITÈRES DE COMMIT
□ Commit contient : code de la feature + ses tests + mise à jour PROGRESS.md
□ Message de commit au format : [PHASE-X][TASK-Y] Description + tests
□ Branche propre (pas de fichiers temporaires, pas de .env commité)
```

### Exemples de paires passant / non passant

**Backend — Service `create_template` (max 5 templates par coach) :**
```python
# ✅ CAS PASSANT
async def test_create_template_ok(db, coach):
    t = await create_template(db, coach.id, title="Maladie", body="Bonjour {prénom}...")
    assert t.id is not None
    assert t.position == 1

# ❌ CAS NON PASSANT — limite dépassée
async def test_create_template_max_5_raises(db, coach_with_5_templates):
    with pytest.raises(TemplateLimitReachedError):
        await create_template(db, coach_with_5_templates.id, title="6ème", body="...")

# ❌ CAS NON PASSANT — coach inconnu
async def test_create_template_unknown_coach(db):
    with pytest.raises(CoachNotFoundError):
        await create_template(db, uuid4(), title="Test", body="...")
```

**Android — ViewModel `CancellationTemplateViewModel` :**
```kotlin
// ✅ CAS PASSANT
@Test fun `getTemplates emits Success with list`() = runTest {
    coEvery { repo.getTemplates() } returns listOf(fakeTemplate)
    viewModel.load()
    assertIs<UiState.Success<*>>(viewModel.uiState.value)
}

// ❌ CAS NON PASSANT — erreur réseau
@Test fun `getTemplates emits Error on network failure`() = runTest {
    coEvery { repo.getTemplates() } throws IOException("timeout")
    viewModel.load()
    assertIs<UiState.Error>(viewModel.uiState.value)
}

// ❌ CAS NON PASSANT — création au-delà de 5
@Test fun `createTemplate emits Error when limit reached`() = runTest {
    coEvery { repo.getTemplates() } returns List(5) { fakeTemplate }
    viewModel.onCreateClicked("nouveau", "corps")
    val state = viewModel.uiState.value
    assertIs<UiState.Error>(state)
    assertEquals("template_limit_reached", (state as UiState.Error).code)
}
```

---

*Ce document est la loi. En cas de doute, relis-le.*
*Version 1.1 — 26/02/2026 — Ajout DoD + règles test cas passants/non passants*
*Version 1.2 — 26/02/2026 — §5.1 Chiffrement PII : EncryptedString SQLAlchemy, champs ciblés, email_hash lookup, FIELD_ENCRYPTION_KEY, longueur prénom/nom 150 chars*
