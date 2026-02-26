# MyCoach — Référentiel des Disciplines

> Ce document définit la liste officielle des types de cours/disciplines disponibles dans MyCoach.
> Il est la source de vérité pour le back-end (table `disciplines`) et l'Android (ressources i18n).

---

## Principes

- **Discipline** = type de cours qu'un coach peut proposer et qu'un client peut filtrer/réserver
- Chaque discipline a un **slug** unique, immuable, utilisé comme clé i18n et en base de données
- Chaque discipline appartient à une **catégorie** (pour le filtrage et l'affichage groupé)
- La discipline est attachée à la **session** (pas au profil coach) — un coach peut proposer plusieurs disciplines
- Le coach définit un **nombre maximum de participants** par session (1 = individuel)
- Les spécialités du profil coach restent libres (chips texte) ; les disciplines de session sont issues de cette liste fermée

---

## Capacité par défaut

| Format | Capacité typique | Exemples |
|--------|-----------------|---------|
| Individuel | 1 | Personal training, coaching perso, bilan |
| Duo | 2 | Binôme, duo, couple |
| Petit groupe | 3–8 | Semi-collectif, boot camp restreint |
| Groupe | 9–20 | Cours collectifs, yoga studio |
| Grand groupe | 21–50 | Cours en salle de sport, outdoor event |
| Illimité | > 50 | Événements, stages, webinaires fitness |

> Le coach fixe librement la capacité de chaque session (min 1, max 999, défaut selon la discipline).
> Un seuil de **tarif groupe** peut être activé à partir de N participants (§10.4 des specs).

---

## Catégories & Disciplines

### 🏋️ FITNESS & MUSCULATION

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `personal_training` | Personal Training | Personal Training | 1 | Coaching individuel polyvalent |
| `strength_training` | Musculation | Strength Training | 1–4 | Poids libres, machines |
| `powerlifting` | Powerlifting | Powerlifting | 1–4 | Squat, bench, deadlift compétition |
| `weightlifting` | Haltérophilie | Olympic Weightlifting | 1–4 | Arraché, épaulé-jeté |
| `bodybuilding` | Bodybuilding | Bodybuilding | 1–4 | Hypertrophie, pose |
| `crossfit` | CrossFit | CrossFit | 4–15 | WOD, AMRAP, EMOM |
| `functional_training` | Functional Training | Functional Training | 1–10 | Mouvement fonctionnel |
| `hiit` | HIIT | HIIT | 4–20 | Haute intensité intervalles |
| `circuit_training` | Circuit Training | Circuit Training | 4–20 | Rotation de postes |
| `tabata` | Tabata | Tabata | 4–20 | 20s effort / 10s repos |
| `kettlebell` | Kettlebell | Kettlebell | 1–12 | |
| `trx` | TRX / Suspension | TRX / Suspension | 1–12 | |
| `calisthenics` | Callisthénie | Calisthenics | 1–8 | Poids du corps, street workout |
| `core_training` | Gainage & Core | Core Training | 4–20 | Abdos, stabilité |
| `stretching` | Stretching | Stretching | 1–20 | Souplesse passive |
| `mobility` | Mobilité | Mobility | 1–20 | Amplitude articulaire active |

---

### 🧘 MIND & BODY

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `yoga_hatha` | Yoga Hatha | Hatha Yoga | 4–20 | Postures statiques, respiration |
| `yoga_vinyasa` | Yoga Vinyasa | Vinyasa Yoga | 4–20 | Enchaînements fluides |
| `yoga_ashtanga` | Yoga Ashtanga | Ashtanga Yoga | 4–15 | Série fixe, discipline |
| `yoga_yin` | Yoga Yin | Yin Yoga | 4–20 | Postures longues, fascias |
| `yoga_hot` | Yoga Chaud | Hot Yoga / Bikram | 4–20 | 40°C, 90 min |
| `yoga_power` | Power Yoga | Power Yoga | 4–20 | Cardio + yoga |
| `yoga_nidra` | Yoga Nidra | Yoga Nidra | 4–30 | Relaxation profonde |
| `pilates_mat` | Pilates Sol | Mat Pilates | 4–12 | Tapis, gainage profond |
| `pilates_reformer` | Pilates Reformer | Reformer Pilates | 1–4 | Machine Reformer |
| `meditation` | Méditation | Meditation | 1–30 | Pleine conscience, guidée |
| `breathwork` | Respiration / Pranayama | Breathwork | 1–20 | Wim Hof, cohérence cardiaque |
| `tai_chi` | Tai Chi | Tai Chi | 4–30 | |
| `qi_gong` | Qi Gong | Qi Gong | 4–30 | |
| `sophrology` | Sophrologie | Sophrology | 1–20 | |
| `body_balance` | Body Balance | Body Balance | 4–30 | Yoga + Tai Chi + Pilates |

---

### 🏃 CARDIO & ENDURANCE

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `running_coaching` | Coaching Running | Running Coaching | 1–8 | Foulée, allure, plan |
| `trail_running` | Trail Running | Trail Running | 1–10 | Montagne, nature |
| `cycling_indoor` | Vélo Indoor / Spinning | Indoor Cycling | 4–30 | Spinning, RPM |
| `cycling_outdoor` | Cyclisme Outdoor | Outdoor Cycling | 1–15 | Route, VTT |
| `nordic_walking` | Marche Nordique | Nordic Walking | 4–20 | Bâtons |
| `cardio_fitness` | Cardio Fitness | Cardio Fitness | 4–30 | Machines cardio |
| `step_aerobics` | Step Aérobic | Step Aerobics | 4–30 | |
| `zumba` | Zumba | Zumba | 4–50 | |
| `dance_fitness` | Dance Fitness | Dance Fitness | 4–50 | |
| `jump_rope` | Corde à Sauter | Jump Rope | 1–15 | Double Dutch, fitness |

---

### 💃 DANSE

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `dance_latin` | Danse Latine | Latin Dance | 2–20 | Salsa, bachata, kizomba |
| `dance_hip_hop` | Hip-Hop | Hip-Hop Dance | 4–20 | |
| `dance_contemporary` | Danse Contemporaine | Contemporary Dance | 4–15 | |
| `dance_classical` | Danse Classique | Classical Ballet | 4–15 | |
| `dance_jazz` | Jazz | Jazz Dance | 4–20 | |
| `pole_dance` | Pole Dance | Pole Dance | 1–8 | |
| `aerial_arts` | Arts Aériens | Aerial Arts | 1–8 | Tissu aérien, cerceau |

---

### 🥊 SPORTS DE COMBAT

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `boxing` | Boxe Anglaise | Boxing | 1–10 | |
| `muay_thai` | Boxe Thaïlandaise | Muay Thai | 1–10 | |
| `kickboxing` | Kickboxing | Kickboxing | 1–10 | |
| `mma` | MMA | Mixed Martial Arts | 1–8 | |
| `judo` | Judo | Judo | 1–20 | |
| `bjj` | Jiu-Jitsu Brésilien | Brazilian Jiu-Jitsu | 1–15 | |
| `karate` | Karaté | Karate | 4–30 | |
| `taekwondo` | Taekwondo | Taekwondo | 4–30 | |
| `wrestling` | Lutte | Wrestling | 1–15 | |
| `krav_maga` | Krav Maga | Krav Maga | 4–20 | Défense personnelle |
| `savate` | Savate | French Boxing | 1–10 | Boxe française |
| `capoeira` | Capoeira | Capoeira | 4–20 | |

---

### 🏊 SPORTS AQUATIQUES

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `swimming_coaching` | Coaching Natation | Swimming Coaching | 1–4 | Nage, technique |
| `aqua_aerobics` | Aquagym | Aqua Aerobics | 4–30 | |
| `aqua_cycling` | Aquabiking | Aqua Cycling | 4–15 | |
| `open_water` | Eau Libre | Open Water Swimming | 1–10 | Lac, mer |
| `surfing` | Surf | Surfing | 1–8 | |
| `paddle` | Paddle / SUP | Stand-Up Paddle | 1–10 | |

---

### 🏇 SPORTS & ACTIVITÉS OUTDOOR

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `climbing` | Escalade | Climbing | 1–8 | Bloc, SAE, voie |
| `golf` | Golf | Golf | 1–4 | |
| `tennis` | Tennis | Tennis | 1–4 | |
| `padel` | Padel | Padel | 2–4 | |
| `squash` | Squash | Squash | 1–2 | |
| `skiing` | Ski & Snowboard | Skiing & Snowboard | 1–8 | |
| `horse_riding` | Équitation | Horse Riding | 1–6 | |
| `triathlon` | Triathlon | Triathlon | 1–8 | Nage + vélo + course |
| `gymnastics` | Gymnastique | Gymnastics | 1–15 | |
| `parkour` | Parkour | Parkour | 1–10 | |
| `skateboarding` | Skateboard | Skateboarding | 1–8 | |

---

### 🏥 SANTÉ & RÉÉDUCATION

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `physical_therapy` | Prépa Physique | Physical Preparation | 1–4 | |
| `rehabilitation` | Rééducation Sportive | Sports Rehabilitation | 1 | Post-blessure |
| `posturology` | Posturologie | Posturology | 1 | |
| `prenatal_fitness` | Fitness Prénatal | Prenatal Fitness | 1–8 | Femmes enceintes |
| `postnatal_fitness` | Fitness Postnatal | Postnatal Fitness | 1–8 | |
| `senior_fitness` | Fitness Senior | Senior Fitness | 1–15 | Adaptée 60+ |
| `adapted_sport` | Sport Adapté | Adapted Sport | 1–8 | Handicap, pathologies |
| `nutrition_coaching` | Coaching Nutritionnel | Nutrition Coaching | 1 | Accompagnement diététique |

---

### 🌟 FORMATS SPÉCIAUX

| Slug | Nom FR | Nom EN | Capacité défaut | Notes |
|------|--------|--------|----------------|-------|
| `bootcamp` | Bootcamp | Bootcamp | 8–30 | Intensif multi-exercices |
| `online_coaching` | Coaching en Ligne | Online Coaching | 1 | Visio, distanciel |
| `workshop` | Atelier / Stage | Workshop | 4–50 | Événement ponctuel |
| `discovery` | Séance Découverte | Discovery Session | 1 | Premier contact |
| `bilan` | Bilan Forme | Fitness Assessment | 1 | Évaluation initiale |
| `outdoor_training` | Training Outdoor | Outdoor Training | 1–20 | Parc, plage, nature |

---

## Règles de gestion

### Configuration par le coach (Profil → Mes disciplines)

1. Le coach **sélectionne les disciplines** qu'il propose (multi-select depuis cette liste)
2. Pour chaque discipline sélectionnée, il définit :
   - **Capacité min** : toujours 1
   - **Capacité max par défaut** : pré-rempli selon le tableau ci-dessus, modifiable (1–999)
   - **Tarif par défaut** pour cette discipline (modifiable à chaque création de session)
3. La discipline est ensuite **disponible à la création de session** dans l'agenda

### Création de session (Agenda → Créer une séance)

```
Type de cours     : [Dropdown — disciplines du coach]
Capacité max      : [Stepper — pré-rempli, modifiable]
Tarif             : [montant unitaire — pré-rempli, modifiable]
Tarif groupe      : [optionnel — seuil + tarif réduit si N participants]
```

### Forfait avec discipline

Un forfait peut être **limité à une ou plusieurs disciplines** :
- "10 séances de Yoga Vinyasa" ≠ "10 séances de Musculation"
- Le coach peut créer un forfait `discipline_ids = null` (toutes disciplines) ou restreint

### Affichage client

- Fiche coach → les disciplines apparaissent comme **chips cliquables** (icône + nom)
- Filtres recherche → les clients filtrent par discipline
- Calendrier → chaque session affiche l'icône de sa discipline dans le bloc

---

## Données en base

```sql
-- Table disciplines (référentiel — seed au démarrage)
CREATE TABLE disciplines (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug        VARCHAR(50) UNIQUE NOT NULL,       -- ex: "yoga_vinyasa"
    category    VARCHAR(50) NOT NULL,              -- ex: "MIND_BODY"
    name_key    VARCHAR(100) NOT NULL,             -- clé i18n ex: "discipline.yoga_vinyasa"
    default_capacity_min  SMALLINT DEFAULT 1,
    default_capacity_max  SMALLINT DEFAULT 1,
    is_active   BOOLEAN DEFAULT TRUE,
    sort_order  SMALLINT DEFAULT 0
);

-- Disciplines proposées par un coach
CREATE TABLE coach_disciplines (
    coach_id            UUID REFERENCES coach_profiles(id) ON DELETE CASCADE,
    discipline_id       UUID REFERENCES disciplines(id),
    capacity_max        SMALLINT NOT NULL DEFAULT 1,
    price_cents         INTEGER,                    -- tarif défaut pour cette discipline
    currency            CHAR(3) DEFAULT 'EUR',
    PRIMARY KEY (coach_id, discipline_id)
);

-- Discipline d'une session (peut différer du défaut du coach)
ALTER TABLE sessions ADD COLUMN discipline_id UUID REFERENCES disciplines(id);
ALTER TABLE sessions ADD COLUMN capacity_max SMALLINT NOT NULL DEFAULT 1;

-- Disciplines couvertes par un forfait (NULL = toutes)
CREATE TABLE package_disciplines (
    package_id      UUID REFERENCES packages(id) ON DELETE CASCADE,
    discipline_id   UUID REFERENCES disciplines(id),
    PRIMARY KEY (package_id, discipline_id)
);
```
