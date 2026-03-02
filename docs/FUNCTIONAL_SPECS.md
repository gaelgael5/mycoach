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

# Spécifications Fonctionnelles
## Application de Coaching & Suivi de Performance

**Document de cadrage — Version consolidée V3**
**Mars 2026**

---

## Table des matières

1. [Espace Client](#1-espace-client)
2. [Espace Coach](#2-espace-coach)
3. [Récapitulatif des écrans](#3-récapitulatif-des-écrans)
4. [Notes techniques et points d'attention](#4-notes-techniques-et-points-dattention)

---

# 1. Espace Client

L'espace client constitue le cœur de l'application. Il permet à chaque utilisateur de gérer son profil, suivre ses performances, planifier ses séances et interagir avec les coachs et autres utilisateurs.

## 1.1 Connexion

| Champ | Type | Détails |
|-------|------|---------|
| Email | Champ texte | Identifiant principal du compte |
| Mot de passe | Champ texte masqué | Avec indicateur de force |
| Mot de passe oublié | Lien | Flux de réinitialisation par email |
| OAuth | Boutons | Connexion via Google / Apple (optionnel) |

## 1.2 Inscription

| Champ | Type | Détails |
|-------|------|---------|
| Email | Champ texte | Identifiant unique du compte |
| Mot de passe | Champ texte masqué | Confirmation obligatoire |
| Téléphone mobile | Sélecteur pays + numéro | Format international |
| Validation CGU | Case à cocher | Obligatoire pour continuer |
| Validation RGPD | Case à cocher | Consentement au traitement des données |

## 1.3 Choix du type de profil

Cet écran conditionne l'expérience utilisateur et les fonctionnalités accessibles.

| Champ | Type | Détails |
|-------|------|---------|
| Professionnel | Bouton radio | Débloque l'espace Coach (création de programmes, suivi clients) |
| Secteur | Liste déroulante | Affiché si professionnel (préparateur physique, coach fitness, kiné, etc.) |
| Non professionnel | Bouton radio | Accès standard à l'espace client |

## 1.4 Profil utilisateur

| Champ | Type | Détails |
|-------|------|---------|
| Nom, Prénom | Champs texte | Obligatoire |
| Date de naissance | Sélecteur de date | Pour calcul de l'âge et recommandations |
| Genre | Boutons radio | Homme / Femme / Autre / Ne pas préciser |
| Poids | Numérique + unité | kg ou lbs selon les préférences |
| Taille | Numérique + unité | cm ou ft/in selon les préférences |
| Avatar | Image dynamique | Visuel dynamique lié au genre + possibilité d'upload photo |
| Objectifs | Multi-sélection | Perte de poids / Prise de masse / Endurance / Remise en forme / Autre |
| Disciplines | Liste multi-lignes | Maximum 10 disciplines, avec bouton d'ajout |

## 1.5 Questionnaire d'onboarding

Complété à l'inscription, reconfigurable à tout moment depuis les paramètres.

| Champ | Type | Détails |
|-------|------|---------|
| Niveau sportif | Sélecteur | Débutant / Intermédiaire / Confirmé |
| Fréquence souhaitée | Sélecteur | X séances par semaine |
| Équipements disponibles | Multi-sélection | Salle complète / Home gym / Cardio uniquement |
| Zones prioritaires | Multi-sélection | Groupes musculaires à travailler en priorité |
| Blessures / Contre-indications | Champ texte libre | Pris en compte dans la génération de programmes |
| Durée de séance préférée | Sélecteur | 30 / 45 / 60 / 90 min |

## 1.6 Salle fréquentée

| Champ | Type | Détails |
|-------|------|---------|
| Recherche | Champ texte + géolocalisation | Recherche par nom ou proximité |
| Sélection | Liste de résultats | Sélection d'une ou plusieurs salles |
| Ajout manuel | Formulaire | Nom, adresse, ville (si salle absente de la base) |
| Salle principale | Indicateur | Possibilité de définir une salle par défaut |

## 1.7 Dashboard (accueil)

Écran principal après connexion. Hub central de l'application.

- Salutation personnalisée avec avatar dynamique
- Résumé rapide : nombre de séances (semaine/mois), streak d'activité
- Dernière performance : carte cliquable (discipline, date, résultat principal)
- Tendance : mini-graphe d'évolution sur la discipline principale
- Données de composition corporelle (poids, masse grasse, masse musculaire) si balance connectée
- Bouton proéminent « Nouvelle performance »
- Salle actuelle affichée (modifiable)
- Prochaine séance planifiée
- Éléments de gamification (streak, niveau, badge récent)

Le contenu détaillé du dashboard sera affiné ultérieurement.

## 1.8 Recherche et sélection d'un coach

### Filtres de recherche
- Salle fréquentée
- Spécialité / discipline
- Disponibilité
- Tarif

### Fiche coach
- Photo, biographie, certifications
- Avis clients et note moyenne
- Tarifs
- Disciplines et spécialités

### Interactions
- Demande de première rencontre (« séance découverte »)
- Plusieurs coachs actifs simultanément (ex : coach musculation + coach cardio)

## 1.9 Tunnel de première rencontre

Flux structuré pour établir la relation coach/client :

1. Le client envoie une demande de découverte
2. Le coach reçoit une notification et accepte en proposant un créneau
3. La séance « Découverte » apparaît comme type dédié dans le calendrier partagé
4. Après la rencontre : confirmation mutuelle de la relation coach/client
5. Le client peut refuser sans conséquence et chercher un autre coach

## 1.10 Planning et agenda partagé

### Vue calendrier
- Vue semaine / mois
- Séances planifiées (avec ou sans coach)
- Statut visible : confirmé / en attente / annulé
- Code couleur par programme actif

### Gestion des créneaux
- Proposition de créneau par le client ou le coach
- Validation obligatoire par le coach avant confirmation
- Types de séances : Découverte / Encadrée / Solo guidée

### Notifications
- Rappel J-1, H-1
- Annulation, demande de validation

### Intégrations
- Synchronisation Google Calendar (optionnel)

## 1.11 Programmes

### Catalogue de programmes préconçus

Programmes prêts à l'emploi, disponibles dès l'installation.

- Navigation par objectif, discipline, niveau, durée
- Aperçu du programme avant engagement
- « Démarrer ce programme » → injection des séances dans le planning
- Suivi de progression : séance X sur Y, pourcentage d'avancement

### Programmes personnalisés par un coach
- Le coach crée et assigne un programme sur mesure
- Le client le retrouve dans son planning
- Le coach suit l'avancement et peut ajuster en cours de route
- Règle de priorité : le programme du coach prend toujours le dessus sur le programme IA ; l'IA comble les jours non couverts

### Programmes multiples
- L'utilisateur peut suivre plusieurs programmes en parallèle
- Code couleur ou étiquette par programme
- Détection de conflits (alerte, pas blocage)
- Chaque programme a sa propre barre de progression

## 1.12 Séances solo intelligentes

- Génération automatique d'un programme hebdomadaire basé sur le questionnaire d'onboarding
- Chaque séance = liste d'exercices avec sets / reps / poids suggérés
- Ajustement progressif automatique (charges augmentent si performances validées sur X séances consécutives)
- Mode guidé : écran par écran, minuterie de repos intégrée
- Possibilité d'ignorer ou modifier un exercice
- Le coach peut pousser son propre programme en remplacement ou complément des suggestions IA

## 1.13 Suivi des performances

### Saisie des données
- Manuelle : après une séance solo
- Par le coach : pendant ou après une séance encadrée
- Depuis un programme : pré-rempli, l'utilisateur valide ou ajuste
- Import automatique depuis apps connectées (Strava, Garmin, Fitbit)

### Structure d'une performance

| Champ | Type | Détails |
|-------|------|---------|
| Date et heure | Automatique / Manuel | Horodatage de la séance |
| Type de séance | Sélecteur | Solo / Encadrée / Programme |
| Discipline | Sélecteur | Parmi celles du profil |
| Catégorie | Sélecteur | Musculation / Cardio / Stretching / Mobilité |
| Exercice | Sélecteur ou scan QR | Depuis machine ou liste |
| Groupes musculaires | Multi-sélection | Auto-rempli selon l'exercice, modifiable |
| Séries × Répétitions × Poids | Numérique | Pour musculation |
| Distance | Numérique + unité | Pour cardio extérieur |
| Durée | Chrono / Manuel | Temps total de la séance ou de l'exercice |
| Allure moyenne | Calculé automatiquement | Distance / Durée |
| Fréquence cardiaque | Import ou manuel | Moyenne et max (optionnel) |
| Ressenti | Échelle 1-5 ou emojis | Important pour détection fatigue / surentraînement |
| Notes libres | Champ texte | Commentaires personnels |
| Source | Badge automatique | Manuelle / Garmin / Strava / Fitbit |

### Performances spécifiques par type

**Course / Cardio extérieur :** Distance, durée, allure, fréquence cardiaque, ressenti

**Fitness — Machine :** Exercice (scan QR ou manuel), machine (marque/modèle), séries (poids + répétitions), temps de repos, ressenti

**Fitness — Exercice libre :** Répétitions × séries, ou durée, poids additionnel optionnel, ressenti

**Sport collectif / autre :** Discipline, durée, rôle/poste, stats spécifiques, ressenti

### Historique et visualisation
- Historique chronologique filtrable par discipline, période, salle
- Graphiques de progression par exercice (courbe poids max, volume total)
- Tableau de bord hebdomadaire : séances réalisées vs prévues
- Partage avec le coach : automatique si option activée, ou manuel par séance

## 1.14 Scanner QR Code machine

### Flux nominal
1. Scan du QR code affiché sur la machine en salle
2. Identification automatique : marque, modèle, exercices associés
3. Pré-remplissage de la fiche de performance

### Flux machine inconnue (fallback)
1. QR code non reconnu → message « Cette machine n'est pas encore référencée »
2. Sélection du type de machine (presse cuisses, tirage vertical, développé couché, vélo, tapis, elliptique…)
3. Sélection de la marque (Technogym, Life Fitness, Hammer Strength, Precor, Matrix, Panatta…)
4. Saisie du modèle (texte libre)
5. Photo de la machine (optionnelle)
6. Envoi en backoffice avec le QR code associé → passage modérateur → ajout à la base
7. En attendant la validation : saisie manuelle sur un exercice générique correspondant

## 1.15 Vidéos pédagogiques

- Chaque exercice dispose d'une courte vidéo (15-45 secondes) générée par IA
- Contenu : positionnement, amplitude, points de vigilance, respiration
- Format silencieux avec légendes texte (adapté au contexte salle de sport)
- Accessible via bouton vidéo sur chaque exercice pendant une séance
- Visible aussi dans la fiche exercice depuis l'historique
- Technologie : génération IA (modèle vidéo génératif) + validation backoffice avant publication
- Plan B recommandé : vidéos tournées classiquement pour le top 50-100 exercices, IA pour compléter le catalogue

## 1.16 Appairage avec apps et objets connectés

### Applications sport

| Service | Protocole | Données récupérées |
|---------|-----------|-------------------|
| Strava | OAuth2 | Séances (course, vélo, natation), distance, durée, allure, FC. Webhook pour sync temps réel |
| Garmin | Garmin Health API | Séances, données quotidiennes (pas, calories, sommeil) |
| Fitbit | Web API OAuth 2.0 | Séances, données quotidiennes, fréquence cardiaque |

### Balances connectées

| Service | Protocole | Données récupérées |
|---------|-----------|-------------------|
| Withings | Health Mate API | Poids, IMC, masse grasse, masse musculaire, masse osseuse, eau corporelle |
| Renpho | API / pont Google Fit | Poids, composition corporelle. API limitée, passage possible par Google Fit |
| Xiaomi | API / pont | Données de pesée et composition corporelle |
| Garmin Index | Garmin Health API | Poids et composition corporelle intégrés à l'écosystème Garmin |

### Pont universel

Stratégie hybride recommandée : Apple Health (iOS) et Google Fit / Health Connect (Android) comme socle universel, complété par des intégrations directes pour les données enrichies.

### Règles de synchronisation
- Choix utilisateur : import automatique ou validation manuelle avant import
- Dédoublonnage : détection des doublons (même date, durée, discipline) avec alerte
- Badge de source sur chaque performance (manuelle, Garmin, Strava, Fitbit)

## 1.17 Composition corporelle

Écran de visualisation des données reçues des balances connectées.

- Courbes d'évolution : poids, masse grasse, masse musculaire, eau corporelle
- Historique des pesées
- Corrélation possible avec les performances (futur coaching)

## 1.18 Contacts et carnet d'adresses

### Découverte automatique
- Comparaison du carnet téléphone (numéros + emails) avec la base utilisateurs
- Affichage : « X personnes de vos contacts utilisent déjà l'app »
- Distinction par type : coachs retrouvés vs autres utilisateurs
- Consentement RGPD explicite pour l'accès au carnet, données non matchées non stockées

### Liste de contacts
- Coachs fréquentés
- Partenaires d'entraînement
- Ajout manuel par recherche (pseudo, email)

## 1.19 Messagerie

Messagerie asynchrone légère, optimisée pour limiter la charge serveur.

### Fonctionnalités
- Conversations individuelles (coach ↔ client, utilisateur ↔ utilisateur)
- Messages texte courts
- Partage d'éléments internes : performances, programmes, séances
- Indicateur de messages non lus
- Notifications push

### Architecture technique recommandée
- V1 : Polling simple (client interroge le serveur toutes les X secondes)
- V2 : Migration vers WebSocket ou service tiers (Firebase, Stream) si la base utilisateurs le justifie

### Non inclus en V1
- Messages vocaux et vidéo
- Conversations de groupe
- Indicateur « vu » en temps réel et « en train d'écrire »

## 1.20 Gamification

Mécaniques de jeu intégrées pour favoriser l'engagement et la régularité. La gamification doit rester au service de la régularité, pas de la compétition toxique.

### Priorité haute (facile à implémenter, fort impact)
- Streaks : jours consécutifs d'activité, visuel qui évolue
- Badges / trophées : première séance, 10 séances, premier record, première séance avec coach…
- Progression de niveau : XP par séance, paliers (débutant → confirmé → expert…)

### Priorité moyenne
- Défis hebdomadaires : « Fais 3 séances cette semaine », « Bats ton record de squat »
- Comparaison amicale entre contacts sur une discipline (opt-in)
- Partage de badges dans la messagerie

### Priorité basse (ambitieux)
- Récompenses réelles : partenariats avec les salles (réduction si streak de 30 jours)
- Système « Coach du mois » basé sur les avis

Le ressenti saisi sur chaque performance permet de tempérer les défis en cas de fatigue détectée.

## 1.21 Paramètres

| Champ | Type | Détails |
|-------|------|---------|
| Modification du profil | Formulaire | Genre, avatar, disciplines, salle, objectifs |
| Questionnaire d'onboarding | Lien | Reconfigurable à tout moment |
| Changement d'email | Formulaire + confirmation | Validation par email |
| Changement de mot de passe | Formulaire | Ancien + nouveau + confirmation |
| Notifications | Bascules on/off | Par type : rappel séance, message, défi, streak… |
| Unités | Sélecteur | km / miles, kg / lbs |
| Apps connectées | Écran dédié | Liste des connexions, ajouter / supprimer |
| Déconnexion | Bouton | |
| Export des données | Bouton | Obligation RGPD |
| Suppression du compte | Bouton + confirmation | Obligation RGPD, suppression irréversible |

---

# 2. Espace Coach

L'espace coach est accessible aux utilisateurs ayant choisi le profil « Professionnel ». Il s'ajoute à l'espace client (le coach peut aussi suivre ses propres entraînements). L'espace coach comprend des fonctionnalités de gestion de clientèle, de facturation, de création de programmes et de suivi des performances.

## 2.1 Fiche profil du coach

Le profil coach contient des informations supplémentaires par rapport au profil client standard.

| Champ | Type | Détails |
|-------|------|---------|
| Biographie | Champ texte riche | Présentation personnelle, parcours, philosophie |
| Spécialités | Multi-sélection | Disciplines et méthodes pratiquées |
| Méthodes | Champ texte | Approche pédagogique, méthodologie |
| Certifications / Diplômes | Upload documents | Photo du justificatif pour obtenir le badge « Vérifié » |
| Badge Vérifié | Badge automatique | Attribué après validation backoffice des justificatifs |
| RIB | Champ sécurisé | Intégration bancaire pour les versements |
| Photo | Upload | Photo professionnelle |
| Salles | Multi-sélection | Salles où le coach exerce |

## 2.2 Paramétrage des tarifs et forfaits

Après la création du profil, le coach doit obligatoirement paramétrer ses tarifs avant de pouvoir accepter des clients.

### Gestion des forfaits
- Ajout d'un forfait : nom, durée de séance (en minutes), nombre de séances, prix total
- Modification d'un forfait existant
- Suppression d'un forfait (avec alerte si des clients l'utilisent)
- Exemples : Forfait 5h, Forfait 10h, Forfait 20h

### Options de paiement
- Paiement en 1 fois (X1)
- Paiement en 2 fois (X2)
- Paiement en 3 fois (X3)
- Paiement en 4 fois (X4)

### Forfait gratuit
- Le coach peut créer un forfait gratuit (ex : séance découverte offerte, geste commercial)
- Possibilité de créditer un nombre d'heures gratuites pour un client spécifique

## 2.3 Gestion des clients

### Liste des clients

| Champ | Type | Détails |
|-------|------|---------|
| Liste des clients | Tableau filtrable | Avec statut : Actif / En pause / Terminé |
| Fiche client | Écran détaillé | Profil, objectifs, historique, forfait en cours |
| Performances du client | Historique complet | Accessible si le client a activé le partage |
| Notes privées | Champ texte | Visibles uniquement par le coach, non accessibles au client |

### Gestion des excuses et crédits
- Messages d'excuse : le coach peut envoyer un message d'excuse lors d'une annulation
- Crédit d'heures : possibilité de créditer un nombre d'heures supplémentaires pour un client (compensation, geste commercial)
- Forfait gratuit : attribution d'un forfait offert à un client

## 2.4 Demandes entrantes

### Notifications
- Réception des demandes de séance découverte avec notification push
- Informations du client demandeur visibles (profil, objectifs, niveau)

### Actions
- Accepter la demande
- Refuser la demande (avec message optionnel)
- Proposer un créneau alternatif

### Pipeline de suivi

Vue pipeline visuelle du parcours client :

- **En attente :** demande reçue, non traitée
- **Découverte planifiée :** créneau accepté, séance à venir
- **Actif :** relation coach/client confirmée après la découverte

## 2.5 Agenda partagé du coach

### Vue globale
- Vue calendrier de toutes les séances (tous clients confondus)
- Code couleur par client ou par type de séance
- Création de séances à l'initiative du coach

### Validation des créneaux
- Validation des demandes de créneau reçues des clients
- Séances encadrées confirmées = heures décomptées automatiquement du forfait client

### Annulations
- Possibilité d'annuler les rendez-vous de la journée
- Sélection des créneaux à annuler avec envoi d'un message d'excuse automatique ou personnalisé
- Pour chaque créneau annulé : choix entre report (proposition d'un nouveau créneau) ou annulation définitive
- Notification automatique au client concerné

## 2.6 Saisie des performances pour un client

- Saisie pendant ou après une séance encadrée
- Interface identique à la saisie client (mêmes champs, même structure)
- Le coach sélectionne le client concerné dans sa liste
- Saisie exercice par exercice avec les mêmes paramètres (séries, répétitions, poids, durée, ressenti)
- Confirmation envoyée au client pour validation (optionnel, configurable)
- La performance apparaît dans l'historique du client avec le badge « Saisie par le coach »

## 2.7 Programmes d'entraînement solo

Le coach crée des programmes structurés que le client suit en autonomie.

### Création du programme

| Champ | Type | Détails |
|-------|------|---------|
| Nom | Champ texte | Nom du programme |
| Description | Champ texte riche | Objectifs, philosophie, consignes générales |
| Durée | Numérique | En semaines |
| Jours cibles | Sélection multiple | Ex : Lundi (Push) / Mercredi (Pull) / Vendredi (Legs) |
| Séances | Constructeur | Pour chaque jour : liste d'exercices + sets / reps / poids cibles |

### Construction des séances
- Ajout de séances semaine par semaine
- Pour chaque séance : liste ordonnée d'exercices
- Pour chaque exercice : paramètres cibles (séries, répétitions, poids, durée, repos)
- Duplication d'une séance ou d'une semaine entière
- Réordonnancement par glisser-déposer

### Assignation et suivi
- Assignation à un ou plusieurs clients
- Le client suit le programme en mode guidé (écran par écran, minuterie)
- Le coach visualise l'avancement : séances réalisées vs prévues
- Comparaison performances réelles vs objectifs cibles
- Ajustement du programme en cours de route avec notification au client

### Destination du programme
- **Programme assigné à un client :** sélection du client, le programme apparaît dans son planning
- **Programme publié dans le catalogue :** visible par tous les utilisateurs, vitrine pour le coach, option gratuit / payant
- **Programme en brouillon :** non visible, bibliothèque personnelle de templates réutilisables

## 2.8 Gestion des paiements

### Forfaits et tarification
- Définition des forfaits (5h, 10h, 20h) avec tarifs associés
- Options de paiement fractionné : X1, X2, X3, X4
- Forfait gratuit (séance découverte, geste commercial)

### Facturation
- Facturation automatique selon les séances réalisées
- Historique des paiements par client
- Export CSV pour comptabilité

### Statuts de paiement
- **En attente :** facture émise, paiement non reçu
- **Payé :** paiement confirmé
- **En retard :** délai de paiement dépassé, alerte au coach

### Intégration paiement en ligne
- Intégration Stripe prévue en phase 2
- En V1 : suivi manuel des paiements avec statuts

## 2.9 Suivi des heures

- Compteur heures consommées / heures forfait pour chaque client
- Vue d'ensemble : tableau récapitulatif de tous les clients avec leur solde d'heures
- Alerte automatique quand il reste 2 séances ou moins sur un forfait (pour proposer un renouvellement)
- Historique des séances décomptées avec date, type et durée
- Décompte automatique à chaque séance encadrée confirmée

---

# 3. Récapitulatif des écrans

Vue d'ensemble de tous les écrans identifiés dans l'application.

| Groupe | Écrans | Estimation |
|--------|--------|------------|
| Onboarding | Connexion, Inscription, Type de profil, Profil, Questionnaire, Salle fréquentée | 6 écrans |
| Principal | Dashboard, Planning, Performances, Contacts, Messagerie | 5 écrans |
| Performance | Nouvelle perf (Course / Machine / Libre / Autre), Historique, Détail, Source connectée | 6 écrans |
| Planning | Calendrier, Recherche coach, Fiche coach, Réservation, Tunnel découverte | 5 écrans |
| Programmes | Catalogue, Détail programme, Suivi programme(s) en cours | 3 écrans |
| Séances solo | Génération programme, Mode guidé (écran par écran), Minuterie | 3 écrans |
| Vidéos | Lecture vidéo pédagogique (intégré aux fiches exercices) | 1 composant |
| Messagerie | Liste conversations, Fil de discussion | 2 écrans |
| Composition corporelle | Courbes et historique des mesures | 1 écran |
| Gamification | Badges, Streaks, Niveaux, Défis (intégré au dashboard + profil) | 2 composants |
| Paramètres | Profil, Sécurité, Notifications, Unités, Apps connectées, RGPD | 6 écrans |
| Coach — Profil | Fiche profil enrichie, Certifications, RIB | 2 écrans |
| Coach — Tarifs | Paramétrage forfaits, Options de paiement | 2 écrans |
| Coach — Clients | Liste clients, Fiche client, Notes privées, Crédits d'heures | 4 écrans |
| Coach — Demandes | Pipeline demandes entrantes (En attente / Planifiée / Actif) | 2 écrans |
| Coach — Agenda | Calendrier global, Validation créneaux, Annulations | 3 écrans |
| Coach — Performances | Saisie performance pour un client, Confirmation | 2 écrans |
| Coach — Programmes | Création/édition, Bibliothèque, Assignation, Suivi avancement | 4 écrans |
| Coach — Paiements | Facturation, Historique, Export CSV, Statuts | 3 écrans |
| Coach — Heures | Compteur heures, Alertes renouvellement, Historique décomptes | 2 écrans |

> **Total estimé : environ 60 écrans et composants**

---

# 4. Notes techniques et points d'attention

## 4.1 RGPD
- Consentement explicite pour l'accès au carnet de contacts (données non matchées non stockées côté serveur)
- Export des données personnelles sur demande
- Suppression irréversible du compte
- Consentement séparé pour chaque intégration tierce (Strava, Garmin, etc.)

## 4.2 Ajustement progressif automatique

L'algorithme d'ajustement des charges devra être conçu avec précaution pour éviter les blessures. Critères suggérés :

- Toutes les séries complétées au poids cible sur X séances consécutives
- Ressenti positif (3/5 ou plus)
- Prise en compte des blessures et contre-indications du questionnaire

## 4.3 Vidéos pédagogiques IA

La génération vidéo IA de mouvements sportifs reste un défi technique. Stratégie recommandée :

- Vidéos tournées classiquement pour les exercices les plus courants (top 50-100)
- Génération IA pour compléter le catalogue
- Validation systématique par le backoffice avant publication

## 4.4 Architecture messagerie

Pour limiter la charge serveur tout en offrant une expérience satisfaisante :

- V1 : polling simple (requête toutes les X secondes), suffisant pour une base utilisateurs modérée
- V2 : migration vers WebSocket ou service tiers (Firebase Cloud Messaging, Stream, SendBird) si nécessaire

## 4.5 Intégrations tierces

Toutes les intégrations passent par OAuth2. Stratégie hybride : Apple Health / Google Fit comme socle universel, complété par des APIs directes (Strava, Withings) pour des données plus riches.

## 4.6 Gestion des paiements

En V1, le suivi des paiements est manuel (le coach renseigne les statuts). L'intégration Stripe est prévue en phase 2 et couvrira :

- Paiement en ligne sécurisé (carte bancaire)
- Paiement fractionné automatisé (X2, X3, X4) via Stripe Installments ou paiements récurrents
- Versement automatique sur le RIB du coach (Stripe Connect)
- Facturation automatique avec génération de reçus
- Gestion des litiges et remboursements

Point d'attention : le paiement fractionné est soumis à réglementation. Une étude juridique sera nécessaire selon les pays ciblés.

## 4.7 Sécurité des données sensibles

Le RIB du coach et les données de paiement nécessitent des mesures de sécurité renforcées :

- Chiffrement des données bancaires au repos et en transit
- Accès restreint aux données sensibles côté backoffice
- Conformité PCI-DSS si traitement direct des cartes bancaires (ou délégation à Stripe)

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
