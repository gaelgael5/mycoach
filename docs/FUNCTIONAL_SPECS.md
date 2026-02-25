# MyCoach — Cahier des charges fonctionnel v1.0

> Application mobile de coaching sportif personnalisé.  
> Deux espaces distincts : **Coach** (interface sombre/tech) et **Client** (interface claire/dynamique).

---

## 🎯 Vision produit

MyCoach connecte des coachs sportifs indépendants avec leurs clients. L'application couvre l'ensemble du cycle de coaching : découverte, planification, entraînement, suivi des performances, paiement — avec une expérience mobile-first, haute technologie, et des fonctionnalités IA.

---

## 🎨 Design System

### Principes
- **High-tech** : UI sombre, effets glassmorphism, accents néon, typographie moderne (ex: Space Grotesk)
- **Deux identités visuelles distinctes** :

| | Espace Coach | Espace Client |
|--|--------------|---------------|
| Fond | `#0A0E1A` (noir profond) | `#F0F4FF` (blanc bleuté) |
| Accent | `#7B2FFF` (violet électrique) | `#00C2FF` (cyan dynamique) |
| Secondaire | `#FF6B2F` (orange énergie) | `#FF6B2F` (orange énergie) |
| Ambiance | Dashboard pro, analytics | App fitness moderne |

- Animations fluides (Lottie)
- Composants : cartes avec ombres longues, barres de progression animées, graphiques style "dark analytics"

---

## 🌍 Internationalisation (i18n)

L'application est **pensée internationale dès le premier commit**. Aucun texte codé en dur, aucune devise fixe, aucun format de date implicite.

### Principes
- Toutes les chaînes de l'UI sont externalisées dans des fichiers de ressources (Android : `strings.xml` par locale, Backend : fichiers i18n JSON)
- La langue de l'interface suit la **culture du profil utilisateur** (`fr-FR`, `en-US`, `es-ES`, `pt-BR`…)
- Les formats de date, heure, devise et unités (kg/lb) s'adaptent automatiquement à la locale
- Le backend retourne les messages d'erreur et notifications dans la langue de l'utilisateur

### Culture par défaut
- Détectée à l'installation (locale système de l'appareil)
- Modifiable dans le profil utilisateur à tout moment
- Stockée côté serveur (persistée sur tous les appareils)

### Locales supportées (Phase 1)
| Code | Langue | Devise | Unité poids |
|------|--------|--------|-------------|
| `fr-FR` | Français (France) | EUR € | kg |
| `fr-BE` | Français (Belgique) | EUR € | kg |
| `fr-CH` | Français (Suisse) | CHF | kg |
| `en-US` | English (US) | USD $ | lb |
| `en-GB` | English (UK) | GBP £ | kg |
| `es-ES` | Español (España) | EUR € | kg |
| `pt-BR` | Português (Brasil) | BRL R$ | kg |
| `de-DE` | Deutsch | EUR € | kg |

> D'autres locales ajoutables sans refactoring grâce à l'architecture i18n first.

---

## 🏋️ Salles de sport intégrées

Sélection à l'inscription (coach ET client). Multi-sélection possible. Filtrable par **pays**.

| Chaîne | Pays | Clubs |
|--------|------|-------|
| Fitness Park | 🇫🇷 France, 🇬🇵 Guadeloupe, 🇲🇶 Martinique | ~400 |
| Basic-Fit | 🇫🇷 🇧🇪 🇳🇱 🇱🇺 🇩🇪 🇪🇸 🇲🇦 | ~1 200 |
| L'Orange Bleue | 🇫🇷 France | ~470 |
| Keep Cool | 🇫🇷 France | ~250 |
| Elancia | 🇫🇷 France | ~100 |
| Neoness | 🇫🇷 France | ~50 |
| GoFit | 🇫🇷 France | ~30 |
| CMG Sports Club | 🇫🇷 France (IDF) | ~20 |
| Wellness Sport Club | 🇫🇷 France | ~40 |
| Moving | 🇫🇷 France | ~30 |
| Anytime Fitness | 🌍 International (50+ pays) | ~5 000 |
| PureGym | 🇬🇧 🇩🇰 🇸🇦 | ~600 |
| McFit | 🇩🇪 🇦🇹 🇵🇱 🇮🇹 🇪🇸 | ~350 |
| Holmes Place | 🇩🇪 🇦🇹 🇨🇿 🇵🇱 🇮🇱 🇨🇭 | ~100 |
| Virgin Active | 🇬🇧 🇮🇹 🇵🇹 🇿🇦 🇦🇺 | ~200 |

> Répertoire enrichi en back-office. Chaque club : nom, adresse, CP, ville, **pays (ISO 3166-1 alpha-2)**, coordonnées GPS.

