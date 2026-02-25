# MyCoach — Cahier des charges fonctionnel DÉTAILLÉ v1.0

> Document de référence complet. Chaque module décrit les écrans, actions, validations, règles métier, cas d'erreur et notifications.

---

## 🌍 INTERNATIONALISATION (i18n) — PRINCIPES FONDATEURS

L'application est **internationale dès le premier commit**. Ces règles s'appliquent à toutes les phases de développement, sans exception.

### Règles de développement (non négociables)
- **Zéro texte codé en dur** dans le code (Android ou Backend) — tout passe par les fichiers de ressources
- **Android :** `res/values/strings.xml` (défaut) + `res/values-fr/strings.xml`, `res/values-en/strings.xml`, etc.
- **Backend :** Répertoire `locales/` avec fichiers JSON par langue (`fr.json`, `en.json`, `es.json`…) — messages d'erreur, notifications, emails
- **Dates :** toujours stockées en UTC en base, converties en affichage selon `user.timezone`
- **Devises :** stockées en centimes (entier) + code ISO 4217 (`EUR`, `USD`, `GBP`…), jamais en float
- **Poids :** stockés en kg en base, affichés selon `user.weight_unit` (kg ou lb) avec conversion automatique
- **Numéros de téléphone :** format E.164 (`+33612345678`)
- **Codes pays :** ISO 3166-1 alpha-2 (`FR`, `BE`, `US`, `GB`…)
- **Codes langue/culture :** BCP 47 (`fr-FR`, `en-US`, `es-ES`, `pt-BR`…)

### Sélection de la culture (utilisateur)
- Détectée automatiquement depuis la locale système de l'appareil (Android : `Locale.getDefault()`)
- Modifiable dans Profil → Préférences → Langue
- Persistée en base (`user.locale`) → synchronisée sur tous les appareils
- Tout changement → rechargement de l'UI sans redémarrage (Android : `recreate()`)

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

## 🔐 DÉCISIONS TECHNIQUES ARRÊTÉES

| Composant | Choix | Notes |
|-----------|-------|-------|
| SGBD | **PostgreSQL 16** | Docker, multi-users, MVCC |
| ORM | SQLAlchemy 2 async + asyncpg | Driver natif async |
| Migrations | Alembic | Versionning schéma |
| Auth API | **API Key SHA-256** | `X-API-Key` header sur tous les appels |
| Auth Google | ID Token → `POST /auth/google` → API Key maison | 1 vérif Google puis lookup local |
| Auth email | bcrypt credentials → API Key maison | Même système unifié |
| Stockage Android | EncryptedSharedPreferences (AES-256) | Jamais en clair |
| Révocation | `revoked = TRUE` en base | Multi-device, immédiat |
| Tarification | Séance unitaire + forfaits (N séances, prix, validité) | Configurable par coach |
| Annulation | Pénalité si < délai configuré (défaut 24h) | Séance due au coach |
| Liste d'attente | File FIFO, fenêtre 30 min par candidat | Automatique à chaque libération |
| **i18n** | **BCP 47 locale par utilisateur (fr-FR, en-US…)** | Zéro texte codé en dur |
| Pays | ISO 3166-1 alpha-2 (FR, BE, US…) | Sur clubs, profils, devises |
| Devises | ISO 4217 (EUR, USD, GBP…) stockées en centimes | Jamais de float pour les montants |
| Dates | UTC en base, converti selon user.timezone | Pas de décalage horaire surprenant |
| Poids | Stocké kg, affiché kg ou lb selon préférence | Conversion automatique |

---

## 1. AUTHENTIFICATION

### 1.1 Inscription Coach
**Écran :** `RegisterScreen` (rôle = Coach)

**Champs :**
- Prénom (obligatoire, min 2 chars, max 50 chars)
- Nom (obligatoire, min 2 chars, max 50 chars)
- Email (obligatoire, format RFC5322, unicité vérifiée côté serveur)
- Mot de passe (obligatoire, min 8 chars, au moins 1 majuscule, 1 chiffre, 1 caractère spécial)
- Confirmation mot de passe (doit être identique)
- Pays (sélecteur ISO 3166-1, pré-sélectionné depuis la locale système)
- Langue / Culture (pré-sélectionnée depuis la locale système, ex: `fr-FR`) — modifiable
- Case "J'accepte les CGU" (obligatoire)

**Validations en temps réel :**
- Email : vérification format à la sortie du champ
- Password strength indicator (faible / moyen / fort)
- Confirm password : comparaison en temps réel

