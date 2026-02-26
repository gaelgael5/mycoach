# MyCoach — Suivi de progression

> Ce fichier est maintenu par l'agent IA codeur.
> Mis à jour après chaque tâche terminée.
> Le détail des tâches est dans : `docs/TASKS_BACKEND.md` et `docs/TASKS_ANDROID.md`
>
> Statuts : ⬜ À faire | 🔄 En cours | ✅ Terminé | ⛔ Bloqué

---

Dernière mise à jour : —
Répertoire back : `backend/`
Répertoire android : `android/`
**Prochaine tâche : B2-01** — Modèle client_questionnaires

---

## Backend (backend/) — TASKS_BACKEND.md

### Phase 0 — Fondations
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B0-01 | Structure dossiers backend/ | ✅ | 26/02/2026 |
| B0-02 | pyproject.toml (pytest, black, ruff) | ✅ | 26/02/2026 |
| B0-03 | requirements.txt | ✅ | 26/02/2026 |
| B0-04 | config.py (pydantic-settings) | ✅ | 26/02/2026 |
| B0-05 | database.py (SQLAlchemy async) | ✅ | 26/02/2026 |
| B0-06 | docker-compose.yml (PostgreSQL + backend) | ✅ | 26/02/2026 |
| B0-07 | Alembic init + env.py async | ✅ | 26/02/2026 |
| B0-08 | Modèle users | ✅ | 26/02/2026 |
| B0-09 | Modèle api_keys | ✅ | 26/02/2026 |
| B0-10 | Modèle email_verification_tokens | ✅ | 26/02/2026 |
| B0-11 | Modèle password_reset_tokens | ✅ | 26/02/2026 |
| B0-12 | Migration Alembic Phase 0 | ✅ | 26/02/2026 |
| B0-13 | Schemas auth.py (Pydantic) | ✅ | 26/02/2026 |
| B0-14 | utils/hashing.py | ✅ | 26/02/2026 |
| B0-15 | utils/i18n.py | ✅ | 26/02/2026 |
| B0-16 | locales/fr.json + locales/en.json | ✅ | 26/02/2026 |
| B0-17 | Repository user_repository.py | ✅ | 26/02/2026 |
| B0-18 | Repository api_key_repository.py | ✅ | 26/02/2026 |
| B0-19 | auth/utils.py (verify_google_token) | ✅ | 26/02/2026 |
| B0-20 | auth/middleware.py (get_current_user) | ✅ | 26/02/2026 |
| B0-21 | Service auth_service.py | ✅ | 26/02/2026 |
| B0-22 | Router auth.py (tous les endpoints /auth) | ✅ | 26/02/2026 |
| B0-23 | main.py (app, CORS, headers, rate limiter) | ✅ | 26/02/2026 |
| B0-24 | GET /health | ✅ | 26/02/2026 |
| B0-25 | tests/conftest.py (fixtures) | ✅ | 26/02/2026 |
| B0-26 | tests/test_auth.py | ✅ | 26/02/2026 |

### Phase 1 — Espace Coach
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B1-01 à B1-35 | Phase 1 complète — 16 modèles, migration Alembic, 4 schemas, 4 repositories, 3 services, 4 routers, 42 tests (70/70 total) | ✅ | 26/02/2026 |

### Phase 2 — Client & Réservations
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B2-01 à B2-26 | Voir TASKS_BACKEND.md | ⬜ | |

### Phase 3 — Performances
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B3-01 à B3-15 | Voir TASKS_BACKEND.md | ⬜ | |

### Phase 4 — IA & Programmes
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B4-01 à B4-13 | Voir TASKS_BACKEND.md | ⬜ | |

### Phase 5 — Intégrations
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B5-01 à B5-08 | Voir TASKS_BACKEND.md | ⬜ | |

### Phase 6 — Finalisation
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| B6-01 à B6-06 | Voir TASKS_BACKEND.md | ⬜ | |

---

## Android (android/) — TASKS_ANDROID.md

### Phase 0 — Fondations Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A0-01 | Init projet Android | ⬜ | |
| A0-02 | build.gradle.kts (dépendances) | ⬜ | |
| A0-03 | network_security_config.xml | ⬜ | |
| A0-04 | backup_rules.xml | ⬜ | |
| A0-05 | Color.kt (palettes Coach + Client) | ⬜ | |
| A0-06 | Typography.kt (Space Grotesk) | ⬜ | |
| A0-07 | Theme.kt (CoachTheme + ClientTheme) | ⬜ | |
| A0-08 | UiState.kt (sealed class) | ⬜ | |
| A0-09 | Composants UI (Loading, Error, Empty) | ⬜ | |
| A0-10 | ApiKeyStore.kt (EncryptedSharedPreferences) | ⬜ | |
| A0-11 | SessionManager.kt | ⬜ | |
| A0-12 | ApiKeyInterceptor.kt | ⬜ | |
| A0-13 | ApiClient.kt (Retrofit + OkHttp) | ⬜ | |
| A0-14 | NetworkModule.kt (Hilt) | ⬜ | |
| A0-15 | LocaleHelper.kt | ⬜ | |
| A0-16 | PriceFormatter.kt | ⬜ | |
| A0-17 | DateTimeFormatter.kt | ⬜ | |
| A0-18 | WeightFormatter.kt | ⬜ | |
| A0-19 | AuthApiService.kt (Retrofit interface) | ⬜ | |
| A0-20 | DTOs auth | ⬜ | |
| A0-21 | AuthRepository.kt | ⬜ | |
| A0-22 | AuthModule.kt (Hilt) | ⬜ | |
| A0-23 | SplashFragment (auto-login) | ⬜ | |
| A0-24 | LoginFragment + LoginViewModel | ⬜ | |
| A0-25 | RegisterFragment + RegisterViewModel | ⬜ | |
| A0-26 | EmailVerificationFragment | ⬜ | |
| A0-27 | RoleSelectionFragment | ⬜ | |
| A0-28 | ForgotPassword + ResetPassword | ⬜ | |
| A0-29 | nav_graph.xml | ⬜ | |
| A0-30 | strings.xml EN + FR (Phase 0) | ⬜ | |
| A0-31 | Tests unitaires auth ViewModels | ⬜ | |

### Phase 1 — Coach Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A1-01 à A1-20 | Voir TASKS_ANDROID.md | ⬜ | |

### Phase 2 — Client Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A2-01 à A2-26 | Voir TASKS_ANDROID.md | ⬜ | |

### Phase 3 — Performances Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A3-01 à A3-20 | Voir TASKS_ANDROID.md | ⬜ | |

### Phase 4 — IA & Programmes Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A4-01 à A4-17 | Voir TASKS_ANDROID.md | ⬜ | |

### Phase 5 — Intégrations Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A5-01 à A5-12 | Voir TASKS_ANDROID.md | ⬜ | |

### Phase 6 — Launch Android
| ID | Tâche résumée | Statut | Notes |
|----|--------------|--------|-------|
| A6-01 à A6-12 | Voir TASKS_ANDROID.md | ⬜ | |

---

## Bugs & blocages actifs

| # | Description | Phase | Priorité | Statut |
|---|-------------|-------|----------|--------|
| — | — | — | — | — |

---

## Décisions prises en cours de dev

| Date | ID tâche | Décision | Raison |
|------|----------|----------|--------|
| — | — | — | — |