---

## 👤 ESPACE CLIENT

### 1. Inscription & profil
- Nom, prénom, photo de profil
- Date de naissance, poids, taille
- Objectifs (perte de poids / prise de masse / endurance / remise en forme / autre)
- Sélection des salles fréquentées
- Connexion Strava (OAuth2, optionnel)
- Connexion balance connectée (Withings / Xiaomi / Garmin Index)

### 2. Questionnaire d'onboarding
Complété à l'inscription, reconfigurable à tout moment :
- Niveau sportif (débutant / intermédiaire / confirmé)
- Fréquence souhaitée (x séances / semaine)
- Équipements disponibles (salle complète / home gym / cardio uniquement)
- Zones à travailler prioritairement
- Blessures / contre-indications
- Préférence de durée de séance (30 / 45 / 60 / 90 min)

### 3. Recherche & sélection d'un coach
- Filtre par : salle, spécialité, disponibilité, tarif
- Profil coach : photo, bio, certifications, avis clients, tarifs
- **Demande de première rencontre** ("séance découverte")
- Plusieurs coachs actifs simultanément (ex: coach muscu + coach cardio)

### 4. Tunnel de première rencontre
1. Client envoie une demande de découverte
2. Coach reçoit notification → accepte + propose un créneau
3. Séance "Découverte" = type dédié dans le calendrier partagé
4. Après la rencontre : confirmation de la relation coach/client
5. Le client peut refuser sans conséquence et chercher un autre coach

### 5. Agenda partagé
- Vue calendrier des séances planifiées
- Proposition de créneau par le client ou le coach
- **Validation obligatoire par le coach** avant confirmation
- Types de séances : Découverte / Encadrée / Solo guidée
- Notifications : rappel (J-1, H-1), annulation, demande de validation
- Synchronisation Google Calendar (optionnel)

### 6. Séances SOLO intelligentes
- Génération automatique d'un programme hebdomadaire basé sur le questionnaire
- Chaque séance = liste d'exercices avec sets / reps / poids suggérés
- Ajustement progressif automatique (charges augmentent si perfs validées)
- Mode guidé : écran par écran, minuterie de repos intégrée
- Possibilité d'ignorer / modifier un exercice
- **Coach peut pousser son propre programme** qui remplace ou complète les suggestions IA

### 7. Suivi des performances

#### Entrée des données
- **Manuelle** : après une séance solo
- **Par le coach** : pendant ou après une séance encadrée
- **Depuis un programme** : pré-rempli, juste valider / ajuster

#### Structure d'une entrée
```
- Date & heure
- Type de séance (solo / encadrée / programme)
- Exercice (depuis machine ou liste)
- Catégorie (Musculation / Cardio / Stretching / Mobilité)
- Groupes musculaires ciblés
- Séries × répétitions × poids (kg)
- Notes libres
```

#### Visualisation
- Historique chronologique filtrable
- Graphiques de progression par exercice (courbe poids max, volume total)
- Tableau de bord hebdomadaire (séances réalisées vs prévues)

#### Partage avec le coach
- Automatique si option activée, ou manuel par séance

### 8. Scanner QR Code machine
- Scan du QR code affiché sur la machine en salle
- Identification automatique : marque, modèle, exercices associés
- Pré-remplit la fiche de performance

**Fallback si scan échoue :**
1. Sélection dans une liste de types de machines (Presse cuisses, Tirage vertical, Développé couché, Vélo, Tapis, Elliptique…)
2. Sélection de la marque (Technogym, Life Fitness, Hammer Strength, Precor, Matrix, Panatta…)
3. Saisie du modèle (texte libre)
4. **Photo de la machine** (envoyée pour validation back-office)

### 9. Vidéos pédagogiques

- Chaque exercice dispose d'une **courte vidéo 15–45s** générée par IA
- Contenu : positionnement, amplitude, points de vigilance, respiration
- Format silencieux avec légendes texte (contexte gym)
- Accessible via bouton 📹 sur chaque exercice pendant une séance
- Visible aussi dans la fiche exercice de l'historique
- Technologie : génération IA (modèle vidéo génératif) + validation back-office avant publication

### 10. Balance connectée
- Connexion via Bluetooth ou API cloud (Withings Health API, Xiaomi Mi Fit, Garmin Connect)
- Données importées : poids, IMC, masse grasse (%), masse musculaire (%)
- Historique et courbes de composition corporelle
- Partageable avec le coach
- Alertes si évolution significative

### 11. Intégration Strava
- Connexion OAuth2
- Push automatique ou manuel des séances vers Strava
- Type d'activité : `WeightTraining`, `Workout`, `Run`…
- Import optionnel depuis Strava (activités cardio extérieures)