**Action "S'inscrire" :**
- Disabled tant que tous les champs ne sont pas valides
- Tap → loader → appel API `POST /auth/register`
- Succès → création compte (statut `unverified`) → envoi email de vérification → redirect `EmailVerificationScreen`
- Erreur email déjà utilisé → message inline sous le champ : "Cette adresse email est déjà utilisée"
- Erreur serveur → toast : "Erreur lors de l'inscription, veuillez réessayer"

**Écran EmailVerificationScreen :**
- Message : "Un email a été envoyé à [email]"
- Bouton "Renvoyer l'email" (cooldown 60s entre chaque envoi, compteur visible)
- Lien "Mauvais email ? → Retour à l'inscription"
- Durée de validité du lien : 24h

**Clic sur le lien email :**
- Token vérifié côté serveur → compte activé → deep link → app ouverte
- Si token expiré → page web d'erreur avec bouton "Renvoyer un nouveau lien"
- Si token invalide → message "Lien invalide"
- Succès → redirect `CoachOnboardingScreen` (étape 1/5)

---

### 1.2 Inscription Client
Identique à 1.1 avec rôle = Client.
Après vérification email → redirect `ClientOnboardingScreen` (questionnaire, étape 1/6)

---

### 1.3 Connexion
**Écran :** `LoginScreen`

**Champs :**
- Email
- Mot de passe (toggle afficher/masquer)

**Actions :**
- "Se connecter" → `POST /auth/login` → vérif bcrypt → génère `SHA256(email+hash+salt)` → `{ "api_key": "..." }` → stocké en `EncryptedSharedPreferences` → redirect selon rôle
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
- Au lancement → lecture API Key depuis `EncryptedSharedPreferences`
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
- Suppression locale de l'API Key (`EncryptedSharedPreferences`)
- Redirect `LoginScreen`

**Déconnexion tous les appareils :**
- Profil → "Déconnecter tous mes appareils"
- `DELETE /auth/logout-all` → `revoked = TRUE` sur toutes les clés de l'utilisateur
- Cas d'usage : appareil perdu, suspicion de compromission

---

## 2. ONBOARDING CLIENT (questionnaire)

### Écran 1/6 — Objectif principal
- Titre : "Quel est votre objectif ?"
- Choix unique (cards sélectionnables) :
  - 🔥 Perte de poids
  - 💪 Prise de masse musculaire
  - 🏃 Endurance / Cardio
  - 🌿 Remise en forme générale
  - 🏆 Performance sportive
  - ✨ Autre (champ texte libre activé)
- Bouton "Suivant" (disabled si rien sélectionné)
- Indicateur de progression (1/6)
- Bouton "Passer" (les données sont optionnelles, programme moins personnalisé)

### Écran 2/6 — Niveau sportif
- Titre : "Quel est votre niveau ?"
- Choix unique :
  - 🌱 Débutant — Je m'entraîne depuis moins de 6 mois
  - 🌿 Intermédiaire — 6 mois à 2 ans de pratique
  - 🌳 Confirmé — Plus de 2 ans, je connais les exercices
- Bouton "Précédent" / "Suivant"

### Écran 3/6 — Fréquence
- Titre : "À quelle fréquence voulez-vous vous entraîner ?"
- Stepper : 1 à 7 séances / semaine (défaut = 3)
- Sélecteur durée préférée : 30 min / 45 min / 60 min / 90 min

### Écran 4/6 — Équipements
- Titre : "Quel équipement avez-vous à disposition ?"
- Multi-sélection :
  - 🏋️ Salle de sport complète (machines + poids libres)
  - 🚲 Salle cardio uniquement
  - 🏠 Home gym (équipement maison)
  - 🏋️ Poids libres uniquement (haltères / barres)
  - 🤸 Aucun équipement (poids du corps)

### Écran 5/6 — Zones à travailler
- Titre : "Quelles zones voulez-vous cibler ?"
- Multi-sélection :
  - Épaules / Pectoraux / Dos / Biceps / Triceps
  - Abdominaux / Lombaires / Fessiers
  - Quadriceps / Ischio-jambiers / Mollets
  - Corps entier (désactive les autres)

### Écran 6/6 — Blessures
- Titre : "Avez-vous des blessures ou contre-indications ?"
- Toggle "Oui / Non"
- Si Oui → multi-select zones : Dos / Genou / Épaule / Poignet / Cheville / Hanche / Cou / Autre
- Zone texte libre : "Précisez si nécessaire (optionnel)"
- Bouton "Terminer" → `POST /clients/questionnaire` → redirect `ClientDashboard`

