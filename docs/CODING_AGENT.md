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

### 1.5 Chaque tâche = un commit Git propre
- Format du message de commit : `[PHASE-X][TASK-Y] Description courte`
- Exemple : `[PHASE-0][TASK-3] Auth API Key - Google OAuth flow`
- Ne pas regrouper plusieurs tâches dans un seul commit
- Branche : `main` (projet solo) ou créer des branches feature si spécifié

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
│  ÉTAPE 4 — TESTER                                           │
│  Écris les tests unitaires couvrant :                       │
│  - Le cas nominal (happy path)                              │
│  - Les cas d'erreur définis dans les specs                  │
│  - Les règles de validation champ par champ                 │
│  Lance les tests. Tous doivent passer.                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 5 — VALIDER                                          │
│  Relis le code produit et vérifie :                         │
│  ✓ i18n respectée (aucune string codée en dur)              │
│  ✓ Standards de code respectés                              │
│  ✓ Tous les cas d'erreur des specs sont couverts            │
│  ✓ Le modèle de données correspond aux specs                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ÉTAPE 6 — COMMITER                                         │
│  `git add .`                                                │
│  `git commit -m "[PHASE-X][TASK-Y] Description"`            │
│  Mets à jour `docs/PROGRESS.md` (tâche = ✅)               │
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

---

## 6. LISTE ORDONNÉE DES TÂCHES

> Mise à jour de l'état dans `docs/PROGRESS.md` après chaque tâche.
> Statuts : `⬜ À faire` | `🔄 En cours` | `✅ Terminé` | `⛔ Bloqué`

---

