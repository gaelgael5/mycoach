# MyCoach — Tâches Backend (Python / FastAPI)

> Répertoire : `backend/`
> Stack : Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2 async, Alembic, asyncpg
>
> **Ordre d'exécution obligatoire au sein de chaque phase :**
> Modèles BDD → Migration Alembic → Schemas Pydantic → Repository → Service → Router → Tests

---

> ### ⚠️ RÈGLE DE TEST — NON NÉGOCIABLE
>
> **Chaque tâche de type "Service" ou "Router" doit être committée avec ses tests.**
> Le fichier de test correspondant fait partie de la même tâche — pas d'une tâche séparée.
>
> Pour chaque fonction de service et chaque endpoint :
> - **1 test minimum "cas passant"** : l'appel nominal retourne le bon résultat
> - **1 test minimum "cas non passant"** : erreur métier, accès refusé, donnée invalide, limite dépassée
>
> Commande de validation avant commit : `pytest tests/ -v`
>
> **Un commit sans tests = commit invalide. Une tâche sans tests = tâche non terminée.**
>
> Voir `docs/CODING_AGENT.md §10` pour des exemples complets.

---

> Le backend d'une phase doit être **complet et testé** avant de démarrer la phase suivante.

---

## Structure du répertoire `backend/`

```
backend/
├── app/
│   ├── main.py                  ← Point d'entrée FastAPI, montage des routers
│   ├── config.py                ← Variables d'env (pydantic-settings)
│   ├── database.py              ← Engine async, session factory, Base
│   ├── auth/
│   │   ├── middleware.py        ← get_current_user, require_coach, require_admin
│   │   └── utils.py             ← generate_api_key, verify_password, verify_google_token
│   ├── models/                  ← Modèles SQLAlchemy (1 fichier par entité)
│   │   ├── user.py
│   │   ├── api_key.py
│   │   ├── coach_profile.py
│   │   ├── client_profile.py
│   │   ├── gym.py
│   │   ├── booking.py
│   │   ├── waitlist.py
│   │   ├── performance.py
│   │   ├── workout_plan.py
│   │   ├── exercise.py
│   │   ├── machine.py
│   │   ├── payment.py
│   │   └── notification.py
│   ├── schemas/                 ← Pydantic (1 fichier par domaine)
│   │   ├── common.py            ← PaginatedResponse, ErrorResponse
│   │   ├── auth.py
│   │   ├── coach.py
│   │   ├── client.py
│   │   ├── booking.py
│   │   ├── performance.py
│   │   ├── program.py
│   │   └── payment.py
│   ├── repositories/            ← Accès BDD pur (1 fichier par entité)
│   │   ├── base.py              ← BaseRepository avec get/create/update/delete génériques
│   │   ├── user_repository.py
│   │   ├── api_key_repository.py
│   │   ├── coach_repository.py
│   │   ├── client_repository.py
│   │   ├── gym_repository.py
│   │   ├── booking_repository.py
│   │   ├── waitlist_repository.py
│   │   ├── performance_repository.py
│   │   ├── program_repository.py
│   │   └── payment_repository.py
│   ├── services/                ← Logique métier (1 fichier par domaine)
│   │   ├── auth_service.py
│   │   ├── coach_service.py
│   │   ├── client_service.py
│   │   ├── booking_service.py
│   │   ├── waitlist_service.py
│   │   ├── performance_service.py
│   │   ├── program_service.py
│   │   ├── payment_service.py
│   │   └── notification_service.py
│   ├── routers/                 ← Routes FastAPI (1 fichier par domaine)
│   │   ├── auth.py
│   │   ├── coaches.py
│   │   ├── clients.py
│   │   ├── gyms.py
│   │   ├── bookings.py
│   │   ├── waitlist.py
│   │   ├── performances.py
│   │   ├── programs.py
│   │   ├── payments.py
│   │   └── admin.py
│   ├── locales/                 ← Fichiers i18n JSON
│   │   ├── fr.json
│   │   ├── en.json
│   │   ├── es.json
│   │   └── pt.json
│   └── utils/
│       ├── i18n.py              ← Fonction t(key, locale, **kwargs)
│       ├── hashing.py           ← generate_api_key, verify_password, hash_password
│       ├── pagination.py        ← Helpers pagination
│       └── date_utils.py        ← Conversion UTC ↔ timezone user
├── alembic/
│   ├── env.py
│   ├── versions/                ← Fichiers de migration (1 par changement de schéma)
│   └── alembic.ini
├── tests/
│   ├── conftest.py              ← Fixtures pytest (DB test, client HTTP, users fixtures)
│   ├── test_auth.py
│   ├── test_coaches.py
│   ├── test_clients.py
│   ├── test_bookings.py
│   ├── test_waitlist.py
│   ├── test_performances.py
│   ├── test_programs.py
│   └── test_payments.py
├── scripts/
│   └── seed_gyms.py             ← Import du répertoire des salles de sport
├── Dockerfile
├── docker-compose.yml
├── docker-compose.test.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── pyproject.toml               ← Config pytest, black, ruff
```

---

## PHASE 0 — Fondations

