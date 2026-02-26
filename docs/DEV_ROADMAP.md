# MyCoach — Organigramme de développement

> Roadmap technique en 7 phases. Chaque phase est livrable et testable de façon indépendante.

---

## ✅ Définition du Done — Rappel (règle absolue)

> **Une tâche n'est terminée que si elle est committée avec ses tests.**

Pour chaque feature implémentée, le commit Git doit contenir :

| Quoi | Critère |
|------|---------|
| **Code** | Feature complète selon les specs |
| **Tests passants** | Au moins 1 test couvrant le cas nominal (happy path) |
| **Tests non passants** | Au moins 1 test par règle métier (erreur, limite, accès refusé) |
| **Tous les tests verts** | `pytest` ou `./gradlew test` → 0 failure, 0 error |
| **PROGRESS.md** | Tâche marquée ✅ |

> Format du message de commit : `[PHASE-X][TASK-Y] Description + tests`
>
> ⛔ **Commit interdit** si un test est rouge ou si les tests manquent.
> Voir `docs/CODING_AGENT.md §10` pour les exemples complets (DoD + paires passant/non passant).

---

## Vue d'ensemble

```mermaid
flowchart TD
    P0["🏗️ PHASE 0\nFondations\n(Semaines 1–2)"]
    P1["🧑‍🏫 PHASE 1\nEspace Coach\n(Semaines 3–5)"]
    P2["👤 PHASE 2\nEspace Client\n(Semaines 6–8)"]
    P3["💪 PHASE 3\nPerformances\n(Semaines 9–11)"]
    P4["🤖 PHASE 4\nIntelligence IA\n(Semaines 12–14)"]
    P5["🔌 PHASE 5\nIntégrations\n(Semaines 15–17)"]
    P6["✨ PHASE 6\nPolish & Launch\n(Semaines 18–20)"]

    P0 --> P1
    P0 --> P2
    P1 --> P3
    P2 --> P3
    P3 --> P4
    P3 --> P5
    P4 --> P6
    P5 --> P6
```

---

## Phase 0 — Fondations *(Sem. 1–2)*

```mermaid
flowchart TD
    subgraph BACK["🖥️ Backend"]
        B1[FastAPI + PostgreSQL setup]
        B2[Modèle de données complet\npays ISO 3166 + locale BCP 47\ndevise ISO 4217 + timezone]
        B3[Auth API Key - Google OAuth + email/password]
        B4[API REST de base - CRUD utilisateurs]
        B5[Docker Compose dev]
        B6[i18n backend\nfichiers locales JSON par langue\nmessages erreur + notifications traduits]
        B1 --> B2 --> B3 --> B4
        B1 --> B5
        B2 --> B6
    end

    subgraph ANDROID["📱 Android"]
        A1[Monorepo Kotlin - navigation setup]
        A2[Design System - couleurs Coach/Client]
        A3[ApiClient Retrofit - X-API-Key interceptor]
        A4[Screens Auth - Login / Register / Rôle + Pays + Locale]
        A5[i18n Android\nstrings.xml par locale\nformat dates devises poids]
        A1 --> A2 --> A4
        A1 --> A3 --> A4
        A1 --> A5
    end

    subgraph INFRA["⚙️ Infra"]
        I1[GitHub repo + CI GitHub Actions]
        I2[Déploiement Proxmox LXC]
        I3[Back-office admin - base]
        I1 --> I2
    end
```

**Livrables :** App installable, login fonctionnel, deux rôles distincts (coach/client), backend déployé.

---

## Phase 1 — Espace Coach *(Sem. 3–5)*

```mermaid
flowchart TD
    C1[Profil coach\nbio, spécialités, certifications]
    C2[Sélection salles\nchaînes + clubs]
    C3[Gestion clients\nliste, fiches, notes]
    C4[Agenda coach\nvue globale séances]
    C5[Tarification\nséance unitaire + forfaits N séances]
    C6[Gestion paiements\nforfaits, facturation, historique]
    C7[Gestion heures\ncompteur, alertes renouvellement]
    C8[Politique d'annulation\ndélai, pénalité, no-show]
    C9[Performances personnelles\ncoach trackant ses propres entraînements]
    C10[Disponibilités\ncréneaux récurrents, nb places, horizon résa]

    C1 --> C3
    C2 --> C3
    C3 --> C4
    C5 --> C6
    C6 --> C7
    C8 --> C4
    C10 --> C4
    C1 --> C9
```

