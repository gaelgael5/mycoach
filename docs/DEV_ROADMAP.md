# MyCoach — Organigramme de développement

> Roadmap technique en 7 phases. Chaque phase est livrable et testable de façon indépendante.

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
        B2[Modèle de données complet]
        B3[Auth JWT - email + Google OAuth]
        B4[API REST de base - CRUD utilisateurs]
        B5[Docker Compose dev]
        B1 --> B2 --> B3 --> B4
        B1 --> B5
    end

    subgraph ANDROID["📱 Android"]
        A1[Monorepo Kotlin - navigation setup]
        A2[Design System - couleurs Coach/Client]
        A3[ApiClient Retrofit singleton]
        A4[Screens Auth - Login / Register / Rôle]
        A1 --> A2 --> A4
        A1 --> A3 --> A4
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
    C5[Gestion paiements\nforfaits, facturation, historique]
    C6[Gestion heures\ncompteur, alertes renouvellement]
    C7[Performances personnelles\ncoach trackant ses propres entraînements]

    C1 --> C3
    C2 --> C3
    C3 --> C4
    C3 --> C5
    C5 --> C6
    C1 --> C7
```

**Livrables :** Un coach peut créer son profil complet, gérer ses clients et ses paiements.

---

## Phase 2 — Espace Client *(Sem. 6–8)*

```mermaid
flowchart TD
    CL1[Profil client\nquestionnaire onboarding]
    CL2[Sélection salles]
    CL3[Recherche coachs\nfiltres, profils]
    CL4[Tunnel découverte\ndemande → créneaux → confirmation]
    CL5[Agenda client\nvue séances, validation]
    CL6[Notifications\nrappels, demandes, annulations]

    CL1 --> CL3
    CL2 --> CL3
    CL3 --> CL4
    CL4 --> CL5
    CL5 --> CL6
```

**Livrables :** Un client peut s'inscrire, trouver un coach, planifier une séance découverte.

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
| **0 — Fondations** | Backend, auth, Android base, CI/CD | 2 sem | — |
| **1 — Coach** | Profil, clients, paiements, agenda, perfs perso | 3 sem | Phase 0 |
| **2 — Client** | Profil, recherche coach, découverte, agenda | 3 sem | Phase 0 |
| **3 — Performances** | QR code, tracking, graphiques, back-office | 3 sem | Phases 1+2 |
| **4 — IA** | Suggestions, programmes, vidéos générées | 3 sem | Phase 3 |
| **5 — Intégrations** | Strava, balance, Calendar, Stripe | 3 sem | Phase 3 |
| **6 — Launch** | Design final, tests, sécurité, Play Store | 3 sem | Phases 4+5 |

**Durée totale estimée : ~20 semaines** *(5 mois, équipe 1–2 devs)*

---

## 🔑 Décisions techniques clés

| Décision | Choix | Raison |
|----------|-------|--------|
| Backend | FastAPI + PostgreSQL | Rapidité dev, scalable |
| Mobile | Android Kotlin d'abord | Marché FR + coût |
| Auth | JWT + Google OAuth2 | UX fluide |
| Vidéos | Génération IA (Kling/Runway) + CDN | Pas de coût production |
| Balance | API Withings en priorité | Meilleure API FR |
| DB dev | SQLite → PostgreSQL prod | Migration simple |
| Déploiement | Docker sur Proxmox LXC | Infrastructure existante |

---

*Version 1.0 — Rédigé le 25/02/2026*
