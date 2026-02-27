# MyCoach — Cahier des charges fonctionnel DÉTAILLÉ v1.0

> Document de référence complet. Chaque module décrit les écrans, actions, validations, règles métier, cas d'erreur et notifications.

**Frontend :** Flutter 3.x — Android · iOS · Web (Riverpod + go_router + Dio)

---

## 🌍 INTERNATIONALISATION (i18n) — PRINCIPES FONDATEURS

L'application est **internationale dès le premier commit**. Ces règles s'appliquent à toutes les phases de développement, sans exception.

### Règles de développement (non négociables)
- **Zéro texte codé en dur** dans le code (Flutter ou Backend) — tout passe par les fichiers de ressources
- **Flutter :** fichiers .arb (flutter_localizations) par langue (`intl_fr.arb`, `intl_en.arb`, etc.)
- **Backend :** Répertoire `locales/` avec fichiers JSON par langue (`fr.json`, `en.json`, `es.json`…) — messages d'erreur, notifications, emails
- **Dates :** toujours stockées en UTC en base, converties en affichage selon `user.timezone`
- **Devises :** stockées en centimes (entier) + code ISO 4217 (`EUR`, `USD`, `GBP`…), jamais en float
- **Poids :** stockés en kg en base, affichés selon `user.weight_unit` (kg ou lb) avec conversion automatique
- **Numéros de téléphone :** format E.164 (`+33612345678`)
- **Codes pays :** ISO 3166-1 alpha-2 (`FR`, `BE`, `US`, `GB`…)
- **Codes langue/culture :** BCP 47 (`fr-FR`, `en-US`, `es-ES`, `pt-BR`…)

### Sélection de la culture (utilisateur)
- Détectée automatiquement depuis la locale système de l'appareil (Android : `PlatformDispatcher.instance.locale`)
- Modifiable dans Profil → Préférences → Langue
- Persistée en base (`user.locale`) → synchronisée sur tous les appareils
- Tout changement → rechargement de l'UI sans redémarrage (Android : `setState / ref.refresh()`)

### Ce que la locale contrôle
| Élément | Exemple fr-FR | Exemple en-US |
|---------|--------------|--------------|
| Dates | 25/02/2026 à 14h30 | Feb 25, 2026 at 2:30 PM |
| Devise | 50,00 € | $50.00 |
| Poids | 80 kg | 176 lb |
| Séparateur décimal | virgule (80,5) | point (80.5) |
| Premier jour semaine | Lundi | Dimanche |
| Notifications | En français | In English |

---

## 📱 DESIGN RESPONSIVE — PRINCIPE FONDATEUR

L'application Flutter est **responsive dès le premier écran** :
- Layouts avec `Flexible`, `Expanded`, `LayoutBuilder` — jamais de tailles fixes
- Textes avec `TextStyle` + `MediaQuery.textScaleFactor` — jamais en px fixes
- Aucune taille fixe codée en dur pour les éléments UI
- Testé sur : mobile compact (360dp), standard (411dp), tablette (600dp+), desktop web
- Orientation portrait principale, paysage supporté sans crash (Flutter OrientationBuilder)

---

## 🧙 PRINCIPE DU WIZARD MINIMALISTE

> **Règle d'or : moins on demande, plus on convertit.**

### Philosophie
- Le wizard d'inscription coach ET client demande **le strict minimum** pour créer un compte fonctionnel
- Dès que les informations obligatoires sont saisies, l'utilisateur peut **sortir et finir plus tard**
- Le profil incomplet est valide — l'app guide progressivement vers la complétion
- Aucune information non critique ne bloque l'accès à l'application

### Informations obligatoires (non différables)
| Rôle | Obligatoire au premier lancement |
|------|----------------------------------|
| Coach | Prénom + Nom + Email + Password (ou Google) + **Téléphone (E.164)** + CGU |
| Client | Prénom + Nom + Email + Password (ou Google) + CGU |

> ⚠️ **Le téléphone est obligatoire pour les coaches dès l'inscription** — validé par OTP SMS *avant* la vérification email.

### Informations différables (complétables plus tard)
| Champ | Coach | Client |
|-------|-------|--------|
| Téléphone | ❌ Obligatoire à l'inscription | ✅ Plus tard |
| Photo de profil | ✅ Plus tard | ✅ Plus tard |
| Pays / Langue | Auto-détecté (modifiable plus tard) | Auto-détecté |
| Biographie | ✅ Plus tard | — |
| Spécialités | ✅ Plus tard | — |
| Certifications | ✅ Plus tard | — |
| Jours/horaires de travail | ✅ Plus tard | — |
| Salles de sport | ✅ Plus tard | ✅ Plus tard |
| Tarification | ✅ Plus tard | — |
| Questionnaire fitness | — | ✅ Plus tard |
| Objectif / Niveau | — | ✅ Plus tard |
| Poids / Taille | — | ✅ Plus tard |

### Comportement du wizard
1. **Étape 1 (Client)** : Prénom + Nom + Email + Password + CGU → "Créer mon compte" → vérification email → Onboarding
1. **Étape 1 (Coach)** : Prénom + Nom + Email + Password + Téléphone + CGU → "Créer mon compte" → **OTP SMS** → vérification email → Onboarding
2. Après création : l'utilisateur est connecté et voit son profil incomplet
3. Un **bandeau de complétion** (barre de progression en haut du Dashboard) indique le % de profil rempli
4. Chaque section manquante affiche un bouton "Compléter" avec une explication courte
5. **Si l'utilisateur est au milieu du wizard** (étapes optionnelles) → bouton **"Terminer plus tard"** visible en permanence dans le header
6. Aucune étape optionnelle n'affiche de message d'erreur si elle est ignorée

---

## 🔐 DÉCISIONS TECHNIQUES ARRÊTÉES

| Composant | Choix | Notes |
|-----------|-------|-------|
| SGBD | **PostgreSQL 16** | Docker, multi-users, MVCC |
| ORM | SQLAlchemy 2 async + asyncpg | Driver natif async |
| Migrations | Alembic | Versionning schéma |
| Auth API | **API Key SHA-256** | `X-API-Key` header sur tous les appels |
| Auth Google | ID Token → `POST /auth/google` → API Key maison | 1 vérif Google puis lookup local |
| Auth email | bcrypt credentials → API Key maison | Même système unifié |
| Stockage Flutter | flutter_secure_storage (AES-256) | Jamais en clair |
| Révocation | `revoked = TRUE` en base | Multi-device, immédiat |
| Tarification | Séance unitaire + forfaits (N séances, prix, validité) + **tarif groupe** (seuil N participants → prix/client réduit) | Configurable par coach par session |
| Annulation | Pénalité si < délai configuré (défaut 24h) | Séance due au coach |
| Liste d'attente | File FIFO, fenêtre 30 min par candidat | Automatique à chaque libération |
| **Crédit obligatoire** | Un client doit avoir un forfait `active` avec `sessions_remaining >= 1` pour réserver — ou `allow_unit_booking = TRUE` sur la relation client/coach — ou séance de type `discovery` | Vérifié par le backend au `POST /bookings` → 402 si non respecté |
| **Sessions multi-clients** | Table `session_participants` — `sessions` n'a plus de `client_id` direct | Chaque participant a son propre statut, prix et état d'annulation |
| **Multi-coach** | Un client peut avoir N coachs simultanément — chaque coach gère ses propres sessions et forfaits | Chaque coach voit librement la liste des autres coachs du client |
| **Traçabilité consommation** | Table `package_consumptions` — ligne par crédit consommé ou dû | Id_pack · Id_Payment · Id_Client · minutes · date planif · statut (Consommé / Due / En attente) |
| **Chiffrement tokens OAuth** | Python applicatif Fernet — clé séparée `TOKEN_ENCRYPTION_KEY` | Clé jamais dans les requêtes SQL ; cohérent avec `EncryptedString` PII ; `EncryptedToken` TypeDecorator dédié |
| **Programme IA** | `programs.coach_id = NULL` + `source = 'ai'` — pas de faux utilisateur admin | Simplicité ; un programme IA n'appartient à aucun coach |
| **Personal Records (PRs)** | `exercise_sets.is_pr = TRUE` — pas de table dédiée | Index partiel `WHERE is_pr = TRUE` pour queryabilité ; recalcul à chaque sauvegarde |
| **Notation coach** | Non modélisé — Phase 2 uniquement | Aucune anticipation de schéma en Phase 0–1 |
| **i18n** | **BCP 47 locale par utilisateur (fr-FR, en-US…)** | Zéro texte codé en dur |
| Pays | ISO 3166-1 alpha-2 (FR, BE, US…) | Sur clubs, profils, devises |
| Devises | ISO 4217 (EUR, USD, GBP…) stockées en centimes | Jamais de float pour les montants |
| Dates | UTC en base, converti selon user.timezone | Pas de décalage horaire surprenant |
| Poids | Stocké kg, affiché kg ou lb selon préférence | Conversion automatique |

---

## 0. ARCHITECTURE DES RÔLES

### 0.1 Principe fondateur : Admin ⊇ Coach ⊇ Client

> **La hiérarchie est inclusive : chaque rôle supérieur possède TOUTES les fonctionnalités des rôles inférieurs.**