### PHASE 0 — Fondations *(Semaines 1–2)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B0-1 | Initialiser le projet FastAPI : structure dossiers, `main.py`, `config.py` (pydantic-settings), `requirements.txt` | ⬜ |
| B0-2 | Docker Compose : service `db` (PostgreSQL 16), service `backend`, volumes, variables d'env | ⬜ |
| B0-3 | Configurer SQLAlchemy 2 async + asyncpg : `database.py`, session factory, base declarative | ⬜ |
| B0-4 | Configurer Alembic : `alembic.ini`, `env.py` async, première migration vide | ⬜ |
| B0-5 | Modèle `users` : id UUID, email, name, photo_url, role, locale (BCP 47), timezone, country (ISO 3166-1), created_at, updated_at | ⬜ |
| B0-6 | Modèle `api_keys` : id, user_id FK, key_hash CHAR(64) unique indexé, device_name, created_at, last_used_at, expires_at, revoked | ⬜ |
| B0-7 | Utilitaire de génération API Key : `generate_api_key(unique_input: str) -> str` (SHA-256 + SECRET_SALT) | ⬜ |
| B0-8 | Middleware d'authentification : `get_current_user(X-API-Key)` → lookup base → retourne User ou HTTP 401 | ⬜ |
| B0-9 | Route `POST /auth/google` : vérifie Google ID Token (clés publiques Google via `google-auth`), crée/récupère user, génère API Key, retourne `{ api_key, user }` | ⬜ |
| B0-10 | Route `POST /auth/register` : création compte email/password, envoi email de vérification (token 24h) | ⬜ |
| B0-11 | Route `GET /auth/verify-email?token=` : active le compte | ⬜ |
| B0-12 | Route `POST /auth/login` : vérifie credentials bcrypt, génère API Key, retourne `{ api_key, user }` | ⬜ |
| B0-13 | Route `DELETE /auth/logout` : révoque la clé courante | ⬜ |
| B0-14 | Route `DELETE /auth/logout-all` : révoque toutes les clés du user | ⬜ |
| B0-15 | Route `GET /auth/me` : retourne le profil utilisateur courant (vérifie API Key) | ⬜ |
| B0-16 | Route `POST /auth/forgot-password` + `POST /auth/reset-password` | ⬜ |
| B0-17 | Système i18n backend : chargement fichiers `locales/fr.json` + `locales/en.json`, fonction `t(key, locale)` | ⬜ |
| B0-18 | Middleware `Accept-Language` → injecte `locale` dans le contexte de chaque requête | ⬜ |
| B0-19 | Route `GET /health` : retourne `{ status: ok, db: ok }` (sans auth) | ⬜ |
| B0-20 | Tests unitaires : toutes les routes auth (happy path + erreurs : email dupe, bad credentials, token expiré, clé révoquée) | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A0-1 | Initialiser le projet Android : package `com.mycoach.app`, minSdk 26, Kotlin 1.9+, Hilt, Retrofit, Navigation Component | ⬜ |
| A0-2 | Design System : définir couleurs Coach (`#0A0E1A` / `#7B2FFF`) et Client (`#F0F4FF` / `#00C2FF`), typographie (Space Grotesk), thème Material 3 | ⬜ |
| A0-3 | `ApiClient` singleton Retrofit : URL base depuis DataStore, intercepteur `ApiKeyInterceptor` (header `X-API-Key` + `Accept-Language`) | ⬜ |
| A0-4 | `ApiKeyStore` : stockage/lecture API Key dans `EncryptedSharedPreferences`, méthode `isLoggedIn()` | ⬜ |
| A0-5 | `SplashScreen` : vérifie `isLoggedIn()` → `GET /auth/me` → si 200 redirect Dashboard, sinon redirect Login | ⬜ |
| A0-6 | `LoginScreen` : email + password, bouton Google Sign-In (SDK), lien "Mot de passe oublié", lien "Créer un compte" | ⬜ |
| A0-7 | `LoginViewModel` : `loginWithEmail()`, `loginWithGoogle(idToken)` → appels API → stocke API Key → émet état `Success(role)` | ⬜ |
| A0-8 | `RegisterScreen` + `RegisterViewModel` : inscription email/password + choix pays/locale + choix rôle Coach/Client | ⬜ |
| A0-9 | `EmailVerificationScreen` : affiche email, bouton renvoyer (cooldown 60s), lien "Mauvais email" | ⬜ |
| A0-10 | `RoleSelectionScreen` : affiché après Google login si nouveau compte → sélection Coach / Client | ⬜ |
| A0-11 | `ForgotPasswordScreen` + `ResetPasswordScreen` | ⬜ |
| A0-12 | Système i18n Android : `strings.xml` en (défaut) + fr + es + pt. `LocaleHelper` : applique la locale user au démarrage et à chaque changement | ⬜ |
| A0-13 | `WeightFormatter`, `PriceFormatter`, `DateTimeFormatter` : fonctions utilitaires i18n pour l'affichage | ⬜ |
| A0-14 | Tests unitaires : `LoginViewModel`, `RegisterViewModel` (mocks Retrofit) | ⬜ |

---