**Livrables :** Un coach peut créer son profil complet, configurer ses tarifs (unitaire + forfaits), ses disponibilités, sa politique d'annulation, et gérer ses clients et paiements.

---

## Phase 2 — Espace Client *(Sem. 6–8)*

```mermaid
flowchart TD
    CL1[Profil client\nquestionnaire onboarding]
    CL2[Sélection salles]
    CL3[Recherche coachs\nfiltres, profils]
    CL4[Tunnel découverte\ndemande → créneaux → confirmation]
    CL5[Réservation créneaux\ncalendrier dispo coach]
    CL6[Choix tarif à la réservation\nunitaire ou sélection forfait]
    CL7[Validation séance par le coach]
    CL8[Annulation\n> 24h libre / < 24h séance due]
    CL9[Liste d'attente\nnotif 30 min si place libérée]
    CL10[Agenda client\nvue séances multi-coach]
    CL11[Notifications\nrappels, confirmations, annulations]

    CL1 --> CL3
    CL2 --> CL3
    CL3 --> CL4
    CL4 --> CL5
    CL5 --> CL6
    CL6 --> CL7
    CL5 --> CL9
    CL7 --> CL10
    CL8 --> CL11
    CL10 --> CL11
```

**Livrables :** Un client peut s'inscrire, trouver un coach, réserver un créneau, choisir son tarif (unitaire ou forfait), gérer ses annulations avec les règles de pénalité, et rejoindre une liste d'attente.

---

## Phase 3 — Performances *(Sem. 9–11)*

```mermaid
flowchart TD
    subgraph SCAN["📷 Scanner"]
        S1[QR Code scanner\nidentification machine]
        S2[Fallback manuel\ntype + marque + photo]
        S1 --> S3
        S2 --> S3
        S3[Fiche machine\npré-remplie]
    end

    subgraph PERF["💪 Tracking"]
        P1[Saisie performance\nsets, reps, poids]
        P2[Saisie par le coach\npour un client]
        P3[Historique & graphiques]
        P4[Partage coach ↔ client]
        P1 --> P3
        P2 --> P3
        P3 --> P4
    end

    subgraph BACKOFFICE["⚙️ Back-office machines"]
        BO1[Modération machines soumises]
        BO2[Validation photo + infos]
        BO3[Génération QR code]
        BO1 --> BO2 --> BO3
    end

    S3 --> P1
    S2 --> BO1
```

**Livrables :** Tracking complet des performances, scanner QR, graphiques de progression.

---

## Phase 4 — Intelligence IA *(Sem. 12–14)*

```mermaid
flowchart TD
    AI1[Moteur de suggestions\nbasé questionnaire + historique]
    AI2[Programme hebdo\ngénéré automatiquement]
    AI3[Ajustement progressif\ncharges auto-incrémentées]
    AI4[Mode guidé\nécran par écran + minuterie repos]
    AI5[Coach push programmes\nstructure + assignment]
    AI6[Génération vidéos IA\npar exercice - validation back-office]
    AI7[Player vidéo intégré\ndans séances guidées]

    AI1 --> AI2 --> AI3 --> AI4
    AI5 --> AI4
    AI6 --> AI7
    AI7 --> AI4
```

**Livrables :** Séances solo intelligentes, programmes coach, vidéos pédagogiques IA sur chaque exercice.

---

## Phase 5 — Intégrations *(Sem. 15–17)*

```mermaid
flowchart TD
    INT1[Strava OAuth2\npush séances]
    INT2[Google Calendar\nsync agenda]
    INT3[Balance Withings\nimport poids + composition]
    INT4[Balance Xiaomi / Garmin\nalternatives]
    INT5[Firebase\npush notifications]
    INT6[Stripe\npaiements en ligne]

    INT3 --> SCALE[Tableau de bord\ncomposition corporelle]
    INT4 --> SCALE
    INT1 --> DASH[Dashboard client\nvu d'ensemble]
    INT2 --> DASH
    SCALE --> DASH
```

**Livrables :** App connectée à l'écosystème fitness (Strava, balances, calendrier, paiements).

---

## Phase 6 — Polish & Launch *(Sem. 18–20)*

```mermaid
flowchart TD
    POL1[Design final\nanimations Lottie, glassmorphism]
    POL2[Tests E2E\nAndroid instrumented tests]
    POL3[Performance\noptimisation API, cache]
    POL4[Sécurité\naudit, RGPD, CGU]
    POL5[Back-office complet\nstats, modération, coachs vérifiés]
    POL6[Beta test\n10 coachs + 50 clients]
    POL7[🚀 Publication\nGoogle Play Store]

    POL1 --> POL6
    POL2 --> POL6
    POL3 --> POL6
    POL4 --> POL6
    POL5 --> POL6
    POL6 --> POL7
```