---

## 3. ONBOARDING COACH (setup profil)

### Écran 1/5 — Informations de base
**Champs :**
- Photo de profil (obligatoire)
  - Tap → choix : Appareil photo / Galerie
  - Validation : min 200×200px, max 5 MB, formats jpg/png/webp
  - Recadrage circulaire proposé après sélection
- Prénom / Nom (pré-remplis, modifiables)
- Date de naissance (optionnel, datepicker, adulte requis ≥ 18 ans)
- Biographie (obligatoire, min 100 chars, max 500 chars)
  - Compteur de caractères visible en temps réel
  - Placeholder : "Présentez votre approche, votre méthode, votre parcours..."

### Écran 2/5 — Spécialités
**Multi-sélection (min 1) :**
- Musculation / Cardio / HIIT / Yoga / Pilates / CrossFit / Boxe / Running / Triathlon / Natation / Cyclisme / Nutrition sportive / Préparation mentale / Rééducation / Stretching / Autre

### Écran 3/5 — Certifications
- Liste initialement vide
- Bouton "+ Ajouter une certification" → mini-formulaire :
  - Nom de la certification (ex: BPJEPS, Personal Trainer ISSA...)
  - Organisme (texte libre)
  - Année d'obtention (sélecteur, max = année en cours)
  - Photo du document (optionnel) → upload → flag `pending_verification`
- Chaque certification affichée en carte avec statut : "En attente de vérification" / "Certifié ✓"
- Tap sur une carte → modifier ou supprimer
- Peut passer l'étape → certifications ajoutables plus tard depuis le profil

### Écran 4/5 — Salles de sport
**Flux de sélection :**
1. Sélection de la chaîne (dropdown : Fitness Park, Basic-Fit, etc.)
2. Recherche par ville, CP ou nom de club
3. Résultats en liste → tap pour sélectionner
4. Club ajouté aux sélections (chips en haut, supprimable avec ×)
5. Répéter pour d'autres chaînes
- Min 1 club requis

### Écran 5/5 — Tarifs & disponibilités
**Tarifs :**
- Devise (pré-sélectionnée depuis le pays du coach, modifiable) : EUR / USD / GBP / CHF / CAD / BRL / AUD…
- Tarif séance unitaire (montant, obligatoire, min 1 dans la devise choisie)
- Forfaits (ajout dynamique de lignes) :
  - Nom du forfait (ex : "Pack 10 séances", "Mensuel")
  - Nb séances + Prix total → prix unitaire calculé et affiché automatiquement
  - Durée de validité : 1 mois / 2 mois / 3 mois / 6 mois / Sans limite
  - Visible publiquement : oui / non
- Séance découverte : toggle "Proposer une séance découverte"
  - Si oui : Gratuite / Payante (saisir le tarif)
  - Durée de la découverte : 30 / 45 / 60 min
- Durée standard d'une séance : 30 / 45 / 60 / 90 min

**Disponibilités récurrentes :**
- Pour chaque jour de la semaine : toggle actif/inactif
- Si actif : heure de début → heure de fin (plages de 30 min)
- Plusieurs plages par jour possibles (bouton "+ Ajouter une plage")
- Nb de places max par créneau (défaut = 1, max = 20 pour group coaching)
- Horizon de réservation : 1 semaine / 2 semaines / 1 mois