```
┌──────────────────────────────────────────────────────┐
│                      ADMIN                            │
│   Accès total à toutes les fonctionnalités            │
│                                                       │
│  ┌────────────────────────────────────────────────┐   │
│  │                    COACH                        │   │
│  │  + Gérer son agenda coach                      │   │
│  │  + Accepter/refuser des réservations           │   │
│  │  + Saisir les performances de ses clients      │   │
│  │  + Créer et assigner des programmes            │   │
│  │  + Gérer ses tarifs et forfaits                │   │
│  │  + Annulation en masse + SMS clients           │   │
│  │  + RIB et paiements reçus                      │   │
│  │  + Back-office de ses clients                  │   │
│  │                                                │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │               CLIENT                     │  │   │
│  │  │  - Réserver une séance                   │  │   │
│  │  │  - Gérer son agenda                      │  │   │
│  │  │  - Suivre ses performances               │  │   │
│  │  │  - Voir ses programmes                   │  │   │
│  │  │  - Gérer ses paiements/forfaits          │  │   │
│  │  │  - Liste d'attente                       │  │   │
│  │  │  - Profil client complet                 │  │   │
│  │  │  - Liens réseaux sociaux                 │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 0.2 Cas d'usage typique
Un coach peut **aussi être client d'un autre coach** : il réserve des séances, suit ses propres performances, utilise ses propres forfaits — exactement comme un client.

### 0.3 Implémentation backend

**Règles middleware :**
```
require_client  → tout utilisateur authentifié (client + coach + admin)
require_coach   → coach + admin
require_admin   → admin uniquement
get_current_user → tout utilisateur authentifié (sans contrainte de rôle)
```

| Rôle | require_client | require_coach | require_admin |
|------|---------------|--------------|--------------|
| client | ✅ | ❌ 403 | ❌ 403 |
| coach | ✅ | ✅ | ❌ 403 |
| admin | ✅ | ✅ | ✅ |

---

### 0.4 Matrice des accès par fonctionnalité

> ✅ Accessible · ❌ Non accessible · 👁 Lecture seule

#### Authentification & Compte

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Inscription (email + mot de passe) | ✅ | ✅ | ✅ |
| Connexion email / Google OAuth | ✅ | ✅ | ✅ |
| Vérification email | ✅ | ✅ | ✅ |
| Réinitialisation mot de passe | ✅ | ✅ | ✅ |
| Déconnexion / révocation API Key | ✅ | ✅ | ✅ |
| Refus inscription domaine jetable (yopmail…) | ✅ | ✅ | ✅ |

#### Profil utilisateur

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Modifier prénom / nom / email / photo | ✅ | ✅ | ✅ |
| Préférences langue, timezone, pays | ✅ | ✅ | ✅ |
| Bandeau de complétion de profil | ✅ | ✅ | ✅ |
| Renseigner son genre | ✅ | ✅ | ✅ |
| Renseigner son année de naissance | ✅ | ✅ | ✅ |
| Valider son numéro de téléphone (OTP SMS) | ✅ | ✅ | ✅ |
| Liens réseaux sociaux (ajouter / modifier / supprimer) | ✅ | ✅ | ✅ |
| Créer un profil client | ✅ | ✅ | ✅ |
| Créer un profil coach | ❌ | ✅ | ✅ |
| Modifier bio, certifications, spécialités | ❌ | ✅ | ✅ |
| Gérer ses salles de sport associées | ✅ | ✅ | ✅ |
| Gérer ses disponibilités / horaires | ❌ | ✅ | ✅ |
| Politique d'annulation | ❌ | ✅ | ✅ |
| Templates de messages d'annulation (SMS) | ❌ | ✅ | ✅ |
| Partager son profil (QR code / lien) | ❌ | ✅ | ✅ |
| RIB / Coordonnées bancaires | ❌ | ✅ | ✅ |

#### Onboarding

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Questionnaire onboarding client | ✅ | ✅ | ✅ |
| Wizard onboarding coach (7 étapes) | ❌ | ✅ | ✅ |
| Générer un lien d'enrôlement | ❌ | ✅ | ✅ |
| Gérer ses liens d'enrôlement | ❌ | ✅ | ✅ |

#### Recherche & Découverte

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Rechercher une salle de sport (par ville/enseigne) | ✅ | ✅ | ✅ |
| Enregistrer des salles favorites | ✅ | ✅ | ✅ |
| Déclarer ses salles de travail (profil coach) | ❌ | ✅ | ✅ |
| Rechercher un coach (filtres, localisation, salle) | ✅ | ✅ | ✅ |
| Voir la fiche publique d'un coach | ✅ | ✅ | ✅ |
| Voir les liens sociaux publics d'un coach | ✅ | ✅ | ✅ |
| Demander une séance découverte (si flag actif) | ✅ | ✅ | ✅ |

#### Réservations — côté client

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Réserver une séance | ✅ | ✅ | ✅ |
| Annuler une réservation | ✅ | ✅ | ✅ |
| Voir ses réservations | ✅ | ✅ | ✅ |
| Rejoindre une liste d'attente | ✅ | ✅ | ✅ |
| Quitter une liste d'attente | ✅ | ✅ | ✅ |
| Signaler une erreur de saisie de performance | ✅ | ✅ | ✅ |

#### Réservations — côté coach

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Voir les demandes de réservation | ❌ | ✅ | ✅ |
| Accepter / refuser une réservation | ❌ | ✅ | ✅ |
| Proposer un créneau à un client | ❌ | ✅ | ✅ |
| Marquer une séance comme no-show | ❌ | ✅ | ✅ |
| Annuler une séance (côté coach) | ❌ | ✅ | ✅ |
| Annulation en masse (vue jour) | ❌ | ✅ | ✅ |
| Diffusion SMS en masse aux clients | ❌ | ✅ | ✅ |
| Gérer sa liste de clients | ❌ | ✅ | ✅ |
| Ajouter des notes sur un client | ❌ | ✅ | ✅ |

#### Agenda

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Voir son agenda (vue client) | ✅ | ✅ | ✅ |
| Voir son agenda (vue coach avec gestion) | ❌ | ✅ | ✅ |
| Synchronisation Google Calendar | ✅ | ✅ | ✅ |

#### Performances & Suivi

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Voir ses propres performances | ✅ | ✅ | ✅ |
| Historique et graphiques de progression | ✅ | ✅ | ✅ |
| Records personnels (PRs) | ✅ | ✅ | ✅ |
| Séances solo guidées (IA) | ✅ | ✅ | ✅ |
| Paramètres de confidentialité (partage perfs) | ✅ | ✅ | ✅ |
| Saisir les performances d'un client | ❌ | ✅ | ✅ |
| Voir l'historique d'un client | ❌ | ✅ | ✅ |
| Enregistrer des paramètres de santé | ✅ | ✅ | ✅ |
| Historique santé (graphiques) | ✅ | ✅ | ✅ |
| Configurer le partage santé avec ses coaches | ✅ | ✅ | ✅ |
| Voir les paramètres de santé partagés d'un client | ❌ | ✅ | ✅ |

#### Programmes

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Voir son programme assigné | ✅ | ✅ | ✅ |
| Créer / modifier / archiver un programme | ❌ | ✅ | ✅ |
| Assigner un programme à un client | ❌ | ✅ | ✅ |
| Suggestions programme par IA | ✅ | ✅ | ✅ |

#### Paiements & Forfaits

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Voir son solde de séances restantes | ✅ | ✅ | ✅ |
| Acheter un forfait | ✅ | ✅ | ✅ |
| Historique de ses paiements | ✅ | ✅ | ✅ |
| Créer / configurer ses forfaits et tarifs | ❌ | ✅ | ✅ |
| Voir ses revenus et paiements reçus | ❌ | ✅ | ✅ |
| Tarification groupe (seuil N clients) | ❌ | ✅ | ✅ |

#### Intégrations

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Connecter Strava | ✅ | ✅ | ✅ |
| Connecter une balance Withings | ✅ | ✅ | ✅ |
| Révoquer une intégration OAuth | ✅ | ✅ | ✅ |

#### Notifications

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Recevoir des notifications push | ✅ | ✅ | ✅ |
| Gérer ses préférences de notifications | ✅ | ✅ | ✅ |
| Envoyer des SMS à ses clients | ❌ | ✅ | ✅ |

#### Conformité RGPD

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Exporter ses données personnelles | ✅ | ✅ | ✅ |
| Demander la suppression de son compte | ✅ | ✅ | ✅ |
| Gérer ses consentements | ✅ | ✅ | ✅ |
| Révoquer un consentement marketing | ✅ | ✅ | ✅ |

#### Administration (back-office)

| Fonctionnalité | Client | Coach | Admin |
|----------------|--------|-------|-------|
| Tableau de bord admin | ❌ | ❌ | ✅ |
| Gestion des utilisateurs (liste, suspension, suppression) | ❌ | ❌ | ✅ |
| Validation des certifications coach | ❌ | ❌ | ✅ |
| Gestion de la blocklist email (domaines jetables) | ❌ | ❌ | ✅ |
| Gestion des chaînes de salles de sport | ❌ | ❌ | ✅ |
| Statistiques globales de la plateforme | ❌ | ❌ | ✅ |
| Modération du contenu | ❌ | ❌ | ✅ |
| Gérer la liste des paramètres de santé | ❌ | ❌ | ✅ |
| Consulter et modérer les feedbacks | ❌ | ❌ | ✅ |

---

## 1. AUTHENTIFICATION

### 1.1 Inscription Coach
**Écran :** `RegisterScreen` (rôle = Coach)

**Champs OBLIGATOIRES (unique étape bloquante) :**
- Prénom (min 2 chars, max 150 chars — noms internationaux supportés)
- Nom (min 2 chars, max 150 chars — noms internationaux supportés)
- Email (format RFC5322, unicité vérifiée côté serveur)
- **Téléphone (E.164)** — indicatif pays auto-détecté depuis la locale (sélecteur modifiable) ; format +33 6 12 34 56 78
- Mot de passe (min 8 chars, au moins 1 majuscule + 1 chiffre)
- Confirmation mot de passe
- Case "J'accepte les CGU"

**Champs AUTO-REMPLIS (non bloquants, modifiables plus tard) :**
- Pays : auto-détecté depuis la locale système
- Langue : auto-détectée depuis la locale système

**Champs OPTIONNELS à l'inscription (complétables ici ou plus tard) :**
- Genre : `male` | `female` | `other` (non chiffré) — affiché dès le formulaire d'inscription
- Année de naissance : ex. 1990 (l'âge est calculé à l'affichage)

> ℹ️ Photo, spécialités, salles, tarifs, horaires → différables, complétables depuis le profil.

**Validations en temps réel :**
- Email : vérification format à la sortie du champ
- Téléphone : validation format E.164 + indicatif pays
- Password strength indicator (faible / moyen / fort)
- Confirm password : comparaison en temps réel

**Action "S'inscrire" :**
- Disabled tant que tous les champs obligatoires ne sont pas valides
- Tap → loader → appel API `POST /auth/register`
- Succès → **flux en 2 temps :**

**Étape A — Vérification SMS (OTP) :**
- Redirect `PhoneVerificationScreen`
- SMS envoyé automatiquement au numéro saisi
- 6 cases d'entrée du code (`[0-9a-z]`, 6 chars)
- Android : SMS auto-lu via SMS Retriever (aucune saisie manuelle)
- iOS : suggestion AutoFill clavier (textContentType: oneTimeCode)
- Bouton "Renvoyer le code" (cooldown 60s)
- Bouton "Modifier mon numéro" → retour formulaire
- Succès OTP → compte `phone_verified` → redirect `EmailVerificationScreen`

**Étape B — Vérification email :**
- Message : "Un email a été envoyé à [email]"
- Bouton "Renvoyer l'email" (cooldown 60s)
- Lien "Mauvais email ? → Retour à l'inscription"
- Durée de validité du lien : 24h
- Clic sur le lien : token vérifié → compte `active` → deep link → app ouverte
- Si token expiré → page web d'erreur avec bouton "Renvoyer un nouveau lien"
- Succès → redirect `CoachOnboardingScreen` (étape 1/7)

**Erreurs inscription :**
- Email déjà utilisé → message inline : "Cette adresse email est déjà utilisée"
- Téléphone déjà utilisé → message inline : "Ce numéro est déjà associé à un compte"
- Erreur serveur → toast : "Erreur lors de l'inscription, veuillez réessayer"

---

### 1.2 Inscription Client
Similaire à 1.1 avec les différences suivantes :
- **Téléphone : optionnel** à l'inscription (pas de validation OTP immédiate)
- **Genre** : optionnel, affiché sur le formulaire d'inscription (comme pour le coach)
- Flux : Inscription → Vérification email → `ClientOnboardingScreen` (questionnaire, étape 1/6)
- Pas d'étape OTP SMS à l'inscription (le téléphone peut être ajouté et validé plus tard depuis le profil)

---

### 1.3 Connexion
**Écran :** `LoginScreen`

**Champs :**
- Email
- Mot de passe (toggle afficher/masquer)

**Actions :**
- "Se connecter" → `POST /auth/login` → vérif bcrypt → génère `SHA256(email+hash+salt)` → `{ "api_key": "..." }` → stocké en `flutter_secure_storage` → redirect selon rôle
- "Mot de passe oublié" → `ForgotPasswordScreen`
- "Créer un compte" → `RegisterScreen`
- "Connexion avec Google" → OAuth2 Google

**Cas d'erreur :**
- Mauvais credentials → "Email ou mot de passe incorrect" (pas de distinction pour sécurité)
- Compte non vérifié → "Votre email n'est pas encore vérifié" + bouton "Renvoyer l'email de vérification"
- Compte suspendu → "Votre compte a été suspendu, contactez le support"
- 5 tentatives échouées → blocage 15 min avec message "Trop de tentatives, réessayez dans X minutes"

**Connexion Google :**
- Bouton → SDK Google Sign-In → obtention du Google ID Token côté app
- Envoi `POST /auth/google { id_token }` → backend vérifie via clés publiques Google
- Extrait : `sub`, `email`, `name`, `picture`
- Génère : `SHA256(sub + email + SECRET_SALT)` → stocké en `api_keys`
- Si nouvel utilisateur → `RoleSelectionScreen` (Coach ou Client ?)
- Si utilisateur existant → retourne `{ "api_key": "..." }` → login direct

**Auto-login :**
- Au lancement → lecture API Key depuis `flutter_secure_storage`
- Si présente → `GET /auth/me` avec `X-API-Key` → si 200 → auto-login silencieux → redirect dashboard
- Si 401 (clé révoquée ou expirée) → effacement locale → `LoginScreen`

---

### 1.4 Réinitialisation mot de passe
**ForgotPasswordScreen :**
- Champ email → "Envoyer le lien de réinitialisation"
- Succès (même si email inconnu, pour ne pas confirmer l'existence) → "Si cet email existe, un lien vous a été envoyé"
- Lien valable 1h
- Clic lien → `ResetPasswordScreen` : nouveau password + confirmation
- Validations identiques à l'inscription
- Succès → toast "Mot de passe modifié" → `LoginScreen`

---

### 1.5 Déconnexion
- Menu Profil → "Se déconnecter" → confirmation
- `DELETE /auth/logout` avec `X-API-Key` → `revoked = TRUE` en base
- Suppression locale de l'API Key (`flutter_secure_storage`)
- Redirect `LoginScreen`

**Déconnexion tous les appareils :**
- Profil → "Déconnecter tous mes appareils"
- `DELETE /auth/logout-all` → `revoked = TRUE` sur toutes les clés de l'utilisateur
- Cas d'usage : appareil perdu, suspicion de compromission

---

### 1.6 Validation du domaine email

Lors de l'inscription, le serveur vérifie que le domaine de l'adresse email n'est pas dans la liste noire des services de messagerie jetable/temporaire.

**Comportement :**
- Si le domaine est bloqué → 422 avec message explicite
- Liste configurable par les admins via l'API (GET/POST/DELETE `/admin/blocked-domains`)
- Seed initial : ~55 domaines connus (yopmail, mailinator, tempmail, guerrillamail…)
- Insensible à la casse : `USER@YOPMAIL.COM` et `user@yopmail.com` sont équivalents

**Modèle de données** — Table `blocked_email_domains` :
| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `domain` | VARCHAR(100) | Domaine en minuscules, UNIQUE |
| `reason` | TEXT NULLABLE | Raison du blocage |
| `created_at` | TIMESTAMPTZ | UTC |

---

### 1.7 Validation du numéro de téléphone (OTP SMS)

Le téléphone est **obligatoire pour les coaches** (saisi à l'inscription) et **optionnel pour les clients** (différable, depuis le profil).

**Déclenchement :**
- **Coach** : immédiatement après le formulaire d'inscription, avant la vérification email
- **Client** : depuis Profil → Téléphone (si le client souhaite ajouter/valider son numéro)

**Algorithme OTP :**
- 6 caractères aléatoires parmi `[0-9a-z]` (36 chars)
- 36^6 = 2 176 782 336 combinaisons possibles (~31 bits d'entropie)
- Génération via `secrets.choice` (CSPRNG)
- Exemples : `"a3f7k2"`, `"9x2m4p"`, `"b0z5r1"`

**SMS format (compatible sms_autofill (sms_autofill (Android SMS Retriever + iOS AutoFill) + iOS AutoFill)) :**
```
<#> Votre code MyCoach : a3f7k2
Expire dans 10 minutes.
FA+9qCX9VSu
```

**Android SMS auto-read :**
Sur Android, l'application utilise l'[sms_autofill (sms_autofill (Android SMS Retriever + iOS AutoFill) + iOS AutoFill)](https://developers.google.com/identity/sms-retriever) pour lire automatiquement le code sans intervention de l'utilisateur. Le hash applicatif en fin de SMS (11 chars) permet l'association avec l'app.

**Règles de sécurité :**
- Expiration : 10 minutes
- Max 3 tentatives par OTP (au-delà → invalider, demander un nouveau code)
- Rate limit : max 3 OTPs envoyés par heure par numéro

**API :**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/verify-phone/request` | Envoie un OTP SMS |
| POST | `/auth/verify-phone/confirm` | Valide le code reçu |

---

### 1.8 Genre et année de naissance (optionnels)

Tout utilisateur peut renseigner :
- **Genre** : homme (`male`) / femme (`female`) / autre (`other`) — 3 valeurs
- **Année de naissance** : ex. 1990 (l'âge est calculé à l'affichage)

**Saisie possible dès le formulaire d'inscription** (coach ET client) — affichés comme champs optionnels directement dans le formulaire pour favoriser la complétion. Modifiables à tout moment depuis le profil.

**Composant UI (Flutter) :** 3 boutons segmentés avec icônes
- ♂ Homme / ♀ Femme / ⚧ Autre
- Non renseigné par défaut (aucun pré-sélectionné)
- Peut être ignoré sans blocage

**Impact avatar :** Le choix du genre détermine l'avatar par défaut affiché (§1.9).

**API :**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| PATCH | `/users/me/profile` | Modifie gender et/ou birth_year |

---

### 1.9 Avatar par défaut

Tant que l'utilisateur n'a pas défini de photo de profil, un avatar par défaut est affiché selon son genre :
- Homme → `/static/avatars/default_male.svg`
- Femme → `/static/avatars/default_female.svg`
- Autre / non renseigné → `/static/avatars/default_neutral.svg`

Le champ `resolved_avatar_url` dans les réponses API retourne toujours une URL valide (avatar perso ou défaut). Ce champ est présent dans **toutes** les réponses API contenant un profil utilisateur.

---

## 2. ONBOARDING CLIENT (questionnaire)
## 2. ONBOARDING CLIENT (questionnaire)

> **Philosophie : wizard minimaliste. Seule la création du compte est obligatoire.**
> Le client accède au Dashboard immédiatement après inscription.
> Le questionnaire est proposé à l'entrée mais entièrement passable.
> Bouton **"Terminer plus tard"** présent à chaque étape optionnelle.

---

### Étape 1/6 — Informations essentielles *(OBLIGATOIRE)*
> Seule étape bloquante. Pré-remplie depuis l'inscription.

**Champs obligatoires (pré-remplis) :** Prénom / Nom

**Champs optionnels (différables) :**
- Photo de profil *(avatar généré par défaut)*
- **Numéro de téléphone** — format E.164, préfixe pays auto
- Date de naissance *(optionnel)*

**Bouton principal :** "Accéder à l'app →" → redirect Dashboard
**Bouton secondaire :** "Remplir mon questionnaire" → passe à l'étape 2

---

### Étape 2/6 — Objectif principal *(optionnel)*
> Bouton **"Terminer plus tard"** en header.

- Choix unique (cards illustrées) :
  - 🔥 Perte de poids / 💪 Prise de masse / 🏃 Endurance / 🌿 Remise en forme / 🏆 Performance / ✨ Autre

---

### Étape 3/6 — Niveau sportif *(optionnel)*
- Choix unique :
  - 🌱 Débutant (< 6 mois) / 🌿 Intermédiaire (6 mois–2 ans) / 🌳 Confirmé (> 2 ans)

---

### Étape 4/6 — Fréquence & durée *(optionnel)*
- Stepper : 1 à 7 séances / semaine (défaut = 3)
- Durée préférée : 30 / 45 / 60 / 90 min

---

### Étape 5/6 — Équipements & zones *(optionnel)*
- Équipements (multi-select) : Salle complète / Cardio uniquement / Home gym / Poids libres / Poids du corps
- Zones à cibler (multi-select) : Épaules / Pectoraux / Dos / Biceps / Triceps / Abdos / Fessiers / Quadriceps / Ischios / Mollets / Corps entier

---

### Étape 6/6 — Blessures *(optionnel)*
- Toggle "J'ai des blessures ou contre-indications"
  - Si Oui → multi-select zones + texte libre

**Bouton :** "Terminer mon profil ✓" → `POST /clients/questionnaire` → Dashboard

---

### Bandeau de complétion (Dashboard Client)
Affiché tant que le questionnaire est incomplet :
```
┌─────────────────────────────────────────────────────────┐
│  💡 Complétez votre profil pour des suggestions précises │
│  [🎯 Objectif] [📊 Niveau] [🏋 Équipements]             │
│                                       [Compléter →]     │
└─────────────────────────────────────────────────────────┘
```

---

## 3. GESTION DES SALLES DE SPORT

> Les salles de sport sont le point d'entrée pour trouver un coach. Les deux rôles (client et coach) interagissent avec les salles, mais différemment.

### 3.1 Rôle des salles par type d'utilisateur

| Utilisateur | Usage | Description |
|-------------|-------|-------------|
| **Coach** | Salles de travail | Déclare les clubs où il exerce → alimente son profil public + filtres de recherche |
| **Client** | Salles favorites | Enregistre les clubs qu'il fréquente → permet de filtrer les coachs disponibles dans ces salles |

### 3.2 Salles favorites côté client

**Accès :** Profil → Mes salles *(ou prompt à la première recherche de coach)*

**Fonctionnement :**
- Le client peut rechercher et enregistrer jusqu'à **10 salles favorites**
- Ces salles sont utilisées comme filtre pré-sélectionné lors de la recherche de coachs
- Elles peuvent être utilisées lors de la saisie d'une séance de tracking libre