> Objectif : infrastructure prête, authentification fonctionnelle, API Key opérationnelle.
> **Aucune autre phase ne peut démarrer avant que B0 soit 100% ✅**

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B0-01** | Créer la structure des dossiers `backend/` telle que définie ci-dessus | — | 🔴 |
| **B0-02** | `pyproject.toml` : configurer pytest, black, ruff (linter) | B0-01 | 🔴 |
| **B0-03** | `requirements.txt` : fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, bcrypt, google-auth, python-multipart, slowapi, httpx | B0-01 | 🔴 |
| **B0-04** | `config.py` : classe Settings avec pydantic-settings (DATABASE_URL, API_KEY_SALT, GOOGLE_CLIENT_ID, SECRET_KEY, DEBUG, FRONTEND_URL) | B0-01 | 🔴 |
| **B0-05** | `database.py` : engine async, session factory, Base declarative, `get_db` Depends | B0-04 | 🔴 |
| **B0-06** | `docker-compose.yml` : service `db` (postgres:16-alpine, volumes, healthcheck), service `backend` (depends_on db) | B0-04 | 🔴 |
| **B0-07** | Alembic : init, `env.py` configuré pour async SQLAlchemy | B0-05 | 🔴 |
| **B0-08** | **Modèle** `users` : id UUID, email (unique), name, photo_url, role (enum: coach/client/admin), **phone (E.164, nullable)**, locale (BCP 47), timezone, country (ISO 3166-1), email_verified, password_hash, **profile_completion_pct INT (0-100)**, created_at, updated_at | B0-05 | 🔴 |
| **B0-09** | **Modèle** `api_keys` : id UUID, user_id FK→users, key_hash CHAR(64) UNIQUE INDEX, device_name, created_at, last_used_at, expires_at, revoked | B0-08 | 🔴 |
| **B0-10** | **Modèle** `email_verification_tokens` : id, user_id FK, token CHAR(64), expires_at, used | B0-08 | 🔴 |
| **B0-11** | **Modèle** `password_reset_tokens` : id, user_id FK, token CHAR(64), expires_at, used | B0-08 | 🔴 |
| **B0-12** | Migration Alembic : créer toutes les tables Phase 0 (`users`, `api_keys`, `tokens`) | B0-09, B0-10, B0-11 | 🔴 |
| **B0-13** | **Schemas** `auth.py` : RegisterRequest, LoginRequest, GoogleLoginRequest, AuthResponse (api_key + UserResponse), ForgotPasswordRequest, ResetPasswordRequest | B0-08 | 🔴 |
| **B0-14** | `utils/hashing.py` : `hash_password`, `verify_password` (bcrypt), `generate_api_key` (SHA-256 + salt), `compare_digest` (constant time) | — | 🔴 |
| **B0-15** | `utils/i18n.py` : chargement des fichiers `locales/*.json`, fonction `t(key, locale, **kwargs)` | — | 🔴 |
| **B0-16** | Fichiers `locales/fr.json` + `locales/en.json` : toutes les clés d'erreur auth | B0-15 | 🔴 |
| **B0-17** | **Repository** `user_repository.py` : get_by_id, get_by_email, create, update, soft_delete | B0-08 | 🔴 |
| **B0-18** | **Repository** `api_key_repository.py` : create, get_by_hash, revoke, revoke_all_for_user, update_last_used | B0-09 | 🔴 |
| **B0-19** | `auth/utils.py` : `verify_google_token` (via google-auth lib + validation iss/aud), `get_locale_from_request` (header Accept-Language) | — | 🔴 |
| **B0-20** | `auth/middleware.py` : `get_current_user` (lookup api_key → user), `require_coach`, `require_client`, `require_admin` | B0-17, B0-18 | 🔴 |
| **B0-21** | **Service** `auth_service.py` : `register`, `verify_email`, `login_with_email`, `login_with_google`, `logout`, `logout_all`, `forgot_password`, `reset_password` | B0-17, B0-18, B0-14, B0-19 | 🔴 |
| **B0-22** | **Router** `auth.py` : POST /auth/register, GET /auth/verify-email, POST /auth/login, POST /auth/google, DELETE /auth/logout, DELETE /auth/logout-all, GET /auth/me, POST /auth/forgot-password, POST /auth/reset-password | B0-21, B0-13 | 🔴 |
| **B0-23** | `main.py` : création app FastAPI, montage router auth, middleware CORS (strict), middleware security headers, rate limiter (slowapi), handler exceptions globales | B0-22 | 🔴 |
| **B0-24** | `GET /health` : retourne `{ "status": "ok", "db": "ok" }` sans authentification | B0-05 | 🟡 |
| **B0-25** | **Tests** `tests/conftest.py` : fixture DB PostgreSQL de test (docker-compose.test.yml), fixture `client` (TestClient async), fixtures `coach_user`, `client_user`, `admin_user`, `valid_api_key` | B0-22 | 🔴 |
| **B0-26** | **Tests** `tests/test_auth.py` : register (OK, email dupe, password faible), verify_email (OK, token expiré, token invalide), login (OK, bad credentials, compte non vérifié, rate limit), google login (OK, token invalide), logout (OK, clé déjà révoquée), me (OK, 401) | B0-25 | 🔴 |

---

## PHASE 1 — Espace Coach