---

## 🧑‍🏫 ESPACE COACH

### 1. Profil coach
- Photo, nom, prénom
- Biographie, spécialités, méthodes
- Certifications / diplômes (avec photo justificatif pour badge "vérifié")
- Salles de sport où il intervient (multi-chaînes)
- Tarifs (séance à l'unité, forfaits 5/10/20h)
- Disponibilités (créneaux récurrents ou ad hoc)

### 2. Gestion des clients
- Liste des clients actifs avec statut (actif / en pause / terminé)
- Fiche client détaillée : profil, historique séances, perfs, paiements
- Accès à toutes les performances du client (si partagées)
- Notes privées sur le client (non visibles par le client)

### 3. Demandes entrantes
- Notifications des demandes de découverte
- Accepter / refuser / proposer créneau
- Vue pipeline : En attente → Découverte planifiée → Actif

### 4. Agenda partagé
- Vue globale de toutes ses séances (tous clients)
- Validation des demandes de créneau
- Création de séances à l'initiative du coach
- Séances encadrées confirmées = heures décomptées du forfait client

### 5. Saisie des performances pour un client
- Pendant ou après une séance encadrée
- Interface identique à la saisie client
- Le coach choisit le client concerné → saisit exercice par exercice
- Confirmation envoyée au client pour validation (optionnel)

### 6. Programmes d'entraînement solo
- Création d'un programme structuré :
  - Nom, description, durée (en semaines)
  - Jours cibles (Lundi : Push / Mercredi : Pull / Vendredi : Legs…)
  - Pour chaque séance : exercices + sets/reps/poids cibles
- Assignment à un ou plusieurs clients
- Le client suit le programme en mode guidé
- Le coach visualise l'avancement et les perfs réelles vs cibles

### 7. Suivi des performances du COACH
- Le coach peut tracker ses propres entraînements
- Même interface que le client (scanner, saisie, historique, graphiques)
- Balance connectée également disponible pour le coach
- Espace personnel distinct de son espace professionnel

### 8. Gestion des paiements
- Définition des forfaits (5h, 10h, 20h) et tarifs
- Facturation automatique selon séances réalisées
- Historique des paiements par client
- Export CSV pour comptabilité
- Statuts : En attente / Payé / En retard
- Intégration Stripe (optionnel, phase 2)

### 9. Suivi des heures
- Compteur heures consommées / forfait par client
- Alerte quand il reste ≤ 2 séances sur un forfait (pour proposer renouvellement)
- Historique des séances décomptées

---

## ⚙️ BACK-OFFICE (Administrateur)

- Gestion des chaînes et clubs (import CSV, mise à jour)
- Modération des fiches machines soumises par les utilisateurs :
  - Validation photo, type, marque, modèle
  - Génération ou association d'un QR code
- Gestion des vidéos pédagogiques :
  - Lancement génération IA par exercice
  - Validation avant publication
  - Remplacement manuel si qualité insuffisante
- Gestion des coachs (validation certifications, badge vérifié)
- Statistiques globales (utilisateurs, séances, revenus SaaS)

---

## 🔌 Intégrations techniques

| Service | Usage | Auth |
|---------|-------|------|
| Google OAuth2 | Authentification utilisateurs | ID Token → échange API Key |
| Google Calendar | Sync agenda | OAuth2 |
| Strava | Push/pull activités | OAuth2 |
| Withings | Balance connectée | OAuth2 |
| Xiaomi Mi Fit / Zepp | Balance connectée | API |
| Garmin Connect | Balance + activités | OAuth2 |
| Firebase | Push notifications | SDK |
| Stripe | Paiements en ligne | API key |
| IA vidéo (Kling / Runway) | Génération vidéos exercices | API key |

## 🔐 Stratégie d'authentification

Toutes les requêtes API sont authentifiées via une **API Key** (SHA-256, 64 chars hex) transmise dans le header `X-API-Key`.

**Flux Google OAuth :**
1. Client obtient un Google ID Token
2. Envoie à `POST /auth/google`
3. Backend vérifie le token (clés publiques Google)
4. Génère : `api_key = SHA256(google_sub + email + SECRET_SALT)`
5. Stocke en table `api_keys` (user_id, key_hash, device, timestamps)
6. Retourne la clé au client → stockée en `EncryptedSharedPreferences`

**Flux Email/Password :**
1. `POST /auth/login` avec email + password
2. Backend vérifie credentials (bcrypt)
3. Génère : `api_key = SHA256(email + bcrypt_hash_stocké + SECRET_SALT)`
4. Même stockage et retour

**Révocation :**
- `DELETE /auth/logout` → `revoked = TRUE` sur la clé courante
- `DELETE /auth/logout-all` → révoque toutes les clés de l'utilisateur (tous appareils)

---

## 📱 Plateformes cibles

- **Android** : Kotlin, Material Design 3, minSdk 26
- **iOS** : Swift / SwiftUI (phase 2)
- **Backend** : FastAPI (Python 3.12)
- **SGBD** : PostgreSQL 16 (Docker)
- **ORM** : SQLAlchemy 2 async + Alembic (migrations)
- **Déploiement** : Docker Compose sur Proxmox LXC

---

## 🗃️ Modèle de données (entités principales)

```
User (base commune coach/client)
  id, email, name, photo_url, role (coach|client)
  phone (E.164, ex: +33612345678, nullable)   ← numéro de téléphone
  locale (ex: fr-FR, en-US, es-ES)            ← culture de l'utilisateur
  timezone (ex: Europe/Paris)
  profile_completion_pct INT                  ← % de complétion du profil (0-100)
  created_at

CoachProfile
  user_id, bio, specialties[], certifications[], gyms[]
  hourly_rate, currency (ISO 4217 : EUR, USD, GBP…)
  verified, country (ISO 3166-1 alpha-2 : FR, BE, US…)
  session_duration_min, discovery_enabled, discovery_free, discovery_price_cents

CoachWorkSchedule (jours de travail & horaires)
  id, coach_id FK
  day_of_week (0=Lun, 1=Mar, …, 6=Dim)
  is_working_day (bool)                       ← false = jour de repos
  slots: [{ start_time, end_time }]           ← plusieurs créneaux par jour possibles

ClientProfile
  user_id, birth_date, weight_kg, height_cm, goal, level, injuries[]
  weight_unit (kg|lb)
  questionnaire_id, strava_token, scale_provider, scale_token
  country (ISO 3166-1 alpha-2)

Gym (par chaîne)
  id, chain_name, name, address, zip_code, city
  country (ISO 3166-1 alpha-2 : FR, BE, US, GB…)
  lat, lng

CoachingRelation
  id, coach_id, client_id
  status: pending|discovery|active|paused|ended
  discovery_slot, confirmed_at

Session
  id, coach_id, client_id (nullable si solo)
  type: discovery|coached|solo_guided|solo_free
  scheduled_at, duration_min, status: proposed|confirmed|done|cancelled
  validated_by_coach (bool), hours_deducted (bool)

PerformanceEntry
  id, user_id, session_id (nullable), entered_by (user_id)
  date, notes
  exercises: [ExerciseSet]

ExerciseSet
  id, entry_id, exercise_type_id, machine_id (nullable)
  sets, reps, weight_kg, order

ExerciseType
  id, name, category, target_muscles[], difficulty_level
  video_url, thumbnail_url, instructions[]

Machine
  id, type, brand, model, photo_url
  validated (bool), qr_code (nullable)
  submitted_by (user_id), validated_by (admin_id)

WorkoutPlan (programme)
  id, created_by (coach_id|AI), name, description, duration_weeks
  assigned_to (client_id nullable)

PlannedSession (dans un programme)
  id, plan_id, day_of_week, order
  exercises: [PlannedExercise]

PlannedExercise
  id, planned_session_id, exercise_type_id
  target_sets, target_reps, target_weight_kg

BodyMeasurement (balance)
  id, user_id, measured_at
  weight_kg, bmi, fat_pct, muscle_pct, source (withings|xiaomi|garmin|manual)

Payment
  id, client_id, coach_id
  amount, currency, status: pending|paid|late
  package_hours, hours_remaining, created_at, paid_at

ApiKey
  id, user_id
  key_hash (CHAR 64, SHA-256, indexé unique)
  device_name (optionnel)
  created_at, last_used_at
  expires_at (NULL = pas d'expiration)
  revoked (bool, défaut FALSE)

CoachPricing
  id, coach_id
  type: per_session|package
  name (ex: "Pack 10 séances")
  session_count (NULL si per_session)
  price_total (€)
  validity_months (NULL = sans limite)
  public (bool)

Booking
  id, client_id, coach_id, slot_datetime
  duration_min, status: pending_validation|confirmed|done
            |cancelled_by_client|cancelled_late_by_client
            |cancelled_by_coach|no_show|rejected
  pricing_type: per_session|package
  package_id (FK CoachPricing, nullable)
  client_message, coach_message
  late_cancel_waived (bool, défaut FALSE)
  created_at

Waitlist
  id, booking_slot_ref, client_id
  position, status: waiting|notified|confirmed|expired
  notified_at, expires_at
  created_at
```

---

*Version 1.3 — 25/02/2026 (+ téléphone E.164 coach+client, jours travail+horaires coach, wizard minimaliste + "Terminer plus tard", responsive, bandeau complétion)*