**Recherche d'une salle :**
- Barre de recherche par **ville** ou **code postal**
- Filtre par **enseigne** (multi-select : Fitness Park, Basic-Fit, CMG Sports Club, Neoness, Keep Cool, L'Orange Bleue, Cercle, Episod, etc.)
- Résultats : nom salle, adresse, enseigne, nb de coachs disponibles dans cette salle
- Tap → ajout en favoris

**Gestion :**
- Liste "Mes salles" avec bouton ✕ pour retirer une salle
- Bouton "+ Ajouter une salle" → revient à la recherche

**Modèle de données — Table `user_gym_favorites` :**
| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID FK | Utilisateur (client ou coach) |
| `gym_id` | UUID FK | Référence `gyms.id` |
| `added_at` | TIMESTAMPTZ | UTC |

**Contrainte :** `UNIQUE (user_id, gym_id)` — pas de doublons

**API :**
| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| GET | `/users/me/gyms` | Client/Coach | Lister ses salles favorites |
| POST | `/users/me/gyms` | Client/Coach | Ajouter une salle `{ gym_id }` |
| DELETE | `/users/me/gyms/{gym_id}` | Client/Coach | Retirer une salle |

### 3.3 Salles de travail côté coach

**Accès :** Onboarding étape 5/7 OU Profil coach → Mes salles

**Fonctionnement :**
- Le coach déclare les clubs où il exerce (multi-select, pas de limite fixe)
- Ces salles apparaissent sur son profil public (§11.2) comme chips cliquables
- Elles alimentent les résultats de recherche : un coach n'apparaît dans les résultats d'une salle que s'il y est déclaré
- Gérées via le même endpoint `users/me/gyms` (la distinction coach/client est faite par le rôle)

### 3.4 Recherche de salles (moteur commun)

**Endpoint :** `GET /gyms/search`

**Paramètres :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `q` | string | Ville, CP, ou nom de salle |
| `brand` | string[] | Filtre enseigne (slug : `fitness_park`, `basic_fit`, `neoness`…) |
| `country` | string | ISO 3166-1 alpha-2 (défaut = pays de l'utilisateur) |
| `page` / `limit` | int | Pagination |

**Réponse par salle :**
```json
{
  "id": "uuid",
  "name": "Fitness Park Bondy",
  "brand": "fitness_park",
  "address": "12 rue de la République",
  "city": "Bondy",
  "postal_code": "93140",
  "country": "FR",
  "coaches_count": 8,
  "is_favorite": true
}
```

---

> **Philosophie : wizard minimaliste. Seule l'étape 1 est obligatoire.**
> Le coach peut accéder au Dashboard dès l'étape 1 validée.
> Le header affiche toujours un bouton **"Terminer plus tard →"** à partir de l'étape 2.
> Un bandeau de complétion (%) rappelle les sections manquantes sur le Dashboard.

---

### Étape 1/6 — Informations essentielles *(OBLIGATOIRE)*
> Seule étape qui bloque l'accès au Dashboard. Les champs sont minimalistes.

**Champs obligatoires (pré-remplis depuis l'inscription) :**
- Prénom / Nom (modifiables)

**Champs optionnels (différables) :**
- Photo de profil *(avatar généré par défaut si non fournie)*
  - Tap → Appareil photo / Galerie
  - Validation : min 200×200px, max 5 MB, jpg/png/webp, recadrage circulaire
- **Numéro de téléphone** — format E.164, aide saisie avec préfixe pays auto
- Date de naissance *(datepicker, adulte requis ≥ 18 ans si renseigné)*
- Biographie *(max 500 chars, compteur visible)*

**Bouton principal :** "Accéder à mon espace →" → sauvegarde partielle + redirect Dashboard
**Bouton secondaire :** "Continuer le setup" → passe à l'étape 2

---

### Étape 2/6 — Jours de travail & horaires *(optionnel)*
> Header : bouton **"Terminer plus tard"** → redirect Dashboard

**Structure :**
- 7 toggles (Lun — Mar — Mer — Jeu — Ven — Sam — Dim)
- Jours **activés** = jours de travail → déroulent les plages horaires
- Jours **désactivés** = jours de repos → grisés, libellé "Repos 😴"
- Pour chaque jour activé :
  - Heure début (time picker, pas 15 min)
  - Heure fin (doit être > heure début)
  - Bouton "+ Ajouter une plage" (ex: matin 09h–12h + après-midi 14h–19h)
  - Chaque plage supprimable par swipe
- Bouton "Appliquer à tous les jours activés" (copie le premier créneau)
- Résumé en bas : "Disponible : Lun–Ven 9h–19h · Sam 10h–14h · Dim repos"

> Ces horaires alimentent directement le calendrier de réservation visible par les clients.

---

### Étape 3/6 — Disciplines proposées *(optionnel)*
- Multi-select depuis la liste officielle des disciplines (voir `docs/DISCIPLINES.md`)
- Affichage groupé par catégorie : Fitness & Musculation · Mind & Body · Cardio · Danse · Combat · Aquatique · Outdoor · Santé
- Pour chaque discipline sélectionnée → capacité max par défaut pré-remplie (modifiable)
- Aucun minimum requis pour passer l'étape
- Ces disciplines apparaissent sur le profil public + servent aux filtres de recherche client

---

### Étape 4/6 — Certifications *(optionnel)*
- Bouton "+ Ajouter une certification" → mini-formulaire : nom, organisme, année, photo document (optionnel)
- Badge "Certifié ✓" après validation back-office

---

### Étape 5/6 — Salles de sport *(optionnel)*
- Sélection chaîne → recherche ville/CP → multi-select clubs (chips supprimables)
- Peut être fait plus tard depuis Profil → Mes salles

---

### Étape 6/7 — Tarification *(optionnel)*
> Sans tarif renseigné, le profil est visible mais non réservable — un bandeau l'indique.

- Devise (pré-sélectionnée depuis le pays du coach, modifiable)
- Tarif séance unitaire (montant + devise)
- Forfaits : lignes dynamiques (nom + nb séances + prix total + validité + visibilité publique)
- Séance découverte : toggle + tarif (gratuite ou payante) + durée
- Durée standard : 30 / 45 / 60 / 90 min

**Bouton principal :** "Continuer →" → passe à l'étape 7
**Bouton secondaire :** "Terminer plus tard"

---

### Étape 7/7 — Messages d'annulation *(optionnel)*

> **Objectif :** préparer à l'avance les messages envoyés aux clients en cas d'annulation de séances.
> Utilisés lors de l'annulation en masse depuis l'agenda (§7.5).

**Pré-rempli par défaut avec 1 message "Maladie" :**
```
🤒 Maladie
──────────────────────────────────────────────
Bonjour {prénom}, je suis malheureusement
malade et dois annuler notre séance du
{date} à {heure}. Je vous présente toutes
mes excuses et vous recontacterai rapidement
pour reprogrammer. — {coach}
──────────────────────────────────────────────
[✏️ Modifier]  [🗑️ Supprimer]
```

**Ajouter un template :**
- Bouton **"+ Ajouter un message"** → formulaire inline :
  - **Titre** (ex: "Urgence familiale", max 40 chars)
  - **Corps du message** (max 300 chars, textarea avec compteur)
  - Variables insérables : boutons `{prénom}` `{date}` `{heure}` `{coach}`
  - **Bouton "Enregistrer"**
- Maximum **5 templates** — le bouton "+" se grise au-delà

**Contraintes :**
- Au moins 1 template doit exister (le default maladie est supprimable uniquement s'il en existe un autre)
- L'ordre peut être changé par drag-and-drop (ordre = ordre d'affichage dans le sélecteur)
- Templates modifiables et supprimables depuis Profil Coach → "Messages d'annulation" (après le wizard)

**Bouton :** "Publier mon profil complet 🚀" → `POST /coaches/profile` → Dashboard

---

### Bandeau de complétion (Dashboard Coach)
Affiché tant que le profil est incomplet :
```
┌────────────────────────────────────────────────────────┐
│  🟡 Profil complété à 40%  ████░░░░░░                  │
│  [📸 Photo] [⚡ Spécialités] [🏋 Salles] [💶 Tarifs] [🕐 Horaires] │
│  Complétez votre profil pour être mieux référencé      │
└────────────────────────────────────────────────────────┘
```
- Tap sur un badge → ouvre directement la section correspondante dans le profil
- Disparaît quand le profil est à 100%


---

## 4. DASHBOARD COACH

### 4.1 Vue principale
**Header :**
- Photo de profil + "Bonjour [Prénom] 👋"
- Date du jour

**Cartes KPIs (row scrollable) :**
- 📅 Séances cette semaine : N réalisées / M planifiées
- 👥 Clients actifs : N
- ⏱️ Heures ce mois : N,N h
- 💶 Revenus ce mois : N€

**Section "Prochaines séances" :**
- 3 prochaines séances (max)
- Chaque item : photo client, nom, date relative ("Demain 14h"), type, salle
- Tap → `SessionDetailScreen`
- Bouton "Voir tout" → `AgendaScreen`

**Section "Réservations à valider" :**
- Badge rouge avec le nombre
- 3 premières demandes en aperçu (photo + nom + créneau)
- Bouton "Voir tout" → `PendingBookingsScreen`
- Si vide : section masquée

**Section "Alertes" :**
- Clients avec forfait ≤ 2 séances restantes
- Chaque item : nom client, "Il reste N séance(s)"
- Tap → fiche client onglet Paiements

**État vide (nouveau coach) :**
- Illustration animée Lottie
- "Votre profil est en ligne !"
- Bouton "Partager mon profil" → génère un deep link `mycoach://coach/[id]` + share sheet

**Navigation bottom bar :**
Dashboard | Clients | Agenda | Perfs | Profil

---

## 5. GESTION DES CLIENTS (Coach)

### 5.1 Liste des clients
**Filtres tabs :** Tous | Actifs | En pause | Terminés
**Tri :** Alphabétique / Dernière activité / Séances restantes
**Barre de recherche** : par nom, filtrage temps réel
**Chaque card client :**
- Photo, Nom Prénom
- Badge statut coloré
- Séances restantes (si forfait actif) : "8 séances restantes"
- Dernière séance : "Il y a 3 jours"
**État vide :** "Aucun client pour l'instant — partagez votre profil !"

### 5.2 Fiche client — Onglet Profil
- Photo, nom, âge, objectif, niveau
- Salles fréquentées
- Blessures / contre-indications (si renseignées)
- Note privée du coach : zone texte libre (max 1000 chars), sauvegarde auto ou bouton "Enregistrer"
- Historique relation : date début, nb séances totales, statut
- Bouton "Suspendre la relation" → confirmation → statut `paused` → notif client
- Bouton "Terminer la relation" → confirmation + raison optionnelle → statut `ended` → notif client

### 5.3 Fiche client — Onglet Séances
- Tri chronologique inverse
- Filtres : Toutes / À venir / Passées / Annulées
- Chaque item : date, heure, type, durée, statut, icône annulation tardive si applicable
- Bouton "Planifier une séance" → `CreateSessionModal`
- Tap sur séance passée → "Saisir les performances" si non encore saisi

### 5.4 Fiche client — Onglet Programme
- Si programme assigné : nom du programme, semaine en cours (X/Y)
  - Vue compacte de la semaine (jours avec statut ✓/✗/⏳)
  - Tap → `ProgramDetailScreen` (suivi perfs réelles vs cibles)
- Si pas de programme : bouton "Assigner un programme"

### 5.5 Fiche client — Onglet Performances
- Si partage activé par le client :
  - Sélecteur d'exercice (dropdown)
  - Graphique courbe : poids max / volume
  - Période sélectionnable
- Si partage non activé : "Ce client n'a pas activé le partage de performances" (pas de bouton de sollicitation — respect vie privée)

### 5.6 Fiche client — Onglet Paiements
- Solde : "N séances restantes sur le forfait [Nom du forfait]" ou "Séances à l'unité"
- Barre de progression du forfait
- Historique transactions (date, montant, mode, statut)
- Bouton "Nouveau forfait" → `CreatePackageModal`
- Bouton "Enregistrer un paiement" → `RecordPaymentModal`
- Bouton "Exporter" → PDF ou CSV

---

## 6. RÉSERVATIONS (côté Coach)

### 6.1 Réservations en attente — `PendingBookingsScreen`
- Liste triée par date de séance (la plus proche en premier)
- Chaque item : photo client, nom, créneau demandé, salle, message du client (si renseigné)
- Bouton "Valider" → statut → `confirmed` → notif client
- Bouton "Refuser" → `RefusalModal`
  - Motif obligatoire (prédéfini ou texte libre)
  - Confirm → statut → `rejected` → notif client + libération créneau
- Timer visible si moins de 12h avant expiration auto-validation

### 6.2 Validation en masse
- Checkbox multi-sélection → "Valider les N sélectionnées"

---

## 7. AGENDA (Coach)

### 7.1 Vue calendrier
- Switcher de vue : Jour | Semaine | Mois
- Vue semaine par défaut
- Chaque séance affichée en bloc coloré :
  - 🔵 Découverte | 🟣 Encadrée | 🟠 En attente validation | ⬜ Annulée
- Tap → `SessionDetailModal`
- Long-press sur créneau vide → `CreateSessionModal` pré-rempli avec date/heure

### 7.2 Créer une séance (coach)
**Modal `CreateSessionModal` :**
- Client (dropdown, clients actifs — optionnel si cours collectif ouvert)
- **Discipline** (dropdown — disciplines configurées par le coach, voir `docs/DISCIPLINES.md`)
- Type : Découverte / Encadrée / Collectif
- **Capacité max** (stepper 1–999, pré-rempli depuis la discipline, modifiable)
  - Si capacité = 1 → séance individuelle
  - Si capacité > 1 → cours collectif, liste d'attente activée automatiquement si complet
- Date (datepicker, min = aujourd'hui + 1h)
- Heure de début (time picker, par tranche de 15 min)
- Durée (30 / 45 / 60 / 90 min)
- Salle (parmi les salles du coach)
- **Tarif** (pré-rempli depuis la discipline, modifiable)
- **Tarif groupe** (optionnel — seuil N participants + prix/client réduit)
- Note optionnelle pour le client (max 300 chars)
- Bouton "Envoyer la proposition" → statut `proposed_by_coach` → notif client

### 7.3 Détail d'une séance
**Selon statut :**
- `pending_coach_validation` : "Valider" / "Refuser"
- `proposed_by_coach` : "Annuler la proposition" (sans pénalité)
- `confirmed` (future) : "Reprogrammer" / "Annuler"
- `confirmed` (passée) : "Saisir les performances" / "Marquer comme no-show"
- `cancelled_late_by_client` : badge "💶 Séance due" + bouton "Exonérer"
- `done` : résumé des performances (si saisi)

**Annulation (coach, séance confirmée) :**
- Délai > politique d'annulation → statut `cancelled_by_coach` → notif client → créneau libéré → liste d'attente notifiée
- Délai < politique d'annulation → idem + question "Proposer un crédit compensatoire ?" → si oui : montant (€) → crédité au compte client

**Reprogrammation :**
- Ouvre `CreateSessionModal` pré-rempli (client, type, durée)
- Ancienne séance passe en `cancelled_by_coach`
- Nouvelle séance créée en `proposed_by_coach`

---

### 7.4 Sélection en masse (vue Jour)

> Cas d'usage principal : le coach est malade ou indisponible, il veut annuler **toutes ses séances du jour** en une action.

**Activation du mode multi-sélection :**
- Bouton **"Sélectionner"** dans la toolbar de la vue **Jour** uniquement
- Long-press sur une séance individuelle → active le mode sélection + coche cette séance

**Comportement en mode sélection :**
- Checkbox visible sur chaque séance de la journée
- Tap → coche / décoche
- Bouton **"Tout sélectionner"** en haut → coche toutes les séances actives du jour (statuts : `confirmed`, `pending_coach_validation`, `proposed_by_coach`)
- Compteur en temps réel : **"3 séances sélectionnées"**
- Bouton **"Annuler la sélection"** (croix) → désactive le mode, tout décoche

**Barre d'actions (flottante en bas, apparaît dès qu'au moins 1 séance cochée) :**
```
┌────────────────────────────────────────────────────────┐
│  ☑ 3 séances sélectionnées          [ Actions ▲ ]     │
└────────────────────────────────────────────────────────┘
```
- Tap **"Actions ▲"** → ouvre un bottom sheet

**Bottom sheet Actions en masse :**
```
┌─────────────────────────────────────────┐
│  Actions sur 3 séances                  │
│                                         │
│  ❌  Annuler les séances sélectionnées  │
│                                         │
│  [ Fermer ]                             │
└─────────────────────────────────────────┘
```

---

### 7.5 Annulation en masse — Workflow complet

**Étape 1 — Confirmation**

Modale :
```
┌──────────────────────────────────────────────────────┐
│  ⚠️ Annuler 3 séances le mardi 25 fév. ?            │
│                                                      │
│  Cette action est irréversible. Vos clients seront   │
│  notifiés de l'annulation.                           │
│                                                      │
│  [ Garder mes séances ]   [ Annuler les séances ]   │
└──────────────────────────────────────────────────────┘
```
- "Garder mes séances" → ferme, rien ne se passe
- "Annuler les séances" → passe à l'étape 2

**Étape 2 — Choix du message d'annulation**

Écran `BulkCancelMessageScreen` :
```
┌──────────────────────────────────────────────────────┐
│  ← Annulation en masse                               │
│                                                      │
│  Choisir le message envoyé à vos clients :           │
│                                                      │
│  ○ 🤒 Maladie                                        │
│    "Bonjour {prénom}, je suis malheureusement..."    │
│                                                      │
│  ○ 🚑 Urgence personnelle                            │
│    "Bonjour {prénom}, je dois faire face à une..."   │
│                                                      │
│  ○ ✍️ Message personnalisé                           │
│    [ Zone de texte libre — max 300 chars ]           │
│                                                      │
│  ─────────────────────────────────────────────────  │
│  📱 Envoyer par SMS aux clients concernés   [ ✓ ON ] │
│  (3 clients avec numéro de téléphone renseigné)      │
│                                                      │
│  [ Aperçu du SMS → ]                                 │
│                                                      │
│  [ Confirmer et annuler les séances ]                │
└──────────────────────────────────────────────────────┘
```

**Variables disponibles dans les messages :**
- `{prénom}` → prénom du client
- `{date}` → ex: "mardi 25 février"
- `{heure}` → ex: "10h30"
- `{coach}` → prénom du coach

**Aperçu SMS résolu (par client) :**
```
┌────────────────────────────────────────────┐
│  Aperçu — Julien                           │
│                                            │
│  Bonjour Julien, je suis malheureusement   │
│  malade et dois annuler notre séance du    │
│  mardi 25 fév. à 10h30. Je vous présente  │
│  toutes mes excuses et vous recontacterai  │
│  rapidement pour reprogrammer. — Marie     │
│                                            │
│  ◄ Précédent  1/3  Suivant ►               │
└────────────────────────────────────────────┘
```

**Étape 3 — Traitement et récapitulatif**

- Animation de chargement : "Annulation des séances en cours…"
- Une fois terminé : écran récapitulatif :
```
┌────────────────────────────────────────────┐
│  ✅ Annulation effectuée                   │
│                                            │
│  3 séances annulées                        │
│  3 SMS envoyés                             │
│  1 client sans numéro → non notifié par SMS│
│                                            │
│  Voir l'agenda                             │
└────────────────────────────────────────────┘
```

**Effets backend :**
- Toutes les séances sélectionnées → statut `cancelled_by_coach`
- Politique d'annulation tardive NON appliquée (annulation initiée par le coach)
- Créneau libéré pour chaque séance → liste d'attente notifiée (push)
- SMS envoyé pour chaque client avec numéro E.164 renseigné
- Log SMS créé en base (`sms_logs`)

---

### 7.6 SMS en masse (coach)

> Accessible également depuis **Mes clients → "📨 Envoyer un message à tous"**

**Fonctionnement :**
- Choix du scope : Tous les clients actifs / Clients d'une journée / Sélection manuelle (checkboxes)
- Choix du message : template ou message libre (max 300 chars)
- Résolution des variables par client
- Confirmation : "Envoyer X SMS ?"
- Envoi via le provider SMS configuré (Twilio par défaut)
- Récapitulatif : X envoyés, Y échoués (numéro invalide ou absent)

**Historique SMS :**
- Profil Coach → "Historique SMS"
- Liste chronologique : date, destinataire, extrait du message, statut (✅ envoyé / ❌ échec)

---

## 8. RÉSERVATION PAR LE CLIENT

### 8.0 Prérequis — Crédits validés

> **Règle fondamentale :** un client ne peut réserver une séance encadrée qu'à condition d'avoir des **crédits validés** auprès du coach concerné.

#### Définition d'un crédit valide

Un crédit est valide si le client dispose d'un forfait (`client_package`) avec le coach en statut **`active`** ET `sessions_remaining >= 1`.

Un forfait est `active` uniquement lorsque :
1. Le coach a créé le forfait (`POST /clients/{id}/packages`)
2. Le client a payé
3. Le coach a **enregistré le paiement** (`POST /payments`) → le forfait passe de `awaiting_payment` à `active`

#### Types de séance et règle de crédit

| Type de séance | Crédit requis | Notes |
|---------------|--------------|-------|
| Séance encadrée (individuelle ou groupe) | ✅ Oui | Vérifié à la réservation |
| Séance découverte | ❌ Non | Premier contact — gratuite ou payée hors app |
| Cours collectif ouvert (non lié à un forfait) | ❌ Non | Paiement sur place ou en ligne hors app |

#### Cas particulier : tarif à l'unité (sans forfait)

Le coach peut accorder à un client spécifique **l'accès sans forfait** (réglement à l'unité après la séance) :
- Profil coach → Fiche client → ⚙️ "Autoriser la réservation sans forfait"
- Flag `client_coach_relation.allow_unit_booking = TRUE`
- Dans ce cas, le crédit n'est pas vérifié, mais la séance est enregistrée et facturée manuellement par le coach

---

### 8.1 Calendrier de disponibilités du coach
**Accès :** Fiche coach → onglet "Réserver"
- Vue semaine avec navigation avant/arrière
- Limite : ne peut pas réserver au-delà de l'horizon configuré par le coach
- **Vérification des crédits avant affichage :** `GET /coaches/{id}/availability` retourne également `client_can_book: bool` + `sessions_remaining: int`
- Chaque créneau affiché :
  - 🟢 Disponible : tap pour réserver *(si `client_can_book = true`)*
  - 🟠 Dernière place (1 place restante) : tap + avertissement *(si `client_can_book = true`)*
  - 🔴 Complet : tap → `WaitlistJoinModal`
  - ⬛ **Non disponible** (`booked`) : créneau indisponible — soit occupé par un autre client (séance individuelle complète), soit bloqué par le coach (repos, congé, indisponibilité personnelle). Affiché grisé, non tappable.
  - 🟡 **Votre séance** (`mine`) : le client a déjà une réservation sur ce créneau — statut `pending_coach_validation` (en attente de confirmation du coach) ou `confirmed`. Indicateur "⏳ En attente" si `pending_coach_validation`, "✓ Confirmée" si `confirmed`.
  - 🔒 **Pas de crédit disponible** *(si `client_can_book = false`)* : tous les créneaux affichent une icône 🔒 et un bandeau :

```
┌─────────────────────────────────────────────────────┐
│  🔒 Vous n'avez pas de séances disponibles          │
│  Contactez [Prénom Coach] pour renouveler           │
│  votre forfait.                                     │
│                          [ Envoyer un message ]     │
└─────────────────────────────────────────────────────┘
```

### 8.2 Confirmation de réservation
**Modal :**
- Récapitulatif : coach, date, heure, durée, salle, discipline, tarif
- **Solde affiché :** "Il vous reste **N séance(s)** sur votre forfait [Nom du forfait]"
- Message optionnel pour le coach (max 300 chars)
- Bouton "Confirmer" → `POST /bookings`

**Vérification backend à la réception de `POST /bookings` :**
```
1. Le client a-t-il un forfait active avec sessions_remaining >= 1 pour CE coach ?
   OU allow_unit_booking = TRUE pour ce couple client/coach ?
   OU la session est de type "discovery" ?
   → Sinon : 402 Payment Required { detail: "no_credits_available" }

2. Le créneau est-il encore disponible ?
   → Sinon : 409 Conflict { detail: "slot_unavailable" }

3. Créer le booking (statut: pending_coach_validation)
```

**Réponse en cas d'absence de crédit (Flutter) :**
```
┌────────────────────────────────────────┐
│  ⚠️ Aucune séance disponible           │
│                                        │
│  Vous n'avez plus de séances sur votre │
│  forfait avec [Coach].                 │
│                                        │
│  [ Contacter mon coach ]               │
└────────────────────────────────────────┘
```

**En cas de succès :**
- Statut booking → `pending_coach_validation`
- Notifications :
  - Client : "Réservation envoyée — en attente de validation ⏳"
  - Coach : "Nouvelle réservation de [Client] pour le [date] à [heure] — [N-1] séances restantes sur le forfait"
- Timer côté coach : 24h pour valider → si dépassé → auto-rejet + notif client + libération créneau

### 8.3 Gestion de mes réservations (client)
**Agenda Client → liste filtrée :**
- À venir : statuts `pending_coach_validation`, `confirmed`
- Passées : statuts `done`, `cancelled_*`
- Chaque item avec statut lisible :
  - "En attente de validation" (avec timer)
  - "Confirmée ✓"
  - "Annulée"

### 8.3 Gestion de mes réservations (client)
**Agenda Client → liste filtrée :**
- À venir : statuts `pending_coach_validation`, `confirmed`
- Passées : statuts `done`, `cancelled_*`
- Chaque item avec statut lisible :
  - "En attente de validation" (avec timer)
  - "Confirmée ✓"
  - "Annulée"

---

## 9. SYSTÈME D'ANNULATION

### 9.1 Annulation par le client — Plus de 24h avant
**Depuis :** Agenda → séance → "Annuler"
- Modale confirmation : "Annuler la séance du [date] à [heure] ?"
- Boutons : "Confirmer l'annulation" / "Garder la séance"
- Confirmation :
  - Statut → `cancelled_by_client`
  - Séance **non décomptée** du forfait
  - Coach notifié : "❌ [Client] a annulé la séance du [date]"
  - Liste d'attente notifiée automatiquement (§10.2)

### 9.2 Annulation par le client — Moins de 24h avant
- Modale d'avertissement :
  > ⚠️ **Annulation tardive**
  > "Cette séance a lieu dans [Xh]. Conformément à la politique de [Coach], cette séance **sera comptée et débitée** de votre forfait."
- Boutons : "Confirmer quand même" / "Ne pas annuler"
- Si confirmation :
  - Statut → `cancelled_late_by_client`
  - Séance **décomptée** du forfait comme si réalisée
  - Coach notifié : "❌ [Client] a annulé la séance du [date] — 💶 séance due"
  - Entrée dans l'historique paiements client : "Annulation tardive — [date]"
  - Le coach peut exonérer depuis la fiche client

### 9.3 No-show client
- Coach peut marquer une séance passée comme "No-show" si le client ne s'est pas présenté
- Options configurables dans la politique du coach : No-show = due / non due
- Si due → même traitement qu'annulation tardive
- Notif client : "Votre séance du [date] a été marquée comme non honorée"

### 9.4 Annulation par le coach — Plus de 24h avant
- Depuis Agenda → séance → "Annuler"
- Modale : raison obligatoire
- Confirmation :
  - Statut → `cancelled_by_coach`
  - Séance **non décomptée**
  - Client notifié avec raison
  - Proposition directe dans la notif : "Reprogrammer ?" (si coach le souhaite)
  - Liste d'attente effacée (créneau annulé)

### 9.5 Annulation par le coach — Moins de 24h avant
- Idem 9.4 +
- Question supplémentaire : "Proposer un crédit compensatoire ?"
  - Oui → montant (€) pré-rempli avec tarif unitaire → validé → crédit ajouté au compte client
  - Non → annulation simple
- Client notifié avec mention du crédit si applicable

### 9.6 Configuration politique d'annulation (coach)
**Profil Coach → "Politique d'annulation" :**
- Délai de pénalité : 12h / 24h / 48h (défaut = 24h)
- Application de la pénalité : Automatique / Manuelle (coach décide au cas par cas)
- No-show : Due / Non due
- Message personnalisé affiché aux clients lors de la réservation (max 300 chars)
- Ce message est visible sur la page de réservation du coach

### 9.7 Exonération d'une pénalité (coach)
- Fiche client → onglet Paiements → séance annulation tardive → "Exonérer"
- Raison obligatoire (max 200 chars) : conservée dans les logs
- Séance retirée du décompte forfait

---

## 10. LISTE D'ATTENTE

### 10.1 Rejoindre la liste d'attente (client)
**Créneau complet → "📋 Liste d'attente" :**
- Modale d'information :
  - Position actuelle dans la file : "Vous seriez N° [X] dans la file d'attente"
  - Règle de notification : "Vous aurez 30 minutes pour confirmer si une place se libère"
  - Bouton "Rejoindre la liste d'attente" / "Annuler"
- Confirmation → inscription avec timestamp → notif coach (info seulement)
- Le client voit sur l'écran de réservation : "✋ En attente (position N°X)"
- Bouton "Quitter la liste d'attente" → suppression immédiate, sans pénalité

### 10.2 Libération d'une place — Workflow automatique
**Déclencheurs :**
1. Annulation par un client (libre ou tardive)
2. Refus de réservation par le coach
3. Expiration de la fenêtre de confirmation du 1er en attente (30 min)
4. No-show avec place libérée manuellement

**Séquence :**
1. Détection de place disponible
2. Récupération du 1er client dans la liste (ordre d'inscription)
3. Notification push urgente : "🎉 Une place s'est libérée ! [Coach] — [date] à [heure] — Confirmez dans **30 minutes** !"
4. Email de backup envoyé simultanément
5. Compte à rebours de 30 min côté serveur
6. Si confirmation dans les 30 min → réservation créée → validation coach déclenchée (§8.2)
7. Si pas de réponse en 30 min :
   - Client expiré → notif "Votre créneau en attente a expiré"
   - Client retiré de la file
   - Place proposée au suivant (même séquence)
8. Si file d'attente épuisée → créneau redevient visible et disponible sur le calendrier

### 10.3 Vue liste d'attente (coach)
**Agenda → tap sur créneau → onglet "Liste d'attente" :**
- Statut du créneau : X/N places occupées
- Participants confirmés (liste)
- File d'attente :
  - Position | Photo | Nom | Heure d'inscription | Statut (En attente / Notifié ⏳ / Expiré)
- Actions coach :
  - Réorganiser l'ordre (drag & drop)
  - Ajouter manuellement un client (recherche parmi ses clients actifs)
  - Retirer un client de la file (avec notif client)

### 10.4 Multi-places (group coaching)
- Si créneau avec N > 1 places :
  - Jusqu'à N réservations simultanées acceptées
  - L'affichage calendrier montre "3/5 places" par exemple
  - La liste d'attente ne s'active qu'à partir de N+1
  - Vue coach : liste de tous les participants confirmés + file d'attente séparée

**Architecture `session_participants` :**
- `sessions` ne référence plus directement un client unique — le lien coach ↔ client(s) passe par `session_participants`
- Chaque participant a son propre : statut, prix, message, état annulation, pénalité
- La machine d'état du §24 s'applique **par participant**, pas par session globale

**Tarif groupe :**
- Le coach peut définir sur chaque session (ou sur un modèle de session) :
  - `unit_price_cents` : tarif standard (1 client)
  - `group_price_threshold` : à partir de N participants → tarif groupe s'applique
  - `group_price_cents` : tarif par client quand le seuil est atteint
- Le tarif est recalculé automatiquement lorsque le Nième participant confirme
- Les participants déjà confirmés voient leur `price_cents` mis à jour dans `session_participants`
- Exemple : 80€/séance solo → 50€/client à partir de 2 participants

**Traçabilité consommation (`package_consumptions`) :**
- À chaque séance confirmée : une ligne `pending` créée avec la durée et la date planifiée
- À la fin de séance (statut `done`) : ligne passe à `consumed`
- Annulation tardive ou no-show : ligne passe à `due`
- Exonération coach : ligne passe à `waived`
- Permet de répondre à tout instant : "Combien de minutes de ce forfait sont consommées, dues, ou en attente ?"

**Multi-coach :**
- Un client peut avoir plusieurs relations actives simultanément avec plusieurs coachs
- Chaque coach gère ses propres sessions et forfaits pour ce client indépendamment
- Un coach peut consulter la liste des autres coachs actifs d'un client (lecture seule)
- La provenance de chaque donnée (workout_session, session, package) est toujours tracée via `coach_id`

---

## 11. PROFIL & RECHERCHE COACH (côté Client)

### 11.1 Écran de recherche
**Barre de recherche :** nom ou spécialité (recherche fulltext)
**Filtres (drawer latéral ou chips sous la barre) :**
- Chaîne de salle (multi-select)
- Club spécifique (dépend de la chaîne sélectionnée)
- Spécialité (multi-select)
- Tarif max (slider 20€–200€, par incrément de 5€)
- Séance découverte (toggle) — filtre `offers_discovery = true`
- Badge "Certifié ✓" (toggle)
- Disponible cette semaine (toggle)

**Badge "Séance découverte gratuite" sur les cards résultats :**
- Affiché uniquement si `coach_profile.offers_discovery = true`
- Apparaît sur la card dans la liste de résultats
- Visible seulement pour les clients qui **n'ont jamais eu de séance avec ce coach** (1ère relation)
- Si la séance découverte a déjà été consommée avec ce coach → badge masqué

**Résultats :**
- Liste (défaut) ou grille (switch)
- Chaque card : photo, nom, spécialités (3 max avec badge overflow "+2"), tarif/séance, note (si disponible), badge certifié, badge découverte (si applicable)
- Tri : Pertinence / Prix croissant / Prix décroissant / Les mieux notés
- Pagination ou scroll infini

### 11.2 Profil coach (vue client)
- Photo grande format (aspect ratio 16/9 avec gradient en bas)
- Nom, badge certifié si applicable
- Biographie complète
- Spécialités (chips)
- Certifications vérifiées (liste avec badge ✓)
- Salles (chips cliquables → maps)
- Tarifs détaillés (séance unitaire + forfaits disponibles)
- Disponibilités : "Généralement disponible : Lun, Mer, Ven — 9h–19h"
- Note et avis (phase 2)
- Bouton principal :
  - **"Demander une séance découverte 🎁"** si `coach_profile.offers_discovery = true` ET client sans relation préalable avec ce coach
  - **"Réserver une séance"** si déjà en relation active
  - **"Demande en cours"** (grisé) si demande découverte déjà envoyée et non traitée
  - **"Votre coach"** (grisé) si relation active
  - *(Le bouton découverte disparaît définitivement après consommation de la 1ère séance avec ce coach)*

### 11.3 Demande de découverte

**Règle métier `offers_discovery` :**
- Flag `coach_profile.offers_discovery: bool` — configurable par le coach dans ses tarifs (§6 Onboarding étape 6/7)
- Quand `true` : affiché sur le profil public + badge dans les résultats de recherche
- La séance découverte est une **première prise de contact**, gratuite ou à tarif réduit selon config du coach
- **Visibilité du badge :** uniquement pour les clients sans relation préalable avec ce coach — disparaît après consommation de la 1ère séance

**Flux :**
- Tap "Demander une séance découverte 🎁"
- Modal :
  - Info : tarif de la découverte (gratuite ou payante selon config coach), durée
  - Message optionnel pour le coach (placeholder : "Parlez-lui de vos objectifs...")
  - Bouton "Envoyer la demande"
- → Création booking type `discovery` → statut `pending_coach_validation` → notif coach → notif client "Demande envoyée ✓"
- Client peut annuler la demande tant que le coach n'a pas confirmé (bouton dans onglet "Mes coachs")
- **Pas de crédit requis** pour une séance `discovery` (exception à la règle §8)

---

## 12. AGENDA CLIENT

### 12.1 Vue calendrier
- Vue semaine (défaut) / mois
- Couleur différente par coach (palette automatique)
- Tous les types de séances visibles (découverte, encadrées, solo guidées)
- Point de couleur sur les jours avec séances (vue mois)
- Tap sur séance → `SessionDetailModal`

### 12.2 SessionDetailModal (client)
- Infos : coach, date, heure, durée, salle, type, statut
- Si statut `proposed_by_coach` : boutons "Accepter" / "Décliner" + message optionnel du coach
- Si statut `pending_coach_validation` : "En attente de validation — [timer]"
- Si statut `confirmed` (future) : bouton "Annuler" (avec règle 24h, §9)
- Si statut `confirmed` (passée) : bouton "Saisir mes performances"
- Si statut `cancelled_late_by_client` : mention "Cette séance a été décomptée de votre forfait"

### 12.3 Sync Google Calendar
**Profil → Intégrations → Google Calendar :**
- Bouton "Connecter Google Calendar" → OAuth2 → scopes : `calendar.events`
- Après connexion :
  - Toutes les séances confirmées poussées comme événements (titre, lieu = salle, description = coach + type)
  - Mise à jour temps réel sur changement de statut (annulation → événement supprimé)
- Option : sync bidirectionnelle → import GCal pour détecter conflits (avertissement lors de réservation)
- Bouton "Déconnecter" → révocation token + suppression événements MyCoach de GCal (optionnel)

---

## 13. TRACKING DES PERFORMANCES — SAISIE

### 13.1 Lancement d'une nouvelle entrée
**Points d'entrée :**
- Dashboard → "Nouvelle séance +"
- Séance passée dans agenda → "Saisir les performances"
- Programme → "Démarrer la séance guidée"
- Historique → "+" en bas de page

**Formulaire initial :**
- Date (défaut = aujourd'hui, datepicker si modifié)
- Heure de début (optionnel, défaut = maintenant)
- Type : Solo libre / Solo programme / Encadrée avec [sélection coach]
- Salle (optionnel, dropdown parmi ses salles)
- "Commencer" → `WorkoutSessionScreen`

### 13.2 WorkoutSessionScreen — Vue principale
- Header : timer en cours (chrono depuis le début)
- Liste des exercices ajoutés (scrollable, réordonnables par drag & drop)
- Pour chaque exercice :
  - Nom + icône muscle ciblé
  - Résumé : "3 séries × 10 reps × 40 kg"
  - Tap → `ExerciseDetailModal`
- Bouton "+ Ajouter un exercice" → `AddExerciseModal`
- Bouton "Terminer la séance" (en bas, sticky)

### 13.3 AddExerciseModal — QR Code
- Onglet "Scanner" (défaut) / "Manuel"
- Ouverture caméra avec overlay de scan
- Feedback scan réussi : vibration + son
- Identification : nom machine, marque, modèle, exercices suggérés (multi-select)
- Confirmation → ajout à la séance
- Si QR inconnu → message "Machine non reconnue dans notre base" → switch auto vers onglet Manuel

### 13.4 AddExerciseModal — Manuel
**Étape 1 — Type de machine/exercice (scroll list) :**
- Machines : Presse à cuisses, Tirage vertical, Développé couché machine, Smith Machine, Hack Squat, Leg Curl, Leg Extension, Hip Thrust, Shoulder Press machine, Poulie haute, Poulie basse, Cable croisé, Chaise romaine, Banc d'extension, Dip machine, Rowing machine
- Cardio : Vélo, Tapis de course, Elliptique, Rameur, Escalier
- Poids libres : Barre libre, Haltères, Kettlebell, Bande élastique
- Corps du corps : Pompes, Tractions, Dips, Gainage, Squats, Fentes, Burpees, etc.
- Autre (texte libre)

**Étape 2 — Détails (si machine) :**
- Marque (dropdown : Technogym, Life Fitness, Hammer Strength, Precor, Matrix, Panatta, Cybex, BH Fitness, Autre)
- Modèle (texte libre, optionnel)

**Étape 3 — Photo (optionnel mais encouragé) :**
- Prompt : "Aidez la communauté ! Photographiez la machine"
- Bouton "Prendre une photo" / "Galerie" / "Passer"
- Si photo prise → upload async → envoi back-office pour modération
- Toast : "Merci ! Votre contribution sera vérifiée sous 48h 🙌"

**Étape 4 — Exercice associé :**
- Sélection de l'exercice parmi ceux liés à ce type de machine (filtrés)
- Si type "Autre" → liste complète des exercices + recherche

**Confirmation → exercice ajouté à la séance**

### 13.5 ExerciseDetailModal — Saisie des sets
- Nom de l'exercice + muscles ciblés (chips)
- Bouton "📹 Voir la vidéo guide" → mini player inline
- Liste des séries :
  - Chaque série : Série N | [stepper reps] | [input poids kg] | ✓ (done toggle)
  - Validation d'une série (tap ✓) → **déclenche automatiquement le timer de repos** (si activé)
  - Swipe gauche sur une série → bouton rouge "Supprimer"
  - Bouton "+ Ajouter une série" (copie valeurs de la dernière série par défaut)

**⏱️ Timer de repos — configuration par exercice :**
- Toggle "Temps de repos automatique" (activé par défaut)
- Quand activé :
  - Presets rapides : **30s / 1min / 1m30 / 2min / 3min** (sélectionnable en un tap)
  - Valeur retenue par exercice (mémorisée pour cet exercice dans la session)
  - Le timer se lance automatiquement après chaque série validée → `RestTimerScreen` (plein écran)
  - Sur `RestTimerScreen` : +30s / −15s, ignorer le repos, série suivante
- Quand désactivé : aucun timer, enchaînement libre des séries

> **Distinction avec le temps de repos global (programmes)** : les programmes (§14.3) définissent un temps de repos *recommandé global* pour la séance. En séance libre (`WorkoutStartScreen`), le temps de repos est configuré *par exercice* dans ce modal. Les deux coexistent — le temps par exercice a priorité en séance libre.

- Note sur cet exercice (texte libre, max 200 chars)
- Bouton "Valider" → retour à `WorkoutSessionScreen`

**Validations :**
- Reps : min 1, max 999, entier
- Poids : min 0 (poids du corps), max 999, décimale possible (ex: 22.5 kg)
- Au moins 1 série requise pour valider

### 13.6 Fin de séance
- Tap "Terminer la séance"
- Validation : au moins 1 exercice avec au moins 1 série → sinon toast "Ajoutez au moins un exercice"
- Récapitulatif :
  - Durée totale
  - Nb exercices
  - Nb séries totales
  - Volume total (somme sets × reps × poids en kg)
  - Liste des exercices avec meilleure série par exercice
- Note de ressenti : 😴 1 – 😐 2 – 🙂 3 – 💪 4 – 🔥 5 (optionnel)
- Bouton "Sauvegarder" → `POST /performances` → animation Lottie confetti
- Si Strava connecté : bottom sheet "Pousser vers Strava ?" → Oui / Non
- Si partage coach activé → push automatique aux coachs liés
- Redirect `PerformanceHistoryScreen`

### 13.7 Saisie par le coach pour un client
**Accès :** Fiche client → Séances → séance passée → "Saisir les performances"
- Interface identique à 13.2–13.6
- Banner en haut : "Saisie pour [Nom Prénom du client] 👤"
- Sauvegarde → associée au compte client
- Notification au client : "Votre coach [Nom] a enregistré votre séance du [date]"
- Le client reçoit une notification avec option "Signaler une erreur" (flag simple → notification coach)

---

## 14. HISTORIQUE & GRAPHIQUES DE PERFORMANCES

### 14.1 PerformanceHistoryScreen
- Liste chronologique (plus récent en haut)
- Chaque item :
  - Date + heure
  - Type de séance (icône : solo / encadrée / programme)
  - Nb exercices
  - Volume total en kg
  - Note de ressenti (étoiles, si renseignée)
  - Icône si saisi par le coach
- Filtres :
  - Période : 7j / 30j / 3m / 6m / Tout
  - Type : Solo / Encadrée / Programme
  - Muscle ciblé (filtre les séances contenant un exercice ciblant ce muscle)
- Tap → `SessionSummaryScreen`

### 14.2 SessionSummaryScreen
- Détail complet : date, heure, durée, type, salle, ressenti
- Liste des exercices → pour chaque : toutes les séries (set × reps × poids)
- Volume par exercice
- Bouton "📹 Guide" disponible sur chaque exercice
- Bouton "Modifier" → accessible si < 48h ET saisi par l'utilisateur lui-même → réouvre `WorkoutSessionScreen` en édition
- Bouton "Supprimer" → confirmation → accessible si < 48h ET saisi par l'utilisateur

### 14.3 Graphiques de progression
**Accès :** Onglet "Stats" du dashboard ou depuis historique

- Sélecteur d'exercice (dropdown searchable)
- 2 graphiques superposables :
  - 📈 Poids max par séance (courbe)
  - 📊 Volume total par séance (barres ou courbe)
- Axe X : timeline
- Période : 2 sem / 1 mois / 3 mois / 6 mois / Tout
- PRs (records personnels) marqués sur la courbe (étoile ⭐ + tooltip)
- Si nouveau PR détecté lors d'une sauvegarde → notification push : "🏆 Nouveau record sur [exercice] : [poids] kg !"

### 14.4 Tableau de bord de la semaine
- Séances réalisées vs objectif (jauge circulaire)
- Radar chart : groupes musculaires travaillés cette semaine
- Streak de jours d'entraînement consécutifs (🔥 + nb jours)
- Volume total ce mois (kg)

---

## 15. SÉANCES SOLO GUIDÉES (IA)

### 15.1 Accès au programme
**Dashboard client → "Mon programme" (card dédiée)**
- Si questionnaire non rempli → redirect questionnaire
- Si programme coach assigné → affichage du programme coach (prioritaire)
- Si programme IA uniquement → affichage du programme généré

**Vue programme semaine :**
- 7 jours avec contenu :
  - Séance nommée (ex: "Push Day 💪")
  - Durée estimée
  - Muscles ciblés (icônes)
  - Statut : ⏳ À faire / ✓ Réalisée / ↩ Manquée
- Badge source : "Proposé par IA 🤖" ou "Programme de [Coach]"
- Bouton "Recalibrer le programme" → questionnaire express (objectif + fréquence + équipement, 3 questions)

### 15.2 Aperçu d'une séance du programme
**Tap sur une séance → `ProgramSessionPreviewScreen` :**
- Titre de la séance
- Durée estimée
- Liste des exercices avec : nom, sets × reps × poids cible, muscle ciblé
- Bouton "📹" sur chaque exercice → mini player
- Bouton "Commencer la séance" → `GuidedSessionScreen`
- Bouton "Modifier les exercices" (avant de commencer) → ajout / suppression / réordonnancement

### 15.3 GuidedSessionScreen — Déroulement
**Navigation :** exercice par exercice avec barre de progression en haut (1/6, 2/6...)

**Pour chaque exercice :**
- Nom, animation ou miniature vidéo (tap → plein écran)
- Muscles ciblés (heatmap corps ou chips)
- Liste des sets à réaliser :
  - "Set 1 — [reps] reps × [poids] kg" (cibles pré-remplies)
  - Champ poids modifiable (la saisie réelle peut différer de la cible)
  - Bouton "✓ Set réalisé" → déclenche le timer de repos
- Timer de repos :
  - Compte à rebours (durée selon type : 30–90s pour muscu, 60–120s pour lourd)
  - Vibration + son de fin
  - Bouton "Ignorer le repos → Série suivante"
  - Bouton "Prolonger (+30s)"
- Après tous les sets → bouton "Exercice suivant →"
- Bouton "Modifier cet exercice" → modale inline (poids, sets, reps)
- Bouton "Passer cet exercice" → modale confirmation + motif (Pas d'équipement disponible / Douleur / Trop difficile / Pas le temps / Autre)

### 15.4 Fin de séance guidée
- Récapitulatif : durée, exercices réalisés / skippés, volume total, meilleurs sets
- Animation Lottie de félicitations
- Ressenti 1–5 étoiles
- Bouton "Sauvegarder" → sauvegarde performances + marquage séance "réalisée" dans le programme
- Proposition Strava si connecté
- Message de motivation personnalisé basé sur les performances

### 15.5 Ajustement progressif automatique
**Règle d'évolution des charges :**
- Si 3 séances consécutives d'affilée : tous les sets réalisés au poids cible → +2.5 kg suggérés
- Si 1 set non atteint lors d'une séance → poids maintenu
- Si 2+ sets non atteints → poids réduit de 2.5 kg
- Notification : "💡 Programme mis à jour — progression détectée sur [exercice]"
- L'utilisateur peut refuser l'ajustement (bouton "Garder l'ancien poids")

---

## 16. PROGRAMMES COACH

### 16.1 Bibliothèque de programmes (coach)
**Coach → Menu → "Mes programmes" :**
- Liste des programmes créés
- Chaque card : nom, durée (X semaines), niveau cible, nb clients assignés, date création
- Bouton "+" → `CreateProgramScreen`
- Actions sur card : Modifier / Dupliquer / Archiver

### 16.2 Création d'un programme
**Étape 1 — Informations générales :**
- Nom du programme (obligatoire, max 80 chars)
- Description (max 300 chars)
- Durée : 1 à 52 semaines (stepper)
- Niveau cible : Débutant / Intermédiaire / Confirmé / Tous niveaux
- Objectif principal (même liste que questionnaire client)

**Étape 2 — Construction du programme :**
- Vue hebdomadaire (7 colonnes)
- Pour chaque jour : "Repos 😴" (défaut) ou bouton "+ Séance"
- Pour chaque séance créée :
  - Nom de la séance (ex: "Push Day", "Cardio HIIT", "Full Body")
  - Durée estimée (30 / 45 / 60 / 90 min)
  - Ajout d'exercices :
    - Recherche dans la base (nom, muscle, catégorie)
    - Pour chaque exercice : sets cibles, reps cibles, poids cible (ou "au ressenti" si non précisé)
    - Drag & drop pour réordonner
    - Swipe gauche pour supprimer
  - Temps de repos recommandé (global pour la séance : 30 / 60 / 90 / 120 / 180s)

**Étape 3 — Validation :**
- Aperçu complet du programme semaine par semaine
- Bouton "Enregistrer le programme"

### 16.3 Assignation d'un programme à un client
**Depuis :** Bibliothèque → programme → "Assigner" OU Fiche client → onglet Programme → "Assigner"
- Sélection du client (si accès via bibliothèque)
- Date de départ (datepicker, min = aujourd'hui, recommandé = lundi prochain)
- Option : "Ce programme remplace les suggestions IA" / "En complément des suggestions IA"
- Confirmation → `POST /programs/assign`
- Notification client : "🏋️ [Coach] vous a créé un programme sur [N] semaines !"

### 16.4 Suivi de l'avancement (coach)
**Fiche client → onglet Programme :**
- Barre de progression globale (semaines réalisées / totales)
- Vue semaine en cours : chaque jour avec statut ✓/✗/⏳
- Tap sur une séance réalisée → détail perfs réelles vs cibles
  - Pour chaque exercice : poids cible vs poids réel, sets/reps cibles vs réels
  - Indicateurs visuels : ✅ atteint / ⚠️ partiellement / ❌ non atteint
- Taux de complétion du programme (%)
- Graphique d'évolution des charges sur les exercices clés

---

## 17. VIDÉOS PÉDAGOGIQUES

### 17.1 Expérience client — Player vidéo
**Déclencheurs :** bouton "📹" visible sur :
- Chaque exercice dans `GuidedSessionScreen`
- Chaque exercice dans `ExerciseDetailModal`
- Chaque exercice dans `SessionSummaryScreen`
- Fiche exercice standalone

**Comportement :**
- Apparaît en overlay (bottom sheet) ou en plein écran (tap pour basculer)
- Lecture automatique en loop
- Silencieuse par défaut (pas de son ambiant) avec sous-titres texte
- Bouton volume pour activer le son si disponible
- Tap extérieur ou bouton ✕ → fermeture → reprend là où l'utilisateur était
- Si pas de vidéo disponible → illustration statique + liste de points clés texte

**Contenu de la vidéo :**
- 15 à 45 secondes
- Phases : position de départ → descente/aller → remontée/retour → points de vigilance
- Angles : vue de côté + vue de face (split screen ou alternance)
- Superposition texte : "✅ Dos droit" / "❌ Ne pas verrouiller les genoux"

### 17.2 Back-office — Génération IA
**Admin → Exercices → liste avec indicateur vidéo :**
- Filtre "Sans vidéo" → liste des exercices à traiter
- Pour chaque exercice : bouton "Générer la vidéo"

**Workflow de génération :**
1. Clic "Générer" → construction du prompt automatique :
   - Exercice, muscles ciblés, niveau de difficulté, points de vigilance
   - Angles souhaités (côté + face)
   - Style visuel : "Démonstration anatomique, éclairage salle de sport, modèle athlétique"
2. Appel API IA (Kling AI / Runway ML / Pika Labs)
3. Statut : Générée → En validation

**Validation :**
- Admin prévisualise la vidéo
- Boutons : "Valider et publier" / "Rejeter" (motif obligatoire) / "Regénérer avec prompt modifié"
- Si validée → statut `published` → disponible dans l'app immédiatement
- Si rejetée → possibilité de modifier le prompt et relancer

**Remplacement :**
- Sur un exercice avec vidéo existante → bouton "Remplacer la vidéo" → même workflow

---

## 18. BALANCE CONNECTÉE

### 18.1 Connexion
**Profil → Intégrations → "Balance connectée" :**
- Options : Withings / Xiaomi Mi Fit / Garmin Connect / Saisie manuelle uniquement
- Sélection → OAuth2 ou token API → test de connexion
- Succès → premier import déclenché
- Échec → message d'erreur avec guide de dépannage (permissions, app tierce à installer, etc.)

### 18.2 Import automatique
- Background sync toutes les 6h (ou à l'ouverture de l'app)
- Import de toutes les mesures depuis la dernière sync
- Données importées (selon disponibilité du capteur) :
  - Poids (kg) — obligatoire
  - IMC (calculé automatiquement si non fourni)
  - Masse grasse (%)
  - Masse musculaire (%)
  - Masse osseuse (%)
  - Eau corporelle (%)
  - Fréquence cardiaque au repos (bpm) — si dispo

### 18.3 Saisie manuelle
- Bouton "Ajouter une mesure" → modale :
  - Date (défaut = aujourd'hui)
  - Poids (obligatoire)
  - Autres métriques (optionnels)
  - Source : "Saisie manuelle"

### 18.4 Visualisation
- Onglet "Corps" dans le dashboard client
- Sélecteur de métrique (chips : Poids / Masse grasse / Masse musculaire / Eau)
- Courbe chronologique avec points de mesure
- Sélecteur période : 1m / 3m / 6m / 1an / Tout
- Si objectif de poids défini → ligne cible affichée + delta actuel vs objectif
- Dernière mesure mise en avant (date + valeur)

### 18.5 Partage avec le coach
**Profil → Intégrations → Balance → "Paramètres de partage" :**
- Toggle par métrique : Poids / Masse grasse / Masse musculaire / Autres
- Si activé → le coach voit les données dans la fiche client onglet Profil

---

## 19. STRAVA

### 19.1 Connexion
**Profil → Intégrations → Strava :**
- Bouton "Connecter Strava" → OAuth2 Strava
- Permissions demandées : `read`, `activity:write`, `activity:read_all`
- Après consentement → token stocké → test ping Strava
- Affichage : photo de profil Strava + nom d'athlète + statut "Connecté ✓"
- Bouton "Déconnecter" → révocation token côté Strava

### 19.2 Push séance vers Strava
**Déclencheur 1 — Automatique :**
- Si option "Push automatique" activée dans les paramètres Strava
- Chaque séance sauvegardée → push immédiat

**Déclencheur 2 — Manuel (bottom sheet après sauvegarde) :**
- "Envoyer cette séance à Strava ?"
- Boutons "Oui, envoyer" / "Non merci"

**Déclencheur 3 — Rétroactif :**
- Historique → séance → "Envoyer à Strava" (si pas encore envoyée)

**Données envoyées vers Strava :**
- Nom : "[Type séance] — MyCoach" (ex: "Musculation Push Day — MyCoach")
- Type d'activité : WeightTraining (muscu) / Workout (HIIT) / Ride / Run (cardio)
- Date et durée
- Description : liste des exercices avec meilleure série (généré automatiquement)
- Calorie estimée (si calcul disponible)

**Retour :**
- Toast : "✅ Séance envoyée à Strava"
- Lien vers l'activité Strava créée

### 19.3 Import depuis Strava
**Optionnel, activable dans Paramètres → Strava :**
- Import des activités Strava non présentes dans MyCoach (cardio outdoor : run, vélo, etc.)
- Chaque activité importée apparaît dans l'historique avec badge Strava
- Non modifiable (lecture seule, source = Strava)

---

## 20. PAIEMENTS

### 20.0 Disciplines & Capacité maximale (coach)

> Voir **`docs/DISCIPLINES.md`** pour la liste complète des 80+ disciplines organisées en 8 catégories.

**Profil coach → "Mes disciplines" :**
- Le coach sélectionne les disciplines qu'il propose parmi la liste de référence (multi-select, chips)
- Catégories : Fitness & Musculation · Mind & Body · Cardio & Endurance · Danse · Sports de Combat · Aquatique · Outdoor · Santé & Rééducation · Formats Spéciaux
- Pour chaque discipline sélectionnée :
  - **Capacité max par défaut** : pré-rempli selon la discipline (ex: Yoga → 12, Personal Training → 1), modifiable de 1 à 999
  - **Tarif par défaut** pour cette discipline (pré-remplit la création de séance)
- Ces réglages apparaissent comme chips sur le profil public du coach

**Création de séance → champ discipline :**
- Dropdown des disciplines configurées par le coach
- Capacité max pré-remplie depuis le réglage de la discipline, modifiable à la séance
- Tarif pré-rempli, modifiable
- Si capacité max > 1 → le tarif groupe peut être activé (§10.4)

**Forfait lié à une discipline :**
- Un forfait peut être restreint à une ou plusieurs disciplines (ex: "10 séances de Yoga Vinyasa")
- Ou générique (toutes disciplines — défaut)

---

### 20.1 Coordonnées bancaires du coach (RIB)

> **Objectif :** permettre au coach de saisir son RIB une seule fois et de le partager facilement aux clients qui souhaitent régler par virement.

#### Saisie et gestion (Profil coach → "Mes coordonnées bancaires")

**Champs RIB :**
| Champ | Obligatoire | Format | Notes |
|-------|-------------|--------|-------|
| Titulaire du compte | ✅ | Texte libre, max 70 chars | Peut différer du nom du coach |
| IBAN | ✅ | 34 chars max, format international | Validé par algorithme MOD-97. Ex: `FR76 3000 6000 0112 3456 7890 189` |
| BIC / SWIFT | ✅ | 8 ou 11 chars | Ex: `BNPAFRPPXXX` |
| Nom de la banque | ☐ | Texte libre, max 60 chars | Ex: "BNP Paribas" |
| Libellé virement | ☐ | Texte libre, max 140 chars | Texte suggéré sur l'ordre de virement (ex: "COACHING [PRÉNOM] [MOIS]") |

> ℹ️ Pour les coachs français uniquement, les champs détaillés (code banque, code guichet, numéro de compte, clé RIB) sont **déduits automatiquement** depuis l'IBAN.

**Comportement :**
- Le coach peut enregistrer **plusieurs RIBs** (ex: compte perso + compte pro) — maximum 3
- Chaque RIB a un **libellé interne** (ex: "Compte BNP pro", "Compte Crédit Agricole perso")
- Un seul RIB est marqué **par défaut** (utilisé dans les suggestions de virement)
- Bouton **"Prévisualiser le RIB"** → affiche le RIB formaté tel qu'il sera vu par le client
- Bouton **"Supprimer"** → confirmation requise

**Sécurité & Chiffrement :**
- IBAN et BIC stockés **chiffrés (Fernet, `FIELD_ENCRYPTION_KEY`)** — jamais en clair en base
- `iban_hash = SHA256(normalize(IBAN))` stocké en clair pour déduplication
- Jamais affiché en clair dans les logs ou les exports génériques
- Accès uniquement : coach (lui-même) + clients liés (lecture du RIB partagé)

---

#### Partage du RIB à un client

**Déclencheurs possibles :**
1. **Lors de la création d'un forfait client** → bouton "📎 Joindre mon RIB" dans `CreatePackageModal`
2. **Depuis la fiche client → Paiements** → bouton "Envoyer mon RIB"
3. **Réponse à une demande de client** → depuis la messagerie ou la notification

**Ce que reçoit le client (notification push + message in-app) :**
```
📄 Coordonnées bancaires de [Prénom Coach]

Titulaire : [Nom titulaire]
IBAN      : FR76 **** **** **** **** **** 189
BIC       : BNP*****XXX
Banque    : BNP Paribas

Libellé suggéré : "COACHING MARIE MARS 2026"

[ Copier l'IBAN ]   [ Voir le RIB complet ]
```

> ⚠️ **IBAN partiellement masqué** dans les notifications (4 premiers + 3 derniers chars visibles). Le client accède au RIB complet en tap → écran dédié, après confirmation identité (biométrie/PIN si configuré).

**Envoi du RIB :**
- `POST /coaches/me/bank-accounts/{id}/share`  
  Body : `{ client_id: UUID }`
- Crée un événement `rib_shared` en base (traçabilité : qui, à qui, quand)
- Log conservé 5 ans (obligation légale transactions financières)

---

#### Vue client — Écran RIB reçu

```
┌──────────────────────────────────────────────────────┐
│  📄 Coordonnées bancaires                            │
│  de Marie Dupont — Coach fitness                     │
│                                                      │
│  Titulaire : Marie Dupont                            │
│  IBAN      : FR76 3000 6000 0112 3456 7890 189       │
│  BIC       : BNPAFRPPXXX                             │
│  Banque    : BNP Paribas                             │
│                                                      │
│  Libellé à indiquer :                               │
│  "COACHING MARIE MARS 2026"                          │
│                                                      │
│  [📋 Copier l'IBAN]   [📤 Partager]                 │
│                                                      │
│  ℹ️  Ces coordonnées sont partagées par votre coach. │
│  MyCoach ne collecte aucun paiement.                 │
└──────────────────────────────────────────────────────┘
```

- Bouton **"Copier l'IBAN"** → copie dans le presse-papier (toast "IBAN copié ✓")
- Bouton **"Partager"** → share sheet natif (share_plus Flutter) (pour envoyer à son app bancaire)
- Historique des RIBs reçus : client → Mes paiements → "Coordonnées reçues" (liste triée par date)

---

#### Modèle de données

```sql
-- Comptes bancaires du coach (stockés chiffrés)
CREATE TABLE coach_bank_accounts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coach_id        UUID NOT NULL REFERENCES coach_profiles(id) ON DELETE CASCADE,
    label           VARCHAR(60) NOT NULL,               -- libellé interne coach
    account_holder  TEXT NOT NULL,                      -- chiffré Fernet
    iban            TEXT NOT NULL,                      -- chiffré Fernet
    iban_hash       CHAR(64) NOT NULL,                  -- SHA256(normalize(IBAN)), pour dédup
    bic             TEXT NOT NULL,                      -- chiffré Fernet
    bank_name       TEXT,                               -- chiffré Fernet (optionnel)
    transfer_label  VARCHAR(140),                       -- libellé virement suggéré (non chiffré)
    is_default      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT max_3_bank_accounts CHECK (
        (SELECT COUNT(*) FROM coach_bank_accounts cb WHERE cb.coach_id = coach_id) <= 3
    )
);

-- Log des partages de RIB (traçabilité légale)
CREATE TABLE rib_shares (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_account_id UUID NOT NULL REFERENCES coach_bank_accounts(id),
    coach_id        UUID NOT NULL REFERENCES coach_profiles(id),
    client_id       UUID NOT NULL REFERENCES users(id),
    shared_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    -- Conservation 5 ans minimum
);

CREATE UNIQUE INDEX uq_iban_per_coach ON coach_bank_accounts (coach_id, iban_hash);
CREATE INDEX idx_bank_accounts_coach ON coach_bank_accounts (coach_id);
```

---

### 20.2 Définition des forfaits (coach)
**Profil coach → "Mes forfaits" :**
- Forfaits prédéfinis (modifiables à tout moment) :
  - Nom (ex: "Pack 10 séances Yoga"), nb séances, prix total, prix unitaire (calculé)
  - Disciplines couvertes : toutes (défaut) ou sélection restreinte depuis `docs/DISCIPLINES.md`
  - Option : durée de validité (ex: valable 3 mois)
- Ces forfaits apparaissent dans la liste lors de l'attribution à un client

### 20.2 Créer un forfait pour un client
**Fiche client → Paiements → "Nouveau forfait" :**
- Sélection parmi les forfaits prédéfinis OU création ad hoc :
  - Nb séances, montant (€), date d'expiration (optionnel)
- Statut initial : `awaiting_payment`
- Notification client : "Votre coach [Nom] vous a créé un forfait de [N] séances — [Montant]€"

### 20.3 Enregistrer un paiement
**Fiche client → Paiements → "Enregistrer un paiement" :**
- Montant (€, obligatoire)
- Mode de paiement : Espèces / Virement / Carte bancaire / Chèque / Autre
- Date (défaut = aujourd'hui)
- Référence (optionnel, texte libre)
- Notes (optionnel)
- Validation → forfait passe en statut `active` → compteur heures activé
- Notification client : "✅ Paiement de [montant]€ enregistré — [N] séances disponibles"

### 20.4 Décompte automatique des séances
- Chaque séance encadrée passée en statut `done` → décompte automatique : -1 séance du forfait actif
- Si plusieurs forfaits actifs → décompte sur le plus ancien (FIFO)
- Si 0 séances restantes → alerte coach + notification client

### 20.5 Alertes forfait
**À 2 séances restantes :**
- Coach : "💡 [Client] a 2 séances restantes sur son forfait"
- Client : "🔔 Plus que 2 séances sur votre forfait — pensez à renouveler"

**À 0 séances :**
- Coach : "❌ [Client] n'a plus de séances sur son forfait"
- Client : "Votre forfait est épuisé — contactez votre coach pour renouveler"

### 20.6 Historique et export
**Fiche client → Paiements → "Exporter" :**
- Format : CSV ou PDF (choix)
- Colonnes CSV : Date, Client, Type, Nb séances, Montant, Mode paiement, Statut, Référence
- PDF : mise en page facture avec logo MyCoach, infos coach, infos client
- Filtre par période

---

## 21. NOTIFICATIONS — CATALOGUE COMPLET

| # | Déclencheur | Destinataire | Canal | Message |
|---|------------|-------------|-------|---------|
| 1 | Nouvelle demande découverte | Coach | Push + Email | "[Client] souhaite vous rencontrer 👋" |
| 2 | Demande de découverte acceptée | Client | Push + Email | "[Coach] a accepté ! Séance le [date] à [heure]" |
| 3 | Demande de découverte refusée | Client | Push | "[Coach] ne peut pas vous prendre en charge — Raison : [motif]" |
| 4 | Nouvelle réservation (client) | Coach | Push + Email | "Nouvelle réservation de [Client] — [date] à [heure]" |
| 5 | Réservation validée | Client | Push | "✅ Séance confirmée le [date] à [heure]" |
| 6 | Réservation refusée | Client | Push | "❌ Votre réservation du [date] a été refusée — [motif]" |
| 7 | Séance proposée par coach | Client | Push | "[Coach] vous propose une séance le [date] à [heure]" |
| 8 | Séance proposée par client | Coach | Push | "[Client] demande un créneau le [date] à [heure]" |
| 9 | Séance confirmée (les deux côtés) | Coach + Client | Push | "📅 Séance confirmée : [date] à [heure] — [salle]" |
| 10 | Séance annulée par client | Coach | Push | "❌ [Client] a annulé la séance du [date]" |
| 11 | Séance annulée par coach | Client | Push + Email | "❌ [Coach] a annulé la séance du [date] — [raison]" |
| 12 | Annulation tardive (client) | Coach | Push | "⚠️ [Client] a annulé la séance du [date] — 💶 Séance due" |
| 13 | Crédit compensatoire coach | Client | Push | "💰 [Coach] vous a crédité [N]€ suite à l'annulation du [date]" |
| 14 | Rappel séance J-1 | Coach + Client | Push | "⏰ Rappel : séance demain à [heure] avec [nom]" |
| 15 | Rappel séance H-1 | Coach + Client | Push | "⏰ Séance dans 1 heure avec [nom] — [salle]" |
| 16 | Place disponible (liste attente) | 1er en attente | Push + Email | "🎉 Une place s'est libérée ! [date] à [heure] — Confirmez dans 30 min !" |
| 17 | Expiration fenêtre liste attente | Client expiré | Push | "⌛ Votre créneau en liste d'attente a expiré" |
| 18 | Coach a saisi des perfs | Client | Push | "💪 [Coach] a enregistré votre séance du [date]" |
| 19 | Erreur signalée sur perfs | Coach | Push | "[Client] a signalé une erreur dans la séance du [date]" |
| 20 | Nouveau programme assigné | Client | Push | "🏋️ [Coach] vous a créé un programme sur [N] semaines !" |
| 21 | Programme modifié | Client | Push | "📋 [Coach] a mis à jour votre programme" |
| 22 | Nouveau record personnel | Client | Push | "🏆 Nouveau PR sur [exercice] : [poids] kg !" |
| 23 | Progression programme (IA) | Client | Push | "💡 Programme mis à jour — progression détectée sur [exercice]" |
| 24 | Forfait ≤ 2 séances | Coach + Client | Push | "⚠️ Plus que [N] séance(s) sur le forfait de [Client/votre forfait]" |
| 25 | Forfait épuisé | Coach + Client | Push | "❌ Forfait épuisé — à renouveler" |
| 26 | Paiement enregistré | Client | Push | "✅ Paiement de [montant]€ enregistré — [N] séances disponibles" |
| 27 | Machine validée (back-office) | Contributeur | Push | "✅ Votre contribution de la machine [modèle] a été validée !" |
| 28 | Certification validée | Coach | Push | "🎓 Votre certification [nom] a été vérifiée — badge Certifié ajouté !" |
| 29 | Strava push réussi | Client | Push | "📤 Séance envoyée à Strava ✓" |
| 30 | No-show marqué | Client | Push | "📋 Votre séance du [date] a été marquée comme non honorée" |

---

## 22. PROFIL UTILISATEUR

### 22.1 Paramètres Coach
- Modifier photo, prénom, nom, bio
- **Genre** (optionnel : Homme / Femme / Autre)
- **Année de naissance** (optionnel)
- **Numéro de téléphone** (obligatoire, validé OTP — modifiable si besoin de changer de numéro)
- **Pays** (ISO 3166-1 — affecte la devise par défaut et le filtrage des salles)
- **Langue / Culture** (BCP 47 : `fr-FR`, `en-US`, `es-ES`… — change l'UI immédiatement)
- **Devise** (ISO 4217 : EUR, USD, GBP… — appliquée à tous les tarifs)
- Spécialités (ajout/suppression)
- Certifications (ajout/suppression/modification)
- Salles de travail (ajout/suppression, filtrées par pays) — §3.3
- Tarifs et forfaits :
  - Séance unitaire
  - Forfaits
  - **Toggle "Séance découverte" (`offers_discovery`)** — active/désactive le badge et la fonctionnalité de 1ère séance découverte ; configurable : gratuite ou tarif réduit + durée
- Disponibilités (modifier les créneaux récurrents)
- Politique d'annulation (§9.6)
- Intégrations : Google Calendar, Strava
- Notifications : toggle par type (push + email séparément)
- Voir son profil public ("Aperçu client")
- Partager son profil (deep link + QR code personnel)
- Changer de mot de passe
- Suppression du compte

### 22.2 Paramètres Client
- Modifier photo, prénom, nom
- **Genre** (optionnel : Homme / Femme / Autre)
- **Année de naissance** (optionnel)
- **Numéro de téléphone** (optionnel — si renseigné : validé par OTP SMS)
- **Pays** (ISO 3166-1 — affecte les salles disponibles et la devise affichée)
- **Langue / Culture** (BCP 47 — change l'UI immédiatement)
- **Unité de poids** (kg / lb — affecte l'affichage des perfs et de la balance)
- Fuseau horaire (auto-détecté, modifiable — affecte l'affichage des horaires de séances)
- Refaire le questionnaire (objectif, fréquence, équipement)
- **Mes salles favorites** (ajout/suppression, filtrage par pays) — §3.2
- Poids et taille (pour calcul IMC, stocké en kg, affiché selon préférence)
- Poids cible (optionnel)
- Intégrations : Strava, Google Calendar, Balance connectée
- Partage des performances :
  - Toggle global "Partager mes performances"
  - Toggle par coach (si plusieurs coachs)
  - Toggle par type de donnée (séances / balance)
- Notifications : toggle par type
- Changer de mot de passe
- Suppression du compte → modale : "Votre compte sera définitivement supprimé dans 30 jours. Vous pouvez annuler cette demande depuis l'email de confirmation."

---

## 23. BACK-OFFICE ADMIN

### 23.1 Dashboard admin
- KPIs : Coachs actifs / Clients actifs / Séances ce mois / Machines en attente de modération / Vidéos en génération / **Coachs sans téléphone vérifié** / **Coachs avec séance découverte active**
- Graphiques : inscriptions par jour (courbe 30j), séances par jour

### 23.2 Modération machines
- Liste filtrée par statut : En attente | Validées | Rejetées
- Pour chaque soumission :
  - Photo (zoomable)
  - Type saisi, marque, modèle
  - Soumis par (nom client + date)
  - Nb de soumissions pour la même machine (agrégation par similarité)
- Actions :
  - Valider : corriger/compléter le type, marque, modèle → `published`
  - Rejeter : motif obligatoire → notification au contributeur
  - Demander plus d'infos : message envoyé à l'utilisateur
  - Fusionner avec une machine existante (doublon détecté)
- Génération de QR code (optionnel) → QR généré avec id machine → imprimable en PDF

### 23.3 Gestion des certifications coaches
- Liste coachs avec certifications en attente
- Pour chaque : photo du diplôme (zoomable), nom certif, organisme, année, nom du coach
- Bouton "Accorder le badge ✓" → coach notifié
- Bouton "Refuser" → motif → coach notifié

### 23.4 Gestion des vidéos
- Liste exercices filtrée : Tous / Sans vidéo / En génération / En validation / Publiées
- Pour chaque exercice sans vidéo : bouton "Générer"
- Pour chaque vidéo en validation : player + "Valider" / "Rejeter" / "Regénérer"
- Historique des générations par exercice (date, statut, prompt utilisé)
- Coût estimé API (si disponible)

### 23.5 Gestion des profils coaches
- Tableau filtrable : tous coachs / **sans téléphone vérifié** / **avec découverte active**
- Colonnes : Nom, Email, Téléphone (✓ vérifié / ✗ non vérifié), `offers_discovery`, Nb clients, Salles déclarées, Inscrit le
- Actions :
  - Voir le profil complet
  - Envoyer un rappel de vérification téléphone (si non vérifié)
  - Suspendre / réactiver le coach
  - Forcer la désactivation de `offers_discovery` si abus signalé

### 23.6 Gestion du répertoire salles
- Tableau filtrable par : chaîne, **pays (ISO 3166-1)**, ville, CP
- Bouton "Importer CSV" → format attendu :
  ```
  chain_name, name, address, zip_code, city, country (ISO 3166-1), latitude, longitude
  ```
- Ajout manuel d'un club (formulaire avec sélecteur pays obligatoire)
- Modification inline
- Suppression (avec confirmation, vérification qu'aucun coach ne référence ce club)
- Export CSV complet (avec colonne `country`)
- Vue carte (Leaflet / Google Maps) pour visualiser la couverture géographique

---

## 24. MACHINE D'ÉTAT — SÉANCES

```
                        ┌─────────────────────────────────────────────────┐
                        │            États d'une séance                   │
                        └─────────────────────────────────────────────────┘

[Client réserve]
      │
      ▼
pending_coach_validation ──(24h expiration)──► auto_rejected
      │                                              │
      ├─── Coach refuse ──────────────────────────► rejected
      │                                              │
      └─── Coach valide ──────────────────────► confirmed
                                                     │
                    ┌──────────────────────────────── ┤
                    │                                 │
         (> délai politique)            (< délai politique)
                    │                                 │
    Client annule ──► cancelled_by_client    cancelled_late_by_client
    Coach annule ───► cancelled_by_coach     cancelled_by_coach_late
                    │
                    └──────────────────────────────► done
                                                      │
                                                (coach marque)
                                                      │
                                              ► no_show_client
```

---

---

## 25. CONFORMITÉ RGPD

> Le RGPD (Règlement Général sur la Protection des Données) s'applique dès la première ligne de code — MyCoach traite des données de santé (poids, blessures, performances) classées comme **données sensibles (Art. 9)**.

### 25.1 Droits des utilisateurs

| Droit | Article | Endpoint | Délai |
|-------|---------|----------|-------|
| **Accès** | Art. 15 | `GET /users/me/export` | Immédiat |
| **Portabilité** | Art. 20 | `GET /users/me/export?format=csv` | Lien valide 24h |
| **Rectification** | Art. 16 | `PUT /users/me` | Immédiat |
| **Effacement** | Art. 17 | `DELETE /users/me` | Anonymisation J+30 |
| **Opposition** | Art. 21 | `PUT /users/me/notifications` (opt-out) | Immédiat |
| **Limitation** | Art. 18 | Compte `suspended` par admin | Sur demande |

### 25.2 Effacement — Règles d'anonymisation

L'effacement **ne supprime pas les lignes** — il anonymise les champs PII pour préserver la cohérence comptable et les statistiques agrégées.

**Données anonymisées (J+30) :**
- `users` : `first_name = "Utilisateur"`, `last_name = "Supprimé"`, `email = NULL`, `phone = NULL`, `google_sub = NULL`, `avatar_url = NULL`
- `email_hash` et `search_token` → vidés
- `api_keys` : toutes révoquées
- `coach_notes` : `content = NULL`
- `sms_logs` : `phone_to = NULL`, `body = NULL`

**Données conservées (base légale comptable — Art. 6(1)(c)) :**
- `sessions`, `package_consumptions`, `payments` : montants, dates, statuts — conservés 10 ans (obligation légale comptable)
- Référence via `user_id` qui pointe vers un compte anonyme (`role = "deleted"`)

**Données supprimées physiquement :**
- `email_verification_tokens`, `password_reset_tokens` : supprimés
- `integration_tokens` : révoqués + tokens OAuth supprimés
- `body_measurements` : supprimées (données de santé)
- `workout_sessions`, `exercise_sets` : supprimées (données de performance)

### 25.3 Export de données (portabilité)

Format JSON structuré :
```json
{
  "export_date": "2026-02-26T10:00:00Z",
  "user": { "first_name": "...", "last_name": "...", "email": "..." },
  "sessions": [...],
  "packages": [...],
  "payments": [...],
  "body_measurements": [...],
  "workout_sessions": [...]
}
```
- Lien de téléchargement généré → valide 24h → stocké temporairement sur CDN
- Données PII déchiffrées dans l'export (le fichier appartient à l'utilisateur)
- Export chiffré (ZIP protégé par mot de passe envoyé par email séparé) — **Phase 2**

### 25.4 Consentements

Table `consents` (log immuable — jamais de DELETE) :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id |
| `type` | ENUM | `terms`, `privacy_policy`, `marketing_emails`, `data_processing_health` |
| `version` | VARCHAR(10) | ex: `"v1.2"` |
| `accepted` | BOOLEAN | TRUE = accepté, FALSE = retiré |
| `accepted_at` | TIMESTAMPTZ | UTC |
| `ip_hash` | CHAR(64) | SHA-256 de l'IP (non-reversible) |
| `user_agent_hash` | CHAR(64) | SHA-256 du user-agent |

**Consentements obligatoires à l'inscription :**
- `terms` v1.0 — CGU
- `privacy_policy` v1.0 — Politique de confidentialité
- `data_processing_health` v1.0 — Traitement données de santé (Art. 9 RGPD)

**Consentement optionnel :**
- `marketing_emails` — Emails promotionnels

### 25.5 Registre des traitements (Art. 30)

Document `docs/RGPD_REGISTRE.md` — à tenir à jour :

| Traitement | Finalité | Base légale | Durée conservation | Sous-traitants |
|-----------|---------|-------------|-------------------|---------------|
| Gestion comptes | Exécution contrat | Art. 6(1)(b) | Durée relation + 30j | — |
| Sessions coaching | Exécution contrat | Art. 6(1)(b) | 10 ans (comptable) | — |
| Données de santé | Consentement explicite | Art. 9(2)(a) | Durée relation + 30j | — |
| Notifications SMS | Intérêt légitime | Art. 6(1)(f) | 12 mois | Twilio (DPA signé) |
| Authentification Google | Consentement | Art. 6(1)(a) | Session | Google (DPA via OAuth) |
| Intégration Strava | Consentement | Art. 6(1)(a) | Jusqu'à révocation | Strava (DPA) |

### 25.6 Durées de conservation

| Catégorie | Durée | Base |
|-----------|-------|------|
| Données de compte actif | Durée de vie du compte | Contrat |
| Données post-suppression (comptables) | 10 ans | Art. L123-22 Code Commerce |
| Logs d'authentification | 1 an | Recommandation CNIL |
| Consentements | 5 ans après retrait | Preuve de conformité |
| Tokens de vérification expirés | 30 jours | Nettoyage automatique (cron) |
| Données de santé (poids, blessures) | Durée relation + 30j | Consentement |

### 25.7 Sécurité des données (mesures techniques)

- ✅ Chiffrement des données PII au repos (Fernet AES-128, `FIELD_ENCRYPTION_KEY`)
- ✅ Chiffrement des tokens OAuth au repos (Fernet AES-128, `TOKEN_ENCRYPTION_KEY`)
- ✅ Chiffrement en transit (HTTPS/TLS 1.3 obligatoire en production)
- ✅ Hachage des mots de passe (bcrypt coût 12)
- ✅ API Keys non stockées en clair (SHA-256)
- ✅ Anonymisation des tokens dans les logs (`key_hash[:8]...`)
- ✅ `FlutterSecureScreen (platform channel)` sur les écrans sensibles (Android + iOS)
- ✅ Pas de PII dans les logs applicatifs

---

## 26. Liens Réseaux Sociaux

### 26.1 Vue d'ensemble
Chaque utilisateur (coach et client) peut renseigner jusqu'à **20 liens** vers ses profils réseaux sociaux ou URL personnalisées.

Deux types de liens coexistent :
- **Standard** : plateforme choisie dans la liste connue (instagram, tiktok…) → 1 seul par plateforme, UPSERT
- **Custom** : URL libre + label personnalisé (platform = NULL) → plusieurs autorisés, max 20 au total

### 26.2 Plateformes standard (liste évolutive)
| Plateforme | Slug | Description |
|-----------|------|-------------|
| Instagram | `instagram` | Profil Instagram |
| TikTok | `tiktok` | Profil TikTok |
| YouTube | `youtube` | Chaîne YouTube |
| LinkedIn | `linkedin` | Profil LinkedIn |
| X (Twitter) | `x` | Profil X |
| Facebook | `facebook` | Page/Profil Facebook |
| Strava | `strava` | Profil Strava |
| Site web | `website` | Site personnel ou professionnel |

> La liste est évolutive — de nouvelles plateformes peuvent être ajoutées sans migration.

### 26.3 Liens personnalisés (custom)
- `platform = NULL` : lien custom, label requis (ex : "Mon portfolio", "Ma boutique")
- Plusieurs liens custom autorisés par utilisateur (dans la limite des 20 total)
- UPSERT non applicable (chaque custom est une entrée distincte)

### 26.4 Règles
- **Max 20 liens** par utilisateur (tous types confondus) — 422 si dépassé
- URL : doit commencer par `http://` ou `https://`, max 500 caractères
- Label custom : max 100 caractères, obligatoire si `platform = NULL`
- Pas de chiffrement (URLs publiques par nature)
- UPSERT standard : poster sur une plateforme existante remplace l'URL

### 26.5 Visibilité par lien
Chaque lien a une visibilité indépendante :
- `'public'` *(défaut)* : visible par tous (visiteurs, clients, coachs)
- `'coaches_only'` : visible uniquement par les coachs avec relation active

### 26.6 Modèle de données
Table `user_social_links` :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id CASCADE |
| `platform` | VARCHAR(50) NULLABLE | Slug standard ou NULL (custom) |
| `label` | VARCHAR(100) NULLABLE | Libellé affiché — requis si platform IS NULL |
| `url` | TEXT | URL complète (https://...) |
| `visibility` | VARCHAR(20) | `'public'` ou `'coaches_only'` |
| `position` | SMALLINT | Ordre d'affichage (tri croissant) |
| `created_at` | TIMESTAMPTZ | UTC |
| `updated_at` | TIMESTAMPTZ | UTC — onupdate |

**Index** : UNIQUE partiel `(user_id, platform) WHERE platform IS NOT NULL` — autorise plusieurs custom, interdit doublons standard

### 26.7 API
| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| GET | `/users/me/social-links` | Tout utilisateur | Liste tous mes liens |
| POST | `/users/me/social-links` | Tout utilisateur | Créer/remplacer un lien |
| PUT | `/users/me/social-links/{id}` | Propriétaire | Modifier label/url/visibility/position |
| DELETE | `/users/me/social-links/{id}` | Propriétaire | Supprimer un lien par ID |
| GET | `/coaches/{id}/social-links` | Public | Liens `visibility='public'` d'un coach |

---

## 27. Suggestions & Rapports de bugs

### 27.1 Vue d'ensemble
Depuis l'application, tout utilisateur peut soumettre une suggestion d'amélioration ou un rapport de bug. Les feedbacks sont stockés côté serveur pour analyse ultérieure par l'équipe.

### 27.2 Règles
- Deux types : `suggestion` | `bug_report`
- Titre : max 200 caractères
- Description : max 5 000 caractères
- Informations techniques optionnelles : version de l'app, plateforme (android/ios/web)
- Statuts (gérés par admin) : `pending` → `reviewing` → `resolved` | `rejected`

### 27.3 Modèle de données — `user_feedback`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID NULLABLE | FK → users.id (SET NULL si supprimé) |
| `type` | VARCHAR(20) | `suggestion` ou `bug_report` |
| `title` | VARCHAR(200) | Titre court |
| `description` | TEXT | Description détaillée |
| `app_version` | VARCHAR(30) NULLABLE | Ex : "1.2.3" |
| `platform` | VARCHAR(20) NULLABLE | `android` / `ios` / `web` |
| `status` | VARCHAR(20) | `pending` / `reviewing` / `resolved` / `rejected` |
| `admin_note` | TEXT NULLABLE | Note interne de l'équipe |
| `created_at` | TIMESTAMPTZ | UTC |
| `updated_at` | TIMESTAMPTZ | UTC |

### 27.4 API

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| POST | `/feedback` | Tout utilisateur | Soumettre un feedback |
| GET | `/feedback/mine` | Tout utilisateur | Mes feedbacks |
| GET | `/admin/feedback` | Admin | Liste tous les feedbacks |
| GET | `/admin/feedback/{id}` | Admin | Détail d'un feedback |
| PATCH | `/admin/feedback/{id}` | Admin | Mettre à jour statut + note |

---

## 28. Historique des Paramètres de Santé

### 28.1 Vue d'ensemble
Tout utilisateur (coach ou client) peut enregistrer un historique de ses paramètres de santé. La liste des paramètres est administrable (admin peut ajouter/désactiver). L'utilisateur contrôle ce qu'il partage avec chacun de ses coaches, paramètre par paramètre.

### 28.2 Paramètres initiaux

| Slug | Label FR | Unité | Catégorie |
|------|----------|-------|-----------|
| `weight_kg` | Poids | kg | morphologie |
| `body_fat_pct` | % Masse grasse | % | morphologie |
| `muscle_mass_kg` | Masse musculaire | kg | morphologie |
| `bmi` | IMC | — | morphologie |
| `resting_heart_rate_bpm` | FC au repos | bpm | cardiovasculaire |
| `blood_pressure_systolic` | Tension systolique | mmHg | cardiovasculaire |
| `blood_pressure_diastolic` | Tension diastolique | mmHg | cardiovasculaire |
| `spo2_pct` | Saturation O₂ | % | cardiovasculaire |
| `vo2max` | VO₂max | mL/kg/min | forme |
| `sleep_hours` | Heures de sommeil | h | sommeil |
| `sleep_quality` | Qualité du sommeil | /10 | sommeil |
| `stress_level` | Niveau de stress | /10 | autre |
| `water_intake_ml` | Hydratation | mL | nutrition |
| `steps_daily` | Pas quotidiens | pas | forme |

### 28.3 Règles de partage (opt-out)
- Par défaut : **tout est partagé** avec tous les coaches actifs
- L'utilisateur peut masquer un paramètre spécifique pour un coach spécifique
- Le coach ne voit que les paramètres dont `shared = TRUE` (ou sans ligne = partagé)
- La préférence est sauvegardée par triplet (user_id, coach_id, parameter_id)

### 28.4 Modèles de données

**`health_parameters`** (liste administrable) :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `slug` | VARCHAR(50) UNIQUE | Identifiant technique |
| `label` | JSONB | i18n {"fr": "...", "en": "..."} |
| `unit` | VARCHAR(20) NULLABLE | Unité de mesure |
| `data_type` | VARCHAR(10) | `float` ou `int` |
| `category` | VARCHAR(30) | morphology/cardiovascular/sleep/fitness/nutrition/other |
| `active` | BOOLEAN | Visible dans l'app |
| `position` | SMALLINT | Ordre d'affichage |

**`health_logs`** (historique des mesures) :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id CASCADE |
| `parameter_id` | UUID | FK → health_parameters.id CASCADE |
| `value` | NUMERIC(10,3) | Valeur numérique |
| `note` | TEXT NULLABLE | Note libre |
| `source` | VARCHAR(20) | `manual` / `withings` / `strava` / `import` |
| `logged_at` | TIMESTAMPTZ | Date/heure de la mesure |
| `created_at` | TIMESTAMPTZ | Date de saisie |

**`health_sharing_settings`** (préférences de partage) :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id CASCADE |
| `coach_id` | UUID | FK → users.id CASCADE |
| `parameter_id` | UUID | FK → health_parameters.id CASCADE |
| `shared` | BOOLEAN | FALSE = masqué pour ce coach |

UNIQUE (user_id, coach_id, parameter_id)

### 28.5 API

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| GET | `/health/parameters` | Tout utilisateur | Liste paramètres actifs |
| POST | `/health/logs` | Tout utilisateur | Ajouter une mesure |
| GET | `/health/logs` | Tout utilisateur | Mon historique (filtres: parameter_id, from, to) |
| DELETE | `/health/logs/{id}` | Propriétaire | Supprimer une mesure |
| GET | `/health/sharing/{coach_id}` | Tout utilisateur | Mes préférences de partage |
| PATCH | `/health/sharing/{coach_id}` | Tout utilisateur | Mettre à jour le partage |
| GET | `/health/clients/{client_id}/logs` | Coach | Mesures partagées d'un client |
| GET | `/admin/health/parameters` | Admin | Liste tous les paramètres |
| POST | `/admin/health/parameters` | Admin | Ajouter un paramètre |
| PATCH | `/admin/health/parameters/{id}` | Admin | Modifier un paramètre |
| DELETE | `/admin/health/parameters/{id}` | Admin | Désactiver un paramètre |

---

## 29. Liens d'enrôlement coach

### 29.1 Vue d'ensemble
Un coach peut générer des liens d'enrôlement personnalisés à partager avec ses clients. Quand un nouveau client s'inscrit via ce lien, il est automatiquement associé au coach (coaching_relation créée sans étape manuelle).

### 29.2 Règles
- Chaque lien contient un token unique (cryptographiquement sécurisé, 64 chars)
- Le coach peut créer autant de liens qu'il veut (ex : un par groupe, un par campagne)
- Options disponibles par lien :
  - **Label** : ex "Groupe yoga janvier" (max 100 chars)
  - **Expiration** : date/heure après laquelle le lien ne fonctionne plus
  - **Max utilisations** : nb max de clients pouvant s'enrôler via ce lien
- Si le token est invalide/expiré/épuisé lors de l'inscription → l'inscription réussit quand même, juste sans association automatique
- Le coach peut désactiver un lien à tout moment

### 29.3 Format du lien
```
mycoach://enroll/{token}             ← Deep link app
https://mycoach.app/enroll/{token}   ← Lien web (futur)
```

### 29.4 Modèle de données — `coach_enrollment_tokens`
| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `coach_id` | UUID | FK → users.id CASCADE |
| `token` | VARCHAR(64) UNIQUE | Token sécurisé (urlsafe_b64) |
| `label` | VARCHAR(100) NULLABLE | Libellé du lien |
| `expires_at` | TIMESTAMPTZ NULLABLE | Expiration optionnelle |
| `max_uses` | INTEGER NULLABLE | Nb max d'utilisations (NULL=illimité) |
| `uses_count` | INTEGER | Nb d'utilisations effectives |
| `active` | BOOLEAN | Peut être désactivé manuellement |
| `created_at` | TIMESTAMPTZ | UTC |

### 29.5 API
| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| POST | `/coaches/me/enrollment-tokens` | Coach | Créer un lien d'enrôlement |
| GET | `/coaches/me/enrollment-tokens` | Coach | Lister ses liens |
| DELETE | `/coaches/me/enrollment-tokens/{id}` | Coach | Désactiver un lien |
| GET | `/enroll/{token}` | Public | Infos coach pré-inscription |
| POST | `/auth/register` | — | `enrollment_token` optionnel → association auto |

---

## CHANGELOG

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 25/02/2026 | Document initial — 24 modules complets |
| 1.1 | 25/02/2026 | SQLite → PostgreSQL 16 · JWT → API Key SHA-256 · Tarification (unitaire + forfaits) · Réservation client + annulation pénalité + liste d'attente |
| 1.2 | 25/02/2026 | i18n first : locale BCP 47 + pays ISO 3166-1 + devise ISO 4217 + unité poids + timezone sur tous les profils · Pays sur clubs · Chaînes internationales ajoutées |
| 1.3 | 25/02/2026 | Téléphone (E.164) sur Coach et Client · Jours de travail + horaires multi-créneaux sur Coach · Wizard minimaliste (1 seule étape obligatoire, "Terminer plus tard" dès étape 2) · Design responsive obligatoire · Bandeau de complétion de profil |
| 1.4 | 25/02/2026 | §7.4 Sélection en masse (vue Jour) · §7.5 Annulation en masse avec workflow complet (confirmation → choix message → aperçu SMS par client → récapitulatif) · §7.6 SMS en masse coach + historique SMS · Wizard coach : étape 7/7 Messages d'annulation (1 template maladie pré-rempli, jusqu'à 5 templates, variables {prénom}/{date}/{heure}/{coach}, drag-and-drop) |
| 1.5 | 26/02/2026 | §1.1 Prénom/Nom : max 50 → **max 150 chars** (noms internationaux) · Règle PII ajoutée : toutes les données personnelles chiffrées au repos (voir DEV_PATTERNS.md §1.9 + CODING_AGENT.md §5.1) |
| 1.6 | 26/02/2026 | §10.4 Architecture multi-participants : `sessions` sans `client_id` → table `session_participants` (statut/prix/annulation par client) · Tarif groupe : seuil N → prix/client réduit · Multi-coach : client peut avoir N coachs simultanément, données tracées par `coach_id` · Traçabilité consommation : table `package_consumptions` (Id_pack · Id_Payment · Id_Client · minutes · date planif · statut Consommé/Due/En attente) |
| 1.7 | 26/02/2026 | Décisions architecturales finales : Programme IA → `coach_id = NULL` + `source = 'ai'` · PRs → `is_pr = TRUE` sur `exercise_sets` (pas de table dédiée) + index partiel · Notation coach → Phase 2, aucun schéma anticipé |
| 1.8 | 26/02/2026 | Chiffrement tokens OAuth → Python Fernet applicatif avec clé dédiée `TOKEN_ENCRYPTION_KEY` (séparée de `FIELD_ENCRYPTION_KEY`) · `EncryptedToken` TypeDecorator distinct · 2 clés = 2 périmètres de compromission indépendants |
| 1.9 | 26/02/2026 | §25 Conformité RGPD ajouté : droits des utilisateurs (accès/portabilité/effacement/opposition), règles d'anonymisation J+30, table `consents` (log immuable), registre des traitements, durées de conservation, mesures techniques · `TASKS_BACKEND.md` : B6-02 → B6-07 (6 tâches RGPD détaillées), anciens B6-03→B6-06 renommés B6-08→B6-11 |
| 2.0 | 27/02/2026 | §26 Liens réseaux sociaux : coaches ET clients · liste évolutive (Instagram, TikTok, YouTube, LinkedIn, X, Facebook, Strava, site web) + liens custom (platform=NULL, label requis) · max 20 liens · visibilité par lien (public/coaches_only) · UPSERT standard, INSERT custom · DELETE/PUT par ID · Table user_social_links avec index partiel UNIQUE (user_id, platform) WHERE platform IS NOT NULL |
| 2.1 | 27/02/2026 | Blocklist domaines email : refus à l'inscription des adresses jetables (yopmail, mailinator…) · Table blocked_email_domains · seed ~55 domaines · admin CRUD /admin/blocked-domains · insensible à la casse · BlockedDomainError → HTTP 422 |
| 2.2 | 27/02/2026 | §0 Architecture des rôles : **Admin ⊇ Coach ⊇ Client** (hiérarchie inclusive) · `require_client` → tout utilisateur authentifié · `require_coach` → coach + admin · `require_admin` → admin uniquement · Un admin a accès à TOUT · Un coach a toutes les fonctionnalités client en plus des siennes |
| 2.3 | 27/02/2026 | §0.4 Matrice des accès : tableau complet de toutes les fonctionnalités × 3 rôles (client / coach / admin) — 70+ fonctionnalités documentées en 12 catégories |
| 2.4 | 27/02/2026 | §27 Suggestions & Bug Reports · §28 Paramètres de santé modulables + historique + partage par coach par paramètre |
| 2.5 | 27/02/2026 | §29 Liens d'enrôlement coach : token sécurisé (label / expiration / max_uses) · `/coaches/me/enrollment-tokens` CRUD · `/enroll/{token}` public · `enrollment_token` optionnel à l'inscription → coaching_relation auto · §0.4 Matrice Onboarding mise à jour |
| 3.0 | 27/02/2026 | Migration frontend Kotlin/Android → Flutter (Android + iOS + Web) · Riverpod + go_router + Dio · Scaffold projet frontend/ · TASKS_FLUTTER.md créé · DEV_ENVIRONMENT, DEV_ROADMAP, CODING_AGENT mis à jour |
| 3.1 | 27/02/2026 | **Téléphone coach obligatoire à l'inscription** — OTP SMS avant vérification email (nouveau flux Coach : inscription → OTP → email → onboarding) · **Téléphone client optionnel** (différable depuis profil) · **Genre affiché dès le formulaire d'inscription** (coach et client) · **§3 Gestion des salles** : client ET coach ont des salles (table `user_gym_favorites`) ; coach = salles de travail, client = salles favorites · **Matrice accès §0.4** : salles mises à ✅ pour Client + nouvelles lignes recherche salle · **`offers_discovery`** flag sur `coach_profile` : configurable dans tarifs, badge visible en recherche jusqu'à 1ère séance consommée · **Statuts créneaux clarifiés** : `mine` = `pending_coach_validation`, `booked` = occupé/bloqué · **Timer de repos par exercice** (`ExerciseDetailModal`) coexiste avec le temps global des programmes · **§22 Paramètres** : genre + téléphone + salles ajoutés profils coach et client · **§23.5 (nouveau)** Gestion profils coaches back-office + §23.6 renommé salles |

---

*Toute modification doit être validée par le product owner avant implémentation*
