# MyCoach — Suivi de progression

> Ce fichier est maintenu par l'agent IA codeur.
> Mis à jour après chaque tâche terminée.
> Format : ⬜ À faire | 🔄 En cours | ✅ Terminé | ⛔ Bloqué

---

Dernière mise à jour : —
Phase en cours : —
Prochaine tâche : **B0-1** — Initialiser le projet FastAPI

---

## Phase 0 — Fondations

### Back-end
| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B0-1 | Initialiser projet FastAPI (structure, config, requirements) | ⬜ | |
| B0-2 | Docker Compose (PostgreSQL 16 + backend) | ⬜ | |
| B0-3 | SQLAlchemy 2 async + asyncpg | ⬜ | |
| B0-4 | Alembic (init + première migration) | ⬜ | |
| B0-5 | Modèle `users` | ⬜ | |
| B0-6 | Modèle `api_keys` | ⬜ | |
| B0-7 | Utilitaire génération API Key (SHA-256) | ⬜ | |
| B0-8 | Middleware auth `get_current_user` | ⬜ | |
| B0-9 | Route `POST /auth/google` | ⬜ | |
| B0-10 | Route `POST /auth/register` + email vérification | ⬜ | |
| B0-11 | Route `GET /auth/verify-email` | ⬜ | |
| B0-12 | Route `POST /auth/login` | ⬜ | |
| B0-13 | Route `DELETE /auth/logout` | ⬜ | |
| B0-14 | Route `DELETE /auth/logout-all` | ⬜ | |
| B0-15 | Route `GET /auth/me` | ⬜ | |
| B0-16 | Routes reset password | ⬜ | |
| B0-17 | Système i18n backend (locales JSON) | ⬜ | |
| B0-18 | Middleware Accept-Language | ⬜ | |
| B0-19 | Route `GET /health` | ⬜ | |
| B0-20 | Tests unitaires auth complets | ⬜ | |

### Android
| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| A0-1 | Init projet Android (Hilt, Retrofit, Navigation) | ⬜ | |
| A0-2 | Design System (couleurs Coach/Client, typo) | ⬜ | |
| A0-3 | ApiClient Retrofit + ApiKeyInterceptor | ⬜ | |
| A0-4 | ApiKeyStore (EncryptedSharedPreferences) | ⬜ | |
| A0-5 | SplashScreen (auto-login) | ⬜ | |
| A0-6 | LoginScreen | ⬜ | |
| A0-7 | LoginViewModel | ⬜ | |
| A0-8 | RegisterScreen + RegisterViewModel | ⬜ | |
| A0-9 | EmailVerificationScreen | ⬜ | |
| A0-10 | RoleSelectionScreen | ⬜ | |
| A0-11 | ForgotPassword + ResetPassword | ⬜ | |
| A0-12 | i18n Android (strings.xml + LocaleHelper) | ⬜ | |
| A0-13 | Formatters i18n (poids, prix, dates) | ⬜ | |
| A0-14 | Tests unitaires ViewModels auth | ⬜ | |

---

## Phase 1 — Espace Coach
*(À démarrer après Phase 0 complète)*

### Back-end
| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B1-1 | Modèles BDD profil coach + salles | ⬜ | |
| B1-2 | Modèles BDD tarification + disponibilités + politique annulation | ⬜ | |
| B1-3 | API création profil coach | ⬜ | |
| B1-4 | API update profil coach | ⬜ | |
| B1-5 | API get profil coach | ⬜ | |
| B1-6 | API recherche clubs (filtres pays) | ⬜ | |
| B1-7 | Seed BDD répertoire salles | ⬜ | |
| B1-8 | API CRUD tarification | ⬜ | |
| B1-9 | API CRUD disponibilités | ⬜ | |
| B1-10 | API politique annulation | ⬜ | |
| B1-11 | Modèles BDD clients + notes | ⬜ | |
| B1-12 | API liste clients | ⬜ | |
| B1-13 | API fiche client | ⬜ | |
| B1-14 | API gestion relation client | ⬜ | |
| B1-15 | API note privée coach | ⬜ | |
| B1-16 | Modèles BDD paiements + forfaits | ⬜ | |
| B1-17 | API CRUD paiements | ⬜ | |
| B1-18 | API heures consommées | ⬜ | |
| B1-19 | Tests unitaires Phase 1 back | ⬜ | |

### Android
| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| A1-1 à A1-12 | (voir CODING_AGENT.md §6 Phase 1) | ⬜ | |

---

## Phase 2 — Espace Client
*(À démarrer après Phase 1 complète)*

| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B2-1 à B2-24 | (voir CODING_AGENT.md §6 Phase 2) | ⬜ | |
| A2-1 à A2-13 | (voir CODING_AGENT.md §6 Phase 2) | ⬜ | |

---

## Phase 3 — Performances
*(À démarrer après Phase 2 complète)*

| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B3-1 à B3-16 | (voir CODING_AGENT.md §6 Phase 3) | ⬜ | |
| A3-1 à A3-13 | (voir CODING_AGENT.md §6 Phase 3) | ⬜ | |

---

## Phase 4 — Intelligence IA
*(À démarrer après Phase 3 complète)*

| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B4-1 à B4-12 | (voir CODING_AGENT.md §6 Phase 4) | ⬜ | |
| A4-1 à A4-12 | (voir CODING_AGENT.md §6 Phase 4) | ⬜ | |

---

## Phase 5 — Intégrations
*(À démarrer après Phase 3 complète)*

| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| B5-1 à B5-10 | (voir CODING_AGENT.md §6 Phase 5) | ⬜ | |
| A5-1 à A5-9 | (voir CODING_AGENT.md §6 Phase 5) | ⬜ | |

---

## Phase 6 — Polish & Launch
*(À démarrer après Phases 4+5 complètes)*

| ID | Tâche | Statut | Notes |
|----|-------|--------|-------|
| P6-1 à P6-13 | (voir CODING_AGENT.md §6 Phase 6) | ⬜ | |

---

## Bugs & blocages actifs

| # | Description | Phase | Priorité | Statut |
|---|-------------|-------|----------|--------|
| — | — | — | — | — |

---

## Décisions prises en cours de dev

*(L'agent documente ici les décisions techniques prises qui ne figurent pas dans les specs)*

| Date | Décision | Raison |
|------|----------|--------|
| — | — | — |