---

## 📊 Résumé des phases

| Phase | Contenu | Durée | Dépendances |
|-------|---------|-------|-------------|
| **0 — Fondations** | Backend FastAPI + PostgreSQL, auth API Key, Android base, CI/CD | 2 sem | — |
| **1 — Coach** | Profil, tarification (unitaire + forfaits), disponibilités, politique annulation, clients, paiements, agenda | 3 sem | Phase 0 |
| **2 — Client** | Profil, recherche coach, réservation, choix tarif, validation coach, annulation (pénalité < 24h), liste d'attente | 3 sem | Phase 0 |
| **3 — Performances** | QR code, tracking, graphiques, back-office | 3 sem | Phases 1+2 |
| **4 — IA** | Suggestions, programmes, vidéos générées | 3 sem | Phase 3 |
| **5 — Intégrations** | Strava, balance, Calendar, Stripe | 3 sem | Phase 3 |
| **6 — Launch** | Design final, tests, sécurité, Play Store | 3 sem | Phases 4+5 |

**Durée totale estimée : ~20 semaines** *(5 mois, équipe 1–2 devs)*

---

## 🔑 Décisions techniques clés

| Décision | Choix | Raison |
|----------|-------|--------|
| Backend | FastAPI (Python) | Rapidité dev, async natif |
| SGBD | **PostgreSQL 16** | Multi-users, MVCC, JSONB, scalable |
| ORM | SQLAlchemy 2 (async) + Alembic | Standard Python, migrations propres |
| Mobile | Android Kotlin d'abord | Marché FR + coût iOS différé |
| **Auth** | **API Key (SHA-256)** | Simple, stateful, révocable, sans dépendance |
| Auth Google | Google ID Token → échange → API Key maison | 1 vérification Google puis lookup local |
| Auth email/password | bcrypt hash → SHA-256(email+hash+salt) → API Key | Même système unifié |
| API Key header | `X-API-Key: <64 chars hex>` | Standard REST, Retrofit-friendly |
| Stockage clé Android | EncryptedSharedPreferences (AES-256) | Sécurisé, natif Android |
| Révocation | `revoked = TRUE` en base | Multi-device, logout immédiat |
| Tarification coach | Séance unitaire + N forfaits configurables | Flexibilité maximale |
| **i18n** | **BCP 47 locale par utilisateur** | Zéro texte codé en dur dès le 1er commit |
| Pays | ISO 3166-1 alpha-2 | Sur clubs, profils coach et client |
| Devises | ISO 4217 stockées en centimes | Jamais de float pour les montants |
| Dates/heures | UTC en base, converti selon timezone user | Android : `DateTimeFormatter` + `ZoneId` |
| Poids | Stocké en kg, affiché kg ou lb | Conversion automatique selon préférence |
| Vidéos | Génération IA (Kling/Runway) + CDN | Pas de coût production |
| Balance | API Withings en priorité | Meilleure API FR |
| Déploiement | Docker Compose sur Proxmox LXC | Infrastructure existante |

---

## 📦 Stack technique résumée

```
Backend
  ├── FastAPI (Python 3.12)
  ├── PostgreSQL 16 (Docker)
  ├── SQLAlchemy 2 async + asyncpg
  ├── Alembic (migrations)
  ├── bcrypt (hash passwords)
  └── hashlib SHA-256 (API keys, stdlib — aucune dépendance)

Android
  ├── Kotlin + Coroutines
  ├── Retrofit 2 (HTTP, intercepteur X-API-Key)
  ├── Room (cache local optionnel)
  ├── Navigation Component
  ├── EncryptedSharedPreferences (stockage clé)
  ├── Lottie (animations)
  └── i18n : strings.xml par locale + java.time (dates UTC → local)

Infra
  ├── Docker Compose (backend + PostgreSQL + pgAdmin)
  ├── Proxmox LXC (hébergement)
  ├── GitHub Actions (CI)
  └── Firebase (push notifications)
```

---

*Version 1.2 — Mis à jour le 25/02/2026 (PostgreSQL + API Key auth + tarification coach + i18n first : locale BCP 47, pays ISO 3166-1, devise ISO 4217, timezone, unité poids)*
