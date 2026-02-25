# 📋 MyCoach — Cahier des charges fonctionnel

> Version 0.1 — Périmètre : **Module Coach**
> Statut : En cours de rédaction

---

## 1. Présentation générale

MyCoach est une application de gestion destinée aux **coachs sportifs indépendants**. Elle permet au coach de gérer son activité au quotidien : clients, séances, paiements, planning et profil professionnel.

**Stack technique**
- Backend : Python / FastAPI + SQLite
- Frontend mobile : Kotlin / Android natif
- Planning : Google Calendar (API)
- Déploiement : Docker (Proxmox LXC)

---

## 2. Module Coach

### 2.1 Inscription & Profil

#### Création de compte
- Email + mot de passe (ou Google Sign-In)
- Informations personnelles : prénom, nom, numéro de téléphone

#### Profil professionnel
Le coach peut renseigner et modifier à tout moment :

| Champ | Type | Description |
|-------|------|-------------|
| Photo de profil | Image | JPG/PNG, max 5 Mo |
| Nom complet | Texte | Affiché aux clients |
| Biographie | Texte long | Présentation libre, parcours |
| Spécialités | Liste | Ex : musculation, yoga, running, nutrition… |
| Qualifications | Liste | Diplômes, certifications (BPJEPS, STAPS, etc.) |
| Années d'expérience | Nombre | |
| Tarif horaire par défaut | Montant € | Peut être personnalisé par client |
| Réseaux sociaux | URLs | Instagram, LinkedIn (optionnel) |

#### Sélection des salles de fitness
À l'inscription, le coach **choisit les salles Fitness Park** dans lesquelles il travaille.
- Sélection multiple par ville ou région
- Basé sur le référentiel officiel Fitness Park (346 clubs, `data/fitness_park_clubs.json`)
- Modifiable à tout moment depuis les paramètres
- Chaque salle est identifiée par : **Nom**, **Adresse**, **Code Postal**, **Ville**

---

### 2.2 Gestion des clients

#### Liste des clients
- Vue liste avec : nom, photo (optionnelle), solde courant (facturé − encaissé), nombre d'heures consommées
- Filtres : par salle, par solde (impayé), par activité récente
- Recherche par nom

#### Fiche client
| Champ | Description |
|-------|-------------|
| Nom, prénom | Obligatoire |
| Photo | Optionnel |
| Email | Pour les rappels de paiement |
| Téléphone | |
| Salle Fitness Park | Salle(s) fréquentée(s) par ce client |
| Tarif horaire | Peut différer du tarif par défaut du coach |
| Objectifs | Notes libres (prise de masse, perte de poids…) |
| Notes internes | Visibles uniquement par le coach |
| Date de début | Première séance |

#### Décompte des heures
- Total des heures consommées par le client (somme des séances)
- Total facturé = Σ (durée_séance_en_h × tarif_horaire) pour les séances facturées
- Total encaissé = Σ des paiements reçus
- **Solde = Total facturé − Total encaissé** (montant dû par le client)
- Historique complet séances + paiements sur la fiche client

---

### 2.3 Gestion des séances

Une séance représente **une heure ou une session de coaching** réalisée avec un client.

#### Enregistrement d'une séance
| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| Client | ✅ | Sélection depuis la liste |
| Date | ✅ | Date de la séance |
| Heure de début | ✅ | Pour la création de l'événement Google Calendar |
| Durée | ✅ | En minutes (ex : 60, 90) |
| Salle | — | Pré-rempli depuis le profil client, modifiable |
| Facturation | ✅ | Oui / Non (séance offerte, annulée…) |
| Notes | — | Contenu de la séance, observations |

#### Synchronisation Google Calendar
- Chaque séance enregistrée **crée automatiquement un événement** dans le Google Calendar du coach
- L'événement contient : nom du client, durée, salle, notes
- Un rappel est envoyé automatiquement : 24h avant + 1h avant
- Suppression de la séance = suppression de l'événement Calendar

---

### 2.4 Gestion des paiements

#### Enregistrement d'un paiement
| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| Client | ✅ | |
| Date | ✅ | |
| Montant | ✅ | En € |
| Méthode | — | Virement, espèces, carte, chèque, PayPal, Lydia… |
| Référence | — | Numéro de virement, chèque… |
| Notes | — | |

#### Suivi des impayés
- Vue dédiée : liste des clients avec un solde positif (argent dû)
- Possibilité d'envoyer un **rappel par email** au client depuis l'app
- Indicateur visuel (badge rouge) sur la fiche client si solde > 0

---

### 2.5 Planning (Google Calendar)

- Le planning est géré **nativement dans Google Calendar**
- L'app se connecte via OAuth2 (une seule autorisation)
- L'app Android affiche les événements des 14 prochains jours
- Le coach peut **créer une séance depuis l'app** → événement créé dans Calendar
- Le coach peut visualiser son **agenda de la semaine** depuis l'app (WebView Google Calendar)

---

### 2.6 Dashboard

Vue d'ensemble de l'activité du coach :

| Indicateur | Description |
|-----------|-------------|
| Clients actifs | Clients avec au moins 1 séance dans les 30 derniers jours |
| Séances ce mois | Nombre de séances réalisées le mois courant |
| Heures ce mois | Total des heures coachées le mois courant |
| CA du mois | Montant total facturé ce mois |
| Encaissé du mois | Montant total reçu ce mois |
| Impayés total | Solde dû par l'ensemble des clients |
| Prochaine séance | Prochain événement Google Calendar |

---

## 3. Référentiel Fitness Park

- **Source** : `data/fitness_park_clubs.json` (346 clubs, scraped depuis fitnesspark.fr)
- **Données** : Nom, adresse, code postal, ville, téléphone, URL
- **Usage** : Sélection de salle à l'inscription coach + affectation client/séance
- **Mise à jour** : Manuel (re-scrape du sitemap Fitness Park)

---

## 4. Roadmap

### ✅ v0.1 — Foundation (en cours)
- [x] Backend FastAPI + SQLite
- [x] App Android Kotlin (clients, séances, paiements, dashboard)
- [x] Référentiel Fitness Park (346 clubs)
- [x] Intégration Google Calendar

### 🔜 v0.2 — Profil & Salles
- [ ] Profil coach complet (photo, bio, qualifications)
- [ ] Sélection salles Fitness Park à l'inscription
- [ ] Affectation client ↔ salle
- [ ] Rappels de paiement par email

### 🔜 v0.3 — UX Mobile
- [ ] Formulaires de création complets (séances, paiements)
- [ ] Fiche client détaillée avec historique
- [ ] Vue Planning dans l'app Android
- [ ] Notifications push (rappel séance)

### 🔜 v1.0 — Multi-utilisateurs
- [ ] Authentification coach (JWT)
- [ ] Isolation des données par coach
- [ ] API multi-tenant