### PHASE 1 — Espace Coach *(Semaines 3–5)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B1-1 | Modèles BDD : `coach_profiles`, `specialties`, `coach_certifications`, `gyms`, `gym_chains`, `coach_gyms` (relation M-M) | ⬜ |
| B1-2 | Modèles BDD : `coach_pricing` (per_session et package), `coach_availability` (créneaux récurrents + nb places + horizon), `cancellation_policies` | ⬜ |
| B1-3 | API `POST /coaches/profile` : création profil coach (onboarding étapes 1–5) | ⬜ |
| B1-4 | API `PUT /coaches/profile` : mise à jour profil | ⬜ |
| B1-5 | API `GET /coaches/profile` : récupère profil coach courant | ⬜ |
| B1-6 | API `GET /gyms?chain=&country=&city=&q=` : recherche de clubs (filtres pays obligatoire) | ⬜ |
| B1-7 | Seed BDD : import des répertoires de salles (Fitness Park, Basic-Fit, etc.) avec champ `country` ISO 3166-1 | ⬜ |
| B1-8 | API CRUD `/coaches/pricing` : créer/modifier/supprimer forfaits et tarif unitaire (montants en centimes + devise) | ⬜ |
| B1-9 | API CRUD `/coaches/availability` : créneaux récurrents + nb places + horizon | ⬜ |
| B1-10 | API `PUT /coaches/cancellation-policy` : délai, mode (auto/manuel), no-show policy, message client | ⬜ |
| B1-11 | Modèles BDD : `coaching_relations`, `clients` (vue coach sur ses clients), `coach_notes` | ⬜ |
| B1-12 | API `GET /coaches/clients` : liste avec filtres (statut, tri) + pagination | ⬜ |
| B1-13 | API `GET /coaches/clients/{id}` : fiche client complète (profil + séances + paiements) | ⬜ |
| B1-14 | API `PUT /coaches/clients/{id}/relation` : suspend / termine la relation | ⬜ |
| B1-15 | API `PUT /coaches/clients/{id}/note` : note privée coach | ⬜ |
| B1-16 | Modèles BDD : `payments`, `packages` (forfaits achetés par client) | ⬜ |
| B1-17 | API CRUD `/coaches/clients/{id}/payments` : créer forfait, enregistrer paiement, historique | ⬜ |
| B1-18 | API `GET /coaches/clients/{id}/hours` : heures consommées / forfait actif | ⬜ |
| B1-19 | Tests unitaires : toutes les routes coach | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A1-1 | `CoachOnboardingActivity` : navigation entre les 5 écrans d'onboarding avec progress indicator | ⬜ |
| A1-2 | Écran 1/5 : photo (Camera/Galerie + crop), prénom/nom, bio avec compteur de chars | ⬜ |
| A1-3 | Écran 2/5 : spécialités multi-select (chips) | ⬜ |
| A1-4 | Écran 3/5 : certifications (liste ajoutables + upload photo) | ⬜ |
| A1-5 | Écran 4/5 : sélection salles (chaîne → pays → ville/CP → clubs multi-select) | ⬜ |
| A1-6 | Écran 5/5 : devise, tarif unitaire, forfaits (lignes dynamiques : nb séances + prix + validité + visibilité), séance découverte, durée standard, disponibilités récurrentes | ⬜ |
| A1-7 | `CoachDashboardFragment` : KPIs (séances, clients, heures, revenus formatés selon locale/devise), prochaines séances, réservations à valider, alertes forfaits | ⬜ |
| A1-8 | `ClientListFragment` + `ClientListViewModel` : liste filtrée/triée, recherche | ⬜ |
| A1-9 | `ClientDetailFragment` : 5 onglets (Profil, Séances, Programme, Performances, Paiements) | ⬜ |
| A1-10 | `ClientPaymentsFragment` : solde forfait, historique, créer forfait, enregistrer paiement, export | ⬜ |
| A1-11 | `CoachProfileFragment` : affichage et édition profil, politique d'annulation, partage profil (deep link) | ⬜ |
| A1-12 | Tests unitaires ViewModels : Dashboard, ClientList, ClientDetail | ⬜ |

---