**Bouton "Publier mon profil" → `POST /coaches/profile` → redirect `CoachDashboard`**

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
- Client (dropdown, clients actifs)
- Type : Découverte / Encadrée
- Date (datepicker, min = aujourd'hui + 1h)
- Heure de début (time picker, par tranche de 15 min)
- Durée (30 / 45 / 60 / 90 min)
- Salle (parmi les salles du coach)
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

## 8. RÉSERVATION PAR LE CLIENT

### 8.1 Calendrier de disponibilités du coach
**Accès :** Fiche coach → onglet "Réserver"
- Vue semaine avec navigation avant/arrière
- Limite : ne peut pas réserver au-delà de l'horizon configuré par le coach
- Chaque créneau affiché :
  - 🟢 Disponible : tap pour réserver
  - 🟠 Dernière place (1 place restante) : tap pour réserver + avertissement
  - 🔴 Complet : tap → `WaitlistJoinModal`
  - ⬛ Non disponible (passé ou bloqué)
  - 🟡 Déjà réservé par le client : non cliquable, indicateur "Votre séance"

### 8.2 Confirmation de réservation
**Modal :**
- Récapitulatif : coach, date, heure, durée, salle, tarif unitaire
- Message optionnel pour le coach (max 300 chars, placeholder : "Précisez votre objectif pour cette séance...")
- Bouton "Confirmer" → `POST /bookings` → statut `pending_coach_validation`
- Notifications :
  - Client : "Réservation envoyée — en attente de validation ⏳"
  - Coach : "Nouvelle réservation de [Client] pour le [date] à [heure]"
- Timer côté coach : 24h pour valider → si dépassé → auto-rejet + notif client + libération créneau

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

---

## 11. PROFIL & RECHERCHE COACH (côté Client)

### 11.1 Écran de recherche
**Barre de recherche :** nom ou spécialité (recherche fulltext)
**Filtres (drawer latéral ou chips sous la barre) :**
- Chaîne de salle (multi-select)
- Club spécifique (dépend de la chaîne sélectionnée)
- Spécialité (multi-select)
- Tarif max (slider 20€–200€, par incrément de 5€)
- Séance découverte gratuite (toggle)
- Badge "Certifié ✓" (toggle)
- Disponible cette semaine (toggle)

**Résultats :**
- Liste (défaut) ou grille (switch)
- Chaque card : photo, nom, spécialités (3 max avec badge overflow "+2"), tarif/séance, note (si disponible), badge certifié
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
  - "Demander une séance découverte" si disponible et pas encore en relation
  - "Réserver une séance" si déjà en relation active
  - "Demande en cours" (grisé) si demande déjà envoyée
  - "Votre coach" (grisé) si relation active

### 11.3 Demande de découverte
- Tap "Demander une séance découverte"
- Modal :
  - Info : tarif de la découverte (gratuite ou payante selon config coach)
  - Message optionnel pour le coach (placeholder : "Parlez-lui de vos objectifs...")
  - Bouton "Envoyer la demande"
- → Statut `pending` → notif coach → notif client "Demande envoyée ✓"
- Client peut annuler la demande tant que le coach n'a pas répondu (bouton dans onglet "Mes coachs")

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
  - Swipe gauche sur une série → bouton rouge "Supprimer"
  - Bouton "+ Ajouter une série" (copie valeurs de la dernière série par défaut)
- Note sur cet exercice (texte libre, max 200 chars)
- Bouton "Valider" → retour à `WorkoutSessionScreen`

**Validations :**
- Reps : min 1, max 999, entier
- Poids : min 0 (corps du corps), max 999, décimale possible (ex: 22.5 kg)
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

### 20.1 Définition des forfaits (coach)
**Profil coach → "Mes forfaits" :**
- Forfaits prédéfinis (modifiables à tout moment) :
  - Nom (ex: "Pack 10 séances"), nb séances, prix total, prix unitaire (calculé)
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
- **Pays** (ISO 3166-1 — affecte la devise par défaut et le filtrage des salles)
- **Langue / Culture** (BCP 47 : `fr-FR`, `en-US`, `es-ES`… — change l'UI immédiatement)
- **Devise** (ISO 4217 : EUR, USD, GBP… — appliquée à tous les tarifs)
- Spécialités (ajout/suppression)
- Certifications (ajout/suppression/modification)
- Salles (ajout/suppression, filtrées par pays)
- Tarifs et forfaits
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
- **Pays** (ISO 3166-1 — affecte les salles disponibles et la devise affichée)
- **Langue / Culture** (BCP 47 — change l'UI immédiatement)
- **Unité de poids** (kg / lb — affecte l'affichage des perfs et de la balance)
- Fuseau horaire (auto-détecté, modifiable — affecte l'affichage des horaires de séances)
- Refaire le questionnaire (objectif, fréquence, équipement)
- Salles fréquentées (filtrées par pays)
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
- KPIs : Coachs actifs / Clients actifs / Séances ce mois / Machines en attente de modération / Vidéos en génération
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

### 23.5 Gestion du répertoire salles
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

## CHANGELOG

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | 25/02/2026 | Document initial — 24 modules complets |
| 1.1 | 25/02/2026 | SQLite → PostgreSQL 16 · JWT → API Key SHA-256 · Tarification (unitaire + forfaits) · Réservation client + annulation pénalité + liste d'attente |
| 1.2 | 25/02/2026 | i18n first : locale BCP 47 + pays ISO 3166-1 + devise ISO 4217 + unité poids + timezone sur tous les profils · Pays sur clubs · Chaînes internationales ajoutées |

---

*Toute modification doit être validée par le product owner avant implémentation*