> Pré-requis : Phase 0 100% ✅
> Objectif : profil coach complet, tarification, disponibilités, politique d'annulation, gestion clients, paiements.

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B1-01** | **Modèle** `gym_chains` : id, name, logo_url, website | — | 🔴 |
| **B1-02** | **Modèle** `gyms` : id, chain_id FK, name, address, zip_code, city, country (ISO 3166-1 alpha-2), lat NUMERIC, lng NUMERIC | B1-01 | 🔴 |
| **B1-03** | **Modèle** `coach_profiles` : user_id FK (1-1), bio, verified, country, currency (ISO 4217), session_duration_min, discovery_enabled, discovery_free, discovery_price_cents | B0-08 | 🔴 |
| **B1-04** | **Modèle** `coach_specialties` : id, coach_id FK, specialty (enum) | B1-03 | 🔴 |
| **B1-05** | **Modèle** `coach_certifications` : id, coach_id FK, name, organization, year, document_url, verified | B1-03 | 🔴 |
| **B1-06** | **Modèle** `coach_gyms` (M-M) : coach_id FK, gym_id FK | B1-03, B1-02 | 🔴 |
| **B1-07** | **Modèle** `coach_pricing` : id, coach_id FK, type (enum: per_session/package), name, session_count, price_cents, currency, validity_months, is_public | B1-03 | 🔴 |
| **B1-08** | **Modèle** `coach_work_schedule` : id, coach_id FK, day_of_week (0=Lun, 6=Dim), is_working_day BOOL, time_slots JSONB `[{start_time, end_time}]` (plusieurs créneaux par jour possibles) | B1-03 | 🔴 |
| **B1-08b** | **Modèle** `coach_availability` : id, coach_id FK, day_of_week (0-6), start_time, end_time, max_slots (nb places par créneau), booking_horizon_days, active — dérivé de work_schedule | B1-08 | 🔴 |
| **B1-09** | **Modèle** `cancellation_policies` : id, coach_id FK (1-1), threshold_hours, mode (auto/manual), noshow_is_due, client_message | B1-03 | 🔴 |
| **B1-10** | **Modèle** `coaching_relations` : id, coach_id FK, client_id FK, status (enum: pending/discovery/active/paused/ended), created_at, updated_at | B1-03 | 🔴 |
| **B1-11** | **Modèle** `coach_client_notes` : id, coach_id FK, client_id FK, content, updated_at | B1-10 | 🟡 |
| **B1-12** | **Modèle** `client_profiles` : user_id FK (1-1), birth_date, weight_kg NUMERIC(5,2), height_cm, goal (enum), level (enum), weight_unit (kg/lb), country | B0-08 | 🔴 |
| **B1-13** | **Modèle** `packages` (forfaits achetés) : id, client_id FK, coach_id FK, pricing_id FK, sessions_total, sessions_remaining, price_cents, currency, status, valid_until, created_at | B1-07, B1-12 | 🔴 |
| **B1-14** | **Modèle** `payments` : id, package_id FK, coach_id FK, client_id FK, amount_cents, currency, payment_method (enum), reference, status (enum: pending/paid/late), paid_at | B1-13 | 🔴 |
| **B1-15** | Migration Alembic : toutes les tables Phase 1 | B1-01 → B1-14 | 🔴 |
| **B1-16** | Script `scripts/seed_gyms.py` : import CSV des salles (Fitness Park, Basic-Fit, L'Orange Bleue, Keep Cool, Elancia, Neoness, GoFit, CMG, Wellness, Moving, Anytime Fitness, PureGym, McFit, Holmes Place, Virgin Active) avec country ISO 3166-1 | B1-15 | 🟡 |
| **B1-17** | **Schemas** `coach.py` : CoachProfileCreate, CoachProfileUpdate, CoachProfileResponse, SpecialtyEnum, CertificationCreate, PricingCreate, PricingResponse, AvailabilityCreate, CancellationPolicyUpdate | B1-03 → B1-09 | 🔴 |
| **B1-18** | **Schemas** `client.py` (vue coach) : ClientSummary, ClientDetail, CoachNoteUpdate, RelationStatusUpdate | B1-10 | 🔴 |
| **B1-19** | **Schemas** `payment.py` : PackageCreate, PaymentRecord, PaymentHistoryItem, HoursSummary | B1-13, B1-14 | 🔴 |
| **B1-20** | **Repository** `coach_repository.py` : get_by_user_id, create_profile, update_profile, get_clients (filtré/paginé/trié), search (public, avec filtres) | B1-03 → B1-11 | 🔴 |
| **B1-21** | **Repository** `gym_repository.py` : search (chain, country, city, zip, q), get_by_id, get_chains | B1-01, B1-02 | 🔴 |
| **B1-22** | **Repository** `payment_repository.py` : create_package, record_payment, get_active_package, deduct_session, get_history, count_remaining | B1-13, B1-14 | 🔴 |
| **B1-23** | **Service** `coach_service.py` : create_profile, update_profile, get_public_profile, list_clients, update_client_relation, update_note, list_available_slots (calcul depuis availability - bookings), set_cancellation_policy | B1-20 | 🔴 |
| **B1-24** | **Service** `payment_service.py` : create_package_for_client, record_payment, deduct_session (appelé après séance done), check_package_alerts | B1-22 | 🔴 |
| **B1-25** | **Router** `coaches.py` : POST /coaches/profile, PUT /coaches/profile, GET /coaches/profile, GET /coaches/clients (paginé), GET /coaches/clients/{id}, PUT /coaches/clients/{id}/relation, PUT /coaches/clients/{id}/note, CRUD /coaches/pricing, CRUD /coaches/availability, PUT /coaches/cancellation-policy | B1-23, B1-17, B1-18 | 🔴 |
| **B1-26** | **Router** `gyms.py` : GET /gyms (filtres: chain, country, city, q, paginator) | B1-21 | 🔴 |
| **B1-27** | **Router** `payments.py` : POST /coaches/clients/{id}/packages, POST /coaches/clients/{id}/payments, GET /coaches/clients/{id}/payments (historique), GET /coaches/clients/{id}/hours | B1-24, B1-19 | 🔴 |
| **B1-28** | **Tests** `tests/test_coaches.py` : CRUD profil, listing clients (filtres), recherche salles, création forfait, enregistrement paiement, décompte heures, alerte 2 séances restantes | B1-25, B1-27 | 🔴 |
| **B1-29** | **Modèle** `cancellation_message_templates` : id, coach_id FK, title (VARCHAR 40), body (VARCHAR 300), variables_used[] (jsonb — liste des {var} détectées), is_default BOOL, position SMALLINT (1-5), created_at, updated_at. Contrainte : max 5 par coach (CHECK + trigger). Seed : 1 template "Maladie" créé automatiquement à la création du profil coach | B1-03 | 🔴 |
| **B1-30** | Migration Alembic : table `cancellation_message_templates` | B1-29 | 🔴 |
| **B1-31** | **Schemas** `cancellation_template.py` : `CancellationTemplateCreate` (title, body), `CancellationTemplateUpdate` (title?, body?, position?), `CancellationTemplateResponse` (id, title, body, is_default, position, variables_used), `CancellationTemplatePreview` (resolved_body, client_name) | B1-29 | 🔴 |
| **B1-32** | **Repository** `cancellation_template_repository.py` : list_by_coach (ordered by position), get_by_id_and_coach, create (enforce max 5), update, delete (refuse si seul template), reorder (swap positions) | B1-30 | 🔴 |
| **B1-33** | **Service** `cancellation_template_service.py` : list_templates, create_template (validate max 5, extract variables), update_template, delete_template, reorder_templates, preview_template (résoudre `{prénom}`, `{date}`, `{heure}`, `{coach}` depuis un booking donné), seed_default_template (appelé par coach_service à la création profil) | B1-32 | 🔴 |
| **B1-34** | **Router** `cancellation_templates.py` : `GET /coaches/cancellation-templates`, `POST /coaches/cancellation-templates`, `PUT /coaches/cancellation-templates/{id}`, `DELETE /coaches/cancellation-templates/{id}`, `POST /coaches/cancellation-templates/{id}/preview` (body: booking_id → retourne message résolu), `POST /coaches/cancellation-templates/reorder` (body: [{id, position}]) | B1-33, B1-31 | 🔴 |
| **B1-35** | **Tests** `tests/test_cancellation_templates.py` : liste vide → seed auto, CRUD complet, refus au-delà de 5 templates, refus suppression du dernier, preview résolution variables, reorder | B1-34 | 🔴 |

---

## PHASE 2 — Espace Client & Réservations

> Pré-requis : Phase 1 100% ✅
> Objectif : profil client, questionnaire, recherche coach, réservation, annulation, liste d'attente, notifications.

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B2-01** | **Modèle** `client_questionnaires` : id, client_id FK (1-1), goal, level, frequency_per_week, session_duration_min, equipment[] (jsonb), target_zones[] (jsonb), injuries (text), injury_zones[] (jsonb), updated_at | B1-12 | 🔴 |
| **B2-02** | **Modèle** `client_gyms` (M-M) : client_id FK, gym_id FK | B1-12, B1-02 | 🔴 |
| **B2-03** | **Modèle** `coaching_requests` : id, client_id FK, coach_id FK, status (pending/accepted/rejected/cancelled), client_message, coach_message, discovery_slot TIMESTAMPTZ, created_at | B1-10 | 🔴 |
| **B2-04** | **Modèle** `bookings` : id, client_id FK, coach_id FK, pricing_id FK nullable, package_id FK nullable, scheduled_at TIMESTAMPTZ, duration_min, gym_id FK nullable, status (enum: pending_coach_validation/confirmed/done/cancelled_by_client/cancelled_late_by_client/cancelled_by_coach/cancelled_by_coach_late/no_show/rejected/auto_rejected), client_message, coach_cancel_reason, late_cancel_waived, created_at, updated_at | B1-12, B1-07, B1-13 | 🔴 |
| **B2-05** | **Modèle** `waitlist_entries` : id, coach_id FK, slot_datetime TIMESTAMPTZ, client_id FK, position INT, status (waiting/notified/confirmed/expired/cancelled), notified_at, expires_at, created_at | B2-04 | 🔴 |
| **B2-06** | **Modèle** `push_tokens` : id, user_id FK, token, platform (android/ios), active, created_at | B0-08 | 🟡 |
| **B2-07** | Migration Alembic : tables Phase 2 | B2-01 → B2-06 | 🔴 |
| **B2-08** | **Schemas** `client.py` (complétés) : ClientProfileCreate, ClientProfileUpdate, QuestionnaireCreate, QuestionnaireUpdate, ClientProfileResponse | B2-01 | 🔴 |
| **B2-09** | **Schemas** `booking.py` : BookingCreate (client_id, coach_id, scheduled_at, pricing_type, package_id?), BookingResponse, BookingStatus enum, CoachingRequestCreate, CoachingRequestResponse, CancellationRequest, WaitlistJoinRequest | B2-03, B2-04, B2-05 | 🔴 |
| **B2-10** | **Repository** `client_repository.py` : create_profile, update_profile, get_by_user_id, create_questionnaire, update_questionnaire | B2-01, B2-02 | 🔴 |
| **B2-11** | **Repository** `booking_repository.py` : create, get_by_id, update_status, get_by_client, get_by_coach, get_by_slot (count occupied), count_pending_for_client, get_upcoming, get_past | B2-04 | 🔴 |
| **B2-12** | **Repository** `waitlist_repository.py` : add_entry, get_first_waiting, get_by_client, remove_entry, update_status, get_all_for_slot (ordered by position), reorder | B2-05 | 🔴 |
| **B2-13** | **Service** `client_service.py` : create_profile, update_profile, search_coaches (filtres + pagination), get_coach_public_profile, send_discovery_request | B2-10, B1-20 | 🔴 |
| **B2-14** | **Service** `booking_service.py` : create_booking (vérifie dispo, prix, max slots), confirm_booking (coach), reject_booking (coach), cancel_booking (applique règle pénalité < threshold_hours → late), waive_penalty, mark_no_show, auto_reject_expired (worker) | B2-11, B1-23, B1-24 | 🔴 |
| **B2-15** | **Service** `waitlist_service.py` : join_waitlist (avec position), notify_next (envoie notif push, set expires_at = now+30min), confirm_from_waitlist (dans la fenêtre), expire_entry (si 30min passées → notify suivant), leave_waitlist | B2-12 | 🔴 |
| **B2-16** | **Service** `notification_service.py` : intégration Firebase Admin SDK, méthode `send_push(user_id, title_key, body_key, data, locale)` — traduit via i18n avant envoi | B0-15, B2-06 | 🔴 |
| **B2-17** | Intégration des notifications dans `booking_service.py` et `waitlist_service.py` (tous les déclencheurs du catalogue §21 des specs) | B2-14, B2-15, B2-16 | 🔴 |
| **B2-18** | Worker async `auto_reject_expired_bookings` : tâche périodique (APScheduler ou Celery), passe en `auto_rejected` les `pending_coach_validation` vieux de 24h | B2-14 | 🟡 |
| **B2-19** | Worker async `expire_waitlist_notifications` : passe en `expired` les `notified` dont `expires_at` est dépassé, appelle `notify_next` | B2-15 | 🟡 |
| **B2-20** | **Router** `clients.py` : POST /clients/profile, PUT /clients/profile, GET /clients/profile, POST /clients/questionnaire, PUT /clients/questionnaire, GET /coaches/search, GET /coaches/{id}/public, GET /coaches/{id}/slots | B2-13, B2-08 | 🔴 |
| **B2-21** | **Router** `bookings.py` : POST /bookings, POST /bookings/{id}/confirm, POST /bookings/{id}/reject, DELETE /bookings/{id}, POST /bookings/{id}/waive-penalty, POST /bookings/{id}/no-show, GET /bookings (client ou coach) | B2-14, B2-09 | 🔴 |
| **B2-22** | **Router** `waitlist.py` : POST /waitlist/{coach_id}/{slot_datetime}, DELETE /waitlist/{id}, POST /waitlist/{id}/confirm, GET /waitlist/{coach_id}/{slot_datetime} (vue coach) | B2-15 | 🔴 |
| **B2-23** | **Router** `push.py` : POST /push/register (enregistre le token Firebase) | B2-06 | 🟡 |
| **B2-24** | **Tests** `tests/test_clients.py` : création profil, questionnaire, recherche coaches (filtres), profil public | B2-20 | 🔴 |
| **B2-25** | **Tests** `tests/test_bookings.py` : réservation (OK, créneau complet, doublon), confirmation coach (OK, délai expiré), annulation (> délai = libre, < délai = pénalité), exonération pénalité, no-show, auto-reject | B2-21 | 🔴 |
| **B2-26** | **Tests** `tests/test_waitlist.py` : rejoindre (OK, position), libération place → notification 1er, confirmation dans fenêtre (OK), expiration 30min → notification suivant, quitter la file | B2-22 | 🔴 |
| **B2-27** | **Modèle** `sms_logs` : id, coach_id FK, client_id FK nullable, template_id FK nullable, recipient_phone E.164, message_body TEXT, status (enum: pending/sent/failed), provider_message_id VARCHAR nullable, error_message VARCHAR nullable, sent_at TIMESTAMPTZ, created_at | B1-29 | 🔴 |
| **B2-28** | Migration Alembic : table `sms_logs` | B2-27 | 🔴 |
| **B2-29** | **Abstraction SMS** `app/core/sms/` : interface `SmsProvider` (méthodes: `send(to: str, body: str) → SmsResult`), implémentation `TwilioSmsProvider` (config: account_sid, auth_token, from_number depuis Settings), implémentation `ConsoleSmsProvider` (dev/test — log uniquement). Factory `get_sms_provider()` depuis `APP_ENV` | — | 🟡 |
| **B2-30** | **Schemas** `sms.py` : `SmsLogResponse` (id, recipient_phone, message_body, status, sent_at), `BulkCancelRequest` (booking_ids: list[UUID], template_id: UUID nullable, custom_message: str nullable, send_sms: bool), `BulkCancelResponse` (cancelled_count, sms_sent_count, sms_failed_count, failed_clients: list[str]), `SmsBroadcastRequest` (scope: all/day/manual, day: date nullable, client_ids: list nullable, template_id: UUID nullable, custom_message: str nullable), `SmsBroadcastResponse` | B2-27, B1-31 | 🔴 |
| **B2-31** | **Repository** `sms_log_repository.py` : create_log, update_status (pending→sent/failed), list_by_coach (paginé, filtres: status, date_from/to), get_by_id | B2-27 | 🔴 |
| **B2-32** | **Service** `bulk_cancel_service.py` : `bulk_cancel_bookings(coach_id, booking_ids, template_id?, custom_message?, send_sms) → BulkCancelResult` — (1) vérifie que tous les booking_ids appartiennent au coach, (2) passe chaque séance en `cancelled_by_coach` via `booking_service`, (3) libère créneaux + notifie liste d'attente, (4) si `send_sms=True` → résout template par client → appelle `SmsProvider.send()` → crée `sms_log`. Atomique : si annulation DB échoue → rollback. SMS best-effort : un échec SMS n'annule pas le rollback | B2-28, B2-29, B2-30, B2-31, B1-33 | 🔴 |
| **B2-33** | **Service** `sms_broadcast_service.py` : `broadcast(coach_id, scope, day?, client_ids?, template_id?, custom_message?) → SmsBroadcastResult` — résout les destinataires selon scope, filtre clients sans numéro, résout template, envoie via `SmsProvider`, log chaque envoi | B2-29, B2-31 | 🟡 |
| **B2-34** | **Router** `bulk_actions.py` : `POST /coaches/bookings/bulk-cancel` (body: BulkCancelRequest → BulkCancelResponse), `POST /coaches/sms/broadcast` (body: SmsBroadcastRequest → SmsBroadcastResponse), `GET /coaches/sms/logs` (paginé, filtres) | B2-32, B2-33, B2-30 | 🔴 |
| **B2-35** | **Tests** `tests/test_bulk_cancel.py` : annulation 3 séances OK, refus si booking d'un autre coach, SMS envoyé (mock provider), SMS non envoyé si pas de numéro, récap correct (N annulées, M SMS envoyés, K échoués). `tests/test_sms_broadcast.py` : scope=all, scope=day, scope=manual, aucun destinataire → réponse vide | B2-34 | 🔴 |

---

## PHASE 3 — Performances

> Pré-requis : Phase 2 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B3-01** | **Modèles** `exercise_types`, `exercise_muscles` (M-M) : id, name (i18n key), category (enum), difficulty, video_url, thumbnail_url, instructions[] (jsonb) | — | 🔴 |
| **B3-02** | **Modèle** `machines` : id, type_key (enum), brand, model, photo_url, qr_code_hash UNIQUE nullable, validated, submitted_by FK, validated_by FK, created_at | B3-01 | 🔴 |
| **B3-03** | **Modèle** `machine_exercises` (M-M) : machine_id FK, exercise_type_id FK | B3-01, B3-02 | 🔴 |
| **B3-04** | **Modèle** `performance_sessions` : id, user_id FK, session_type (enum: solo_free/solo_guided/coached), booking_id FK nullable, entered_by FK nullable, gym_id FK nullable, date TIMESTAMPTZ, duration_min, feeling (1-5), strava_activity_id nullable, created_at | B2-04 | 🔴 |
| **B3-05** | **Modèle** `exercise_sets` : id, session_id FK, exercise_type_id FK, machine_id FK nullable, set_order, sets_count, reps, weight_kg NUMERIC(6,2), notes | B3-04, B3-01 | 🔴 |
| **B3-06** | **Modèle** `personal_records` : id, user_id FK, exercise_type_id FK, weight_kg, achieved_at, session_id FK | B3-04 | 🔴 |
| **B3-07** | Migration Alembic : tables Phase 3 | B3-01 → B3-06 | 🔴 |
| **B3-08** | Seed : exercices de base (50+ exercices avec muscles, catégorie, difficulté) | B3-07 | 🟡 |
| **B3-09** | **Schemas** `performance.py` : PerformanceSessionCreate, ExerciseSetCreate, PerformanceSessionResponse, ProgressionStats, WeekStats, PersonalRecord | B3-04, B3-05 | 🔴 |
| **B3-10** | **Repository** `performance_repository.py` : create_session, get_by_id, update (< 48h only), delete (< 48h only), get_history (filtré), get_progression_stats (max weight + volume par date), get_week_stats, get_personal_records | B3-04, B3-05, B3-06 | 🔴 |
| **B3-11** | **Service** `performance_service.py` : create_session, update_session (check 48h + auteur), delete_session (check 48h), detect_new_pr (compare avec historique → si PR → notif push), get_progression, get_week_dashboard | B3-10, B2-16 | 🔴 |
| **B3-12** | **Router** `performances.py` : POST /performances, POST /performances/for-client/{id} (coach), PUT /performances/{id}, DELETE /performances/{id}, GET /performances, GET /performances/stats/exercise/{id}, GET /performances/stats/week | B3-11, B3-09 | 🔴 |
| **B3-13** | **Router** `exercises.py` : GET /exercises (searchable), GET /machines/qr/{hash}, POST /machines/submit | B3-01, B3-02 | 🔴 |
| **B3-14** | **Router** `admin.py` (machines) : GET /admin/machines/pending, POST /admin/machines/{id}/validate, POST /admin/machines/{id}/reject | B3-02 | 🔴 |
| **B3-15** | **Tests** `tests/test_performances.py` : créer session (OK, avec coach), modifier (OK, > 48h interdit, autre user interdit), supprimer (idem), stats progression, détection PR + notif | B3-12 | 🔴 |

---

## PHASE 4 — Intelligence IA & Programmes

> Pré-requis : Phase 3 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B4-01** | **Modèles** `workout_plans` : id, name, description, duration_weeks, level, goal, created_by FK, is_ai_generated, created_at | B1-12 | 🔴 |
| **B4-02** | **Modèle** `plan_assignments` : id, plan_id FK, client_id FK, start_date, mode (replace_ai/complement), assigned_by FK, created_at | B4-01 | 🔴 |
| **B4-03** | **Modèle** `planned_sessions` : id, plan_id FK, day_of_week (0-6), session_name, estimated_duration_min, rest_seconds | B4-01 | 🔴 |
| **B4-04** | **Modèle** `planned_exercises` : id, planned_session_id FK, exercise_type_id FK, target_sets, target_reps, target_weight_kg nullable, order_index | B4-03, B3-01 | 🔴 |
| **B4-05** | **Modèle** `exercise_videos` : id, exercise_type_id FK (1-1), video_url, status (enum: pending/generating/validating/published/rejected), generated_prompt, generated_at, validated_by FK nullable | B3-01 | 🟡 |
| **B4-06** | Migration Alembic : tables Phase 4 | B4-01 → B4-05 | 🔴 |
| **B4-07** | **Service** `program_generator_service.py` : `generate_weekly_program(questionnaire)` → `WorkoutPlan` (règles métier : distribution musculaire, alternance, repos) | B4-01, B4-03, B4-04 | 🔴 |
| **B4-08** | **Service** `progression_service.py` : `check_and_adjust(client_id, exercise_type_id)` → analyse 3 dernières séances → ajuste `target_weight_kg` si règle atteinte → notif push | B3-10, B2-16 | 🔴 |
| **B4-09** | **Repository** `program_repository.py` : CRUD plans, assign, get_current_for_client, get_progress (séances réalisées vs planifiées), get_exercise_progress (réel vs cible) | B4-01 → B4-04 | 🔴 |
| **B4-10** | **Service** `program_service.py` : create_plan (coach), duplicate, archive, assign_to_client, get_client_progress | B4-09 | 🔴 |
| **B4-11** | **Router** `programs.py` : GET /clients/program, POST /clients/program/recalibrate, CRUD /coaches/programs, POST /coaches/programs/{id}/assign, GET /coaches/clients/{id}/program-progress | B4-07, B4-10 | 🔴 |
| **B4-12** | **Router** `admin.py` (vidéos) : POST /admin/videos/generate/{exercise_id}, GET /admin/videos/pending, POST /admin/videos/{id}/validate, POST /admin/videos/{id}/reject | B4-05 | 🟡 |
| **B4-13** | **Tests** `tests/test_programs.py` : génération programme IA (structure valide), CRUD programmes coach, assignation, progression, ajustement charges | B4-11 | 🔴 |

---

## PHASE 5 — Intégrations

> Pré-requis : Phase 3 100% ✅ (parallèle avec Phase 4)

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B5-01** | **Modèle** `oauth_tokens` : id, user_id FK, provider (strava/google_calendar/withings/garmin), access_token (chiffré), refresh_token (chiffré), expires_at, scope, created_at | B0-08 | 🔴 |
| **B5-02** | **Modèle** `body_measurements` : id, user_id FK, measured_at TIMESTAMPTZ, weight_kg, bmi, fat_pct, muscle_pct, bone_kg, water_pct, source (enum: withings/xiaomi/garmin/manual) | B0-08 | 🔴 |
| **B5-03** | Migration Alembic : tables Phase 5 | B5-01, B5-02 | 🔴 |
| **B5-04** | **Service** `strava_service.py` : OAuth2 authorize/callback, push_session (WeightTraining/Workout), import_activities | B5-01, B3-04 | 🔴 |
| **B5-05** | **Service** `calendar_service.py` : Google Calendar OAuth2 authorize/callback, sync_booking (push/update/delete event), sync_all_confirmed | B5-01, B2-04 | 🟡 |
| **B5-06** | **Service** `scale_service.py` : Withings OAuth2 authorize/callback, import_measurements, manual_entry | B5-01, B5-02 | 🟡 |
| **B5-07** | **Router** `integrations.py` : GET+GET-callback /integrations/strava, POST /integrations/strava/push/{session_id}, GET /integrations/strava/import, idem calendar, idem scale, POST /integrations/scale/manual, GET /integrations/scale/history | B5-04, B5-05, B5-06 | 🔴 |
| **B5-08** | **Tests** `tests/test_integrations.py` : mocks OAuth flows, push Strava (format activité correct), import balance (mapping champs), sync calendar | B5-07 | 🟡 |

---

## PHASE 6 — Finalisation

> Pré-requis : Phases 4 + 5 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **B6-01** | Audit OWASP API Top 10 : revue de chaque endpoint (BOLA, rate limiting, validation, CORS, headers) | Toutes | 🔴 |
| **B6-02** | RGPD — Droit d'accès (Art. 15) : `GET /users/me/export` — dump complet JSON de toutes les données personnelles (profil, séances, paiements, messages chiffrés déchiffrés) | B0-22 | 🔴 |
| **B6-03** | RGPD — Droit à l'effacement (Art. 17) : `DELETE /users/me` → statut `deletion_pending`, anonymisation effective J+30 (cron), suppression champs PII, conservation données comptables anonymisées | B0-22 | 🔴 |
| **B6-04** | RGPD — Droit à la portabilité (Art. 20) : export `GET /users/me/export?format=csv` + format JSON structuré, téléchargeable 24h via lien signé | B6-02 | 🟡 |
| **B6-05** | RGPD — Consentement & registre : modèle `consents` (type, version, accepted_at, ip_hash, user_agent_hash) · endpoints `POST /consents` · `GET /consents` · log immuable (pas de DELETE) | B0-22 | 🔴 |
| **B6-06** | RGPD — Registre des traitements : document `docs/RGPD_REGISTRE.md` (finalités, base légale, durée conservation, sous-traitants — Twilio, Google, Strava, Withings) | — | 🔴 |
| **B6-07** | RGPD — Notification violation de données : procédure `docs/RGPD_BREACH.md` (72h CNIL, template notification utilisateurs, log incidents) | — | 🟡 |
| **B6-08** | Optimisation : index PostgreSQL manquants, requêtes N+1, EXPLAIN ANALYZE sur les requêtes critiques | Toutes | 🟡 |
| **B6-09** | Documentation OpenAPI : descriptions de tous les endpoints, exemples de requêtes/réponses | Toutes | 🟡 |
| **B6-10** | Tests de charge (locust) : scénarios réservation simultanée, liste d'attente sous pression | Toutes | 🟡 |
| **B6-11** | Hardening Docker : image non-root, secrets via Docker secrets, healthcheck sur tous les services | — | 🔴 |

---

## Légende priorités

| Symbole | Signification |
|---------|---------------|
| 🔴 | Bloquant — ne pas passer à la suite sans cette tâche |
| 🟡 | Important — à faire dans la phase mais non bloquant pour les suivantes |
| 🟢 | Optionnel — amélioration, peut être différé |

---

## Phase 7 — Réseaux sociaux (B7)

### B7-01 — Modèle user_social_links ✅
- [x] Model SocialLink (SQLAlchemy) — platform nullable, label, visibility, position
- [x] Migration `008_phase7_social_links` — index partiel UNIQUE (user_id, platform) WHERE platform IS NOT NULL
- [x] Relation `User.social_links` (cascade all, delete-orphan)

### B7-02 — API CRUD liens sociaux ✅
- [x] `social_link_repository` — upsert_standard, create_custom, get_by_id, count_by_user, update_link, delete_link, get_by_user_public
- [x] `social_link_service` — create_or_upsert_link, update_link, delete_link, list_public_links + TooManyLinksError
- [x] Router `GET /users/me/social-links` — liste complète (owner)
- [x] Router `POST /users/me/social-links` — upsert standard OU insert custom (max 20)
- [x] Router `PUT /users/me/social-links/{id}` — modifier url/label/visibility/position
- [x] Router `DELETE /users/me/social-links/{id}` — suppression par ID
- [x] Endpoint public `GET /coaches/{id}/social-links` — filtre visibility='public'
- [x] 26 tests passants (couvre : basic CRUD, custom, visibilité, max 20, isolation, auth)

### B7-03 — Intégration profil coach (à faire)
- [ ] Inclure `social_links` dans `CoachProfileResponse` (champ optionnel)
- [ ] Inclure dans `GET /coaches/search` (au moins les 3 premiers liens)

### B7-04 — Évolution liste plateformes (futur)
- [ ] Table `social_platforms` (admin CRUD) — slug, label, icon_url, active
- [ ] Endpoint `GET /social-platforms` — liste publique des plateformes actives
- [ ] Android : charger dynamiquement la liste depuis l'API

---

## Phase 9 — Liens d'enrôlement coach (B9)

### B9-01 — Modèle CoachEnrollmentToken ✅
- [x] Model `CoachEnrollmentToken` (SQLAlchemy) — token, label, expires_at, max_uses, uses_count, active
- [x] Migration `011_phase9_enrollment_tokens` — table + index UNIQUE sur token + index coach_id
- [x] Relation `User.enrollment_tokens` (cascade all, delete-orphan)

### B9-02 — API CRUD tokens d'enrôlement ✅
- [x] `enrollment_repository` — create_token, get_by_token, get_by_id, list_by_coach, increment_uses, deactivate
- [x] `enrollment_service` — create_token, list_tokens, deactivate_token, validate_token, get_coach_info_for_token, consume_token
- [x] Router `POST /coaches/me/enrollment-tokens` — créer un lien (label/expires_at/max_uses optionnels)
- [x] Router `GET /coaches/me/enrollment-tokens` — lister ses liens
- [x] Router `DELETE /coaches/me/enrollment-tokens/{id}` — désactiver un lien
- [x] Endpoint public `GET /enroll/{token}` — infos coach pour l'écran de pré-inscription

### B9-03 — Intégration inscription ✅
- [x] `RegisterRequest.enrollment_token` (optionnel)
- [x] `auth_service.register()` — consomme le token après création user
- [x] Token invalide/expiré → inscription réussit quand même (pas de blocage)
- [x] coaching_relation créée si token valide (status="active")

### B9-04 — Tests ✅
- [x] 13 tests couvrant : création, label, auth, liste, désactivation, ownership, infos publiques, inscription avec token valide/expiré/invalide, max_uses, uses_count