### PHASE 2 — Espace Client *(Semaines 6–8)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B2-1 | Modèles BDD : `client_profiles`, `client_questionnaires`, `client_gyms` | ⬜ |
| B2-2 | API `POST /clients/profile` + `PUT /clients/profile` + `GET /clients/profile` | ⬜ |
| B2-3 | API `POST /clients/questionnaire` + `PUT /clients/questionnaire` | ⬜ |
| B2-4 | API `GET /coaches/search?country=&chain=&gym=&specialty=&max_price=&discovery=&certified=` : recherche coaches avec filtres | ⬜ |
| B2-5 | API `GET /coaches/{id}/public` : profil public d'un coach (visible par client) | ⬜ |
| B2-6 | Modèles BDD : `coaching_requests` (demandes de découverte), `bookings`, `waitlist` | ⬜ |
| B2-7 | API `POST /coaching-requests` : demande de découverte client → coach | ⬜ |
| B2-8 | API `GET /coaching-requests` (coach) : liste des demandes en attente | ⬜ |
| B2-9 | API `POST /coaching-requests/{id}/accept` : coach accepte + propose créneau découverte | ⬜ |
| B2-10 | API `POST /coaching-requests/{id}/reject` : coach refuse + motif | ⬜ |
| B2-11 | API `GET /coaches/{id}/slots?from=&to=` : créneaux disponibles du coach (calcul depuis availability - bookings existants) | ⬜ |
| B2-12 | API `POST /bookings` : client réserve un créneau (statut `pending_coach_validation`) + choix tarif (unitaire ou forfait_id) | ⬜ |
| B2-13 | API `POST /bookings/{id}/confirm` (coach) : valide la réservation | ⬜ |
| B2-14 | API `POST /bookings/{id}/reject` (coach) : refuse + motif | ⬜ |
| B2-15 | API `DELETE /bookings/{id}` : annulation par client ou coach — applique la règle pénalité (< délai = séance due) | ⬜ |
| B2-16 | API `POST /bookings/{id}/waive-penalty` (coach) : exonère la pénalité d'annulation tardive | ⬜ |
| B2-17 | API `POST /bookings/{id}/no-show` (coach) : marque le client absent | ⬜ |
| B2-18 | Service `WaitlistService` : gestion FIFO, notification 30 min, expiration, passage au suivant | ⬜ |
| B2-19 | API `POST /waitlist/{slot_ref}` : rejoindre la liste d'attente | ⬜ |
| B2-20 | API `DELETE /waitlist/{id}` : quitter la liste d'attente | ⬜ |
| B2-21 | API `POST /waitlist/{id}/confirm` : client confirme dans la fenêtre de 30 min | ⬜ |
| B2-22 | Worker async : auto-reject des `pending_coach_validation` après 24h sans réponse coach | ⬜ |
| B2-23 | Envoi notifications push (Firebase) : tous les déclencheurs définis dans les specs §21 | ⬜ |
| B2-24 | Tests unitaires : réservation, annulation (cas < et > délai), liste d'attente, notifications | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A2-1 | `ClientOnboardingActivity` : 6 écrans de questionnaire avec navigation et sauvegarde progressive | ⬜ |
| A2-2 | Écrans questionnaire 1–6 (objectif, niveau, fréquence, équipements, zones, blessures) | ⬜ |
| A2-3 | `ClientDashboardFragment` : programme de la semaine, prochaines séances, accès rapide "Nouvelle séance" | ⬜ |
| A2-4 | `CoachSearchFragment` : barre recherche + filtres (drawer) + liste résultats | ⬜ |
| A2-5 | `CoachPublicProfileFragment` : profil coach complet, bouton "Demander découverte" / "Réserver" | ⬜ |
| A2-6 | `DiscoveryRequestBottomSheet` : message optionnel + confirmation | ⬜ |
| A2-7 | `CoachSlotsFragment` : calendrier des disponibilités du coach (🟢🟠🔴⬛🟡) | ⬜ |
| A2-8 | `BookingConfirmBottomSheet` : récap créneau + sélection tarif (unitaire / forfait / forfait actif) | ⬜ |
| A2-9 | `ClientAgendaFragment` : vue semaine multi-coach color-coded, tap → détail séance | ⬜ |
| A2-10 | `SessionDetailBottomSheet` (client) : infos + actions selon statut (Accepter/Décliner/Annuler) + règle pénalité affichée si < délai | ⬜ |
| A2-11 | `WaitlistBottomSheet` : position dans la file, règle 30 min, rejoindre/quitter | ⬜ |
| A2-12 | Écran de confirmation liste d'attente (deep link depuis notification) : "Confirmer en X min" avec timer | ⬜ |
| A2-13 | Tests unitaires ViewModels : CoachSearch, Booking, Agenda | ⬜ |

---

### PHASE 3 — Performances *(Semaines 9–11)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B3-1 | Modèles BDD : `exercise_types` (nom, catégorie, muscles ciblés, vidéo, difficulté), `machines` (type, marque, modèle, photo, qr_code, validated) | ⬜ |
| B3-2 | Modèles BDD : `performance_sessions`, `exercise_sets` (session, exercice, sets, reps, weight_kg) | ⬜ |
| B3-3 | API `GET /exercises?q=&category=&muscle=` : liste des exercices searchable | ⬜ |
| B3-4 | API `GET /machines/qr/{qr_code}` : identification machine par QR | ⬜ |
| B3-5 | API `POST /machines/submit` : soumission machine inconnue (type, marque, modèle, photo) | ⬜ |
| B3-6 | API `POST /performances` : créer une session de performance (sets, exercices) | ⬜ |
| B3-7 | API `PUT /performances/{id}` : modifier (accessible < 48h, par l'auteur uniquement) | ⬜ |
| B3-8 | API `DELETE /performances/{id}` : supprimer (accessible < 48h, par l'auteur) | ⬜ |
| B3-9 | API `POST /performances/for-client/{client_id}` (coach) : saisir perf pour un client | ⬜ |
| B3-10 | API `GET /performances?from=&to=&type=&muscle=` : historique filtré | ⬜ |
| B3-11 | API `GET /performances/stats/exercise/{exercise_id}` : données graphique (poids max + volume par date) | ⬜ |
| B3-12 | API `GET /performances/stats/week` : séances semaine en cours, muscles travaillés, streak | ⬜ |
| B3-13 | Détection PR (record personnel) : à chaque sauvegarde, comparer avec l'historique → si nouveau PR → notif push | ⬜ |
| B3-14 | API `GET /coaches/clients/{id}/performances` (coach) : perfs d'un client si partage activé | ⬜ |
| B3-15 | Back-office : API `GET /admin/machines/pending` + `POST /admin/machines/{id}/validate` + `POST /admin/machines/{id}/reject` | ⬜ |
| B3-16 | Tests unitaires : création perf, stats, détection PR, accès coach aux perfs client | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A3-1 | `WorkoutSessionFragment` : liste d'exercices, drag & drop, chrono, bouton "Terminer" | ⬜ |
| A3-2 | `AddExerciseBottomSheet` : onglets Scanner QR / Manuel | ⬜ |
| A3-3 | QR Code scanner : intégration ML Kit Barcode Scanning, overlay caméra, feedback vibration | ⬜ |
| A3-4 | Fallback manuel : type machine (scroll list) → marque → modèle → photo (Camera/Galerie) | ⬜ |
| A3-5 | `ExerciseSetBottomSheet` : steppers reps/poids par série, ajout/suppression série, note, bouton vidéo | ⬜ |
| A3-6 | `VideoPlayerBottomSheet` : mini player vidéo (ExoPlayer) en overlay, loop, légendes | ⬜ |
| A3-7 | `SessionSummaryFragment` : récap perf, ressenti 1–5 étoiles, sauvegarder, bottom sheet Strava | ⬜ |
| A3-8 | `PerformanceHistoryFragment` : liste avec filtres période/type/muscle | ⬜ |
| A3-9 | `PerformanceDetailFragment` : détail séance, modifier/supprimer si < 48h | ⬜ |
| A3-10 | `PerformanceStatsFragment` : sélecteur exercice + graphiques (MPAndroidChart), badges PR | ⬜ |
| A3-11 | `WeekDashboardFragment` : jauge séances, radar muscles, streak, volume mensuel | ⬜ |
| A3-12 | Saisie coach pour client : banner "Saisie pour [Client]", même interface + notif client | ⬜ |
| A3-13 | Tests unitaires ViewModels : WorkoutSession, PerformanceHistory, Stats | ⬜ |

---

### PHASE 4 — Intelligence IA *(Semaines 12–14)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B4-1 | Service `ProgramGeneratorService` : génère un programme hebdo depuis le questionnaire client (règles métier, pas d'IA externe nécessaire en v1) | ⬜ |
| B4-2 | API `GET /clients/program` : programme de la semaine en cours (IA ou coach) | ⬜ |
| B4-3 | API `POST /clients/program/recalibrate` : regénère depuis questionnaire mis à jour | ⬜ |
| B4-4 | Service `ProgressionService` : règle d'ajustement automatique des charges (3 séances OK → +2.5kg, échec → maintien/réduction) | ⬜ |
| B4-5 | Modèles BDD : `workout_plans`, `planned_sessions`, `planned_exercises` | ⬜ |
| B4-6 | API CRUD `/coaches/programs` : créer/modifier/dupliquer/archiver des programmes | ⬜ |
| B4-7 | API `POST /coaches/programs/{id}/assign` : assigner un programme à un client avec date de départ | ⬜ |
| B4-8 | API `GET /coaches/clients/{id}/program-progress` : avancement semaine + perfs réelles vs cibles | ⬜ |
| B4-9 | Modèles BDD : `exercise_videos` (exercise_type_id, video_url, status: pending/generating/validating/published/rejected) | ⬜ |
| B4-10 | Back-office : API `POST /admin/videos/generate/{exercise_id}` → appel API IA vidéo (Kling/Runway), statut async | ⬜ |
| B4-11 | Back-office : API `POST /admin/videos/{id}/validate` + `POST /admin/videos/{id}/reject` | ⬜ |
| B4-12 | Tests unitaires : génération programme, ajustement progressif, CRUD programmes coach | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A4-1 | `ProgramWeekFragment` : vue semaine du programme (séances prévues, statuts ✓/✗/⏳, badge IA ou Coach) | ⬜ |
| A4-2 | `ProgramSessionPreviewFragment` : liste exercices + durée + muscles + bouton "Commencer" | ⬜ |
| A4-3 | `GuidedSessionFragment` : navigation exercice par exercice, progress bar, bouton vidéo | ⬜ |
| A4-4 | Sets guidés : préremplissage poids cibles, saisie poids réel, bouton "Set réalisé ✓" | ⬜ |
| A4-5 | Timer de repos : countdown, vibration + son, "Ignorer", "Prolonger +30s" | ⬜ |
| A4-6 | Modification inline pendant séance guidée : changer poids/reps, passer exercice + motif | ⬜ |
| A4-7 | `GuidedSessionSummaryFragment` : animation Lottie, ressenti, sauvegarde, Strava | ⬜ |
| A4-8 | Affichage suggestion ajustement progressif : notification + confirmation/refus | ⬜ |
| A4-9 | `CoachProgramBuilderFragment` : créer programme (vue semaine, ajout séances, ajout exercices, drag & drop) | ⬜ |
| A4-10 | `CoachProgramLibraryFragment` : liste programmes, assigner à un client | ⬜ |
| A4-11 | `ClientProgramProgressFragment` (coach) : avancement + perfs réelles vs cibles | ⬜ |
| A4-12 | Tests unitaires ViewModels : GuidedSession, ProgramBuilder | ⬜ |

---

### PHASE 5 — Intégrations *(Semaines 15–17)*

#### Back-end

| # | Tâche | Statut |
|---|-------|--------|
| B5-1 | Strava OAuth2 : `GET /integrations/strava/connect` + callback + stockage token | ⬜ |
| B5-2 | API `POST /integrations/strava/push/{session_id}` : push séance vers Strava (WeightTraining, Workout…) | ⬜ |
| B5-3 | API `GET /integrations/strava/import` : import activités Strava non présentes | ⬜ |
| B5-4 | Google Calendar OAuth2 : `GET /integrations/calendar/connect` + callback + stockage token | ⬜ |
| B5-5 | Service `CalendarSyncService` : push séances confirmées vers GCal, update si annulation | ⬜ |
| B5-6 | Withings OAuth2 : connect + callback + import mesures corporelles | ⬜ |
| B5-7 | API `GET /integrations/scale/history` : historique mesures corporelles (poids, IMC, % graisse…) | ⬜ |
| B5-8 | API `POST /integrations/scale/manual` : saisie manuelle d'une mesure | ⬜ |
| B5-9 | Firebase : configuration push notifications, envoi depuis le service de notifications existant | ⬜ |
| B5-10 | Tests d'intégration : OAuth flows, push Strava, sync Calendar, import balance | ⬜ |

#### Android

| # | Tâche | Statut |
|---|-------|--------|
| A5-1 | `IntegrationsFragment` : liste des intégrations (Strava, Calendar, Balance) avec statut connecté/déconnecté | ⬜ |
| A5-2 | Strava OAuth2 : WebView ou Chrome Custom Tab → callback → stockage token | ⬜ |
| A5-3 | Bottom sheet "Pousser vers Strava ?" après sauvegarde séance | ⬜ |
| A5-4 | Google Calendar OAuth2 : connexion + options sync bidirectionnelle | ⬜ |
| A5-5 | Balance connectée : Withings OAuth2 + import + graphiques composition corporelle | ⬜ |
| A5-6 | Saisie manuelle balance : modale date + poids + métriques optionnelles | ⬜ |
| A5-7 | `BodyCompositionFragment` : courbes historiques (poids, % graisse, masse musculaire), sélecteur période | ⬜ |
| A5-8 | Gestion notifications Firebase : réception, routing vers le bon écran selon type | ⬜ |
| A5-9 | Tests unitaires : IntegrationsViewModel, BodyCompositionViewModel | ⬜ |

---

### PHASE 6 — Polish & Launch *(Semaines 18–20)*

| # | Tâche | Statut |
|---|-------|--------|
| P6-1 | Animations Lottie : splash, completion séance, nouveau PR, onboarding | ⬜ |
| P6-2 | Glassmorphism + effets visuels high-tech sur les deux thèmes (Coach/Client) | ⬜ |
| P6-3 | Accessibilité : content descriptions sur tous les éléments interactifs, taille de texte adaptable | ⬜ |
| P6-4 | Tests E2E Android : Espresso sur les flows critiques (login → réservation → perf → sauvegarde) | ⬜ |
| P6-5 | Optimisation performances API : index PostgreSQL, requêtes N+1, cache Redis (optionnel) | ⬜ |
| P6-6 | Audit sécurité : OWASP Mobile Top 10, OWASP API Top 10 | ⬜ |
| P6-7 | RGPD : droit à l'oubli (suppression compte effectif J+30), export données utilisateur, bandeau consentement | ⬜ |
| P6-8 | CGU + Politique de confidentialité (WebView dans l'app) | ⬜ |
| P6-9 | Back-office web complet : modération machines, validation coachs, gestion vidéos, stats globales | ⬜ |
| P6-10 | Configuration Play Store : fiche app, captures d'écran, description (fr + en), politique de confidentialité | ⬜ |
| P6-11 | Beta interne (Firebase App Distribution) : 10 coachs + 50 clients | ⬜ |
| P6-12 | Correction bugs beta + polish final | ⬜ |
| P6-13 | 🚀 Publication Google Play Store | ⬜ |

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

- ❌ Commencer la Phase 1 sans que tous les tests de la Phase 0 passent
- ❌ Utiliser SQLite (même pour les tests — utiliser PostgreSQL avec un container de test)
- ❌ Stocker des montants en float (toujours en centimes entiers)
- ❌ Coder une string UI en dur dans le code Android ou Backend
- ❌ Stocker des secrets dans le code source (utiliser `.env`, jamais commiter `.env`)
- ❌ Créer un endpoint sans middleware d'authentification (sauf `/auth/*` et `/health`)
- ❌ Écrire de la logique métier dans un Router ou un Fragment/Activity
- ❌ Faire des appels réseau depuis le thread UI Android
- ❌ Utiliser `!!` (null assertion) en Kotlin sans justification dans un commentaire
- ❌ Merger une tâche sans tests unitaires associés

---

*Ce document est la loi. En cas de doute, relis-le.*
*Version 1.0 — 25/02/2026*
