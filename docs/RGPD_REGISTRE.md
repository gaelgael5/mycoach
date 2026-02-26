# Registre des Traitements RGPD — MyCoach

> Article 30 RGPD — Tenu par le responsable de traitement.
> Mise à jour : 2026-02-26 | Version : 1.0

---

## 1. Identité du Responsable de Traitement

| Champ | Valeur |
|-------|--------|
| **Société** | MyCoach SAS (à compléter) |
| **Adresse** | À compléter |
| **Email DPO** | dpo@mycoach.app (à désigner) |
| **Représentant EU** | Même entité |

---

## 2. Traitements et Finalités

### 2.1 Gestion des comptes utilisateurs

| Champ | Détail |
|-------|--------|
| **Finalité** | Création et gestion de comptes (coach / client) |
| **Base légale** | Art. 6(1)(b) — Exécution d'un contrat |
| **Données traitées** | Prénom, nom, email, téléphone, rôle, timezone, locale |
| **Chiffrement** | Fernet AES-128 (prénom, nom, email, téléphone) |
| **Durée conservation** | Durée du contrat + 3 ans (prescription) |
| **Sous-traitants** | PostgreSQL (auto-hébergé), Render/Hetzner (infrastructure) |
| **Transfert hors UE** | Non (infrastructure EU) |

### 2.2 Réservations et séances

| Champ | Détail |
|-------|--------|
| **Finalité** | Gestion des réservations coach-client, suivi des séances |
| **Base légale** | Art. 6(1)(b) — Exécution d'un contrat |
| **Données traitées** | Dates/heures de réservation, statut, gym, durée |
| **Durée conservation** | 5 ans (données comptables) |
| **Sous-traitants** | Twilio (SMS de confirmation / rappel) |
| **Transfert hors UE** | Twilio — États-Unis (Clauses contractuelles types) |

### 2.3 Paiements

| Champ | Détail |
|-------|--------|
| **Finalité** | Facturation des séances et abonnements |
| **Base légale** | Art. 6(1)(b) + Art. 6(1)(c) — Obligation légale (comptabilité) |
| **Données traitées** | Montant (centimes), devise, statut, référence |
| **Durée conservation** | 10 ans (obligation comptable, L123-22 Code de Commerce) |
| **Sous-traitants** | Stripe (à intégrer) |
| **Transfert hors UE** | Stripe — États-Unis (Clauses contractuelles types) |

### 2.4 Données de santé (mesures corporelles)

| Champ | Détail |
|-------|--------|
| **Finalité** | Suivi progression physique (poids, composition corporelle) |
| **Base légale** | Art. 9(2)(a) — Consentement explicite |
| **Données traitées** | Poids, IMC, % graisse, % muscle, masse osseuse, % eau |
| **Durée conservation** | Jusqu'à suppression du compte + 30 jours |
| **Sous-traitants** | Withings (import optionnel, OAuth) |
| **Transfert hors UE** | Withings — France (données stockées EU) |
| **Consentement** | `POST /users/me/consents` type=`third_party_sharing` |

### 2.5 Activités sportives (Strava)

| Champ | Détail |
|-------|--------|
| **Finalité** | Synchronisation séances avec Strava (optionnel) |
| **Base légale** | Art. 6(1)(a) — Consentement |
| **Données traitées** | Token OAuth chiffré, type d'activité, date |
| **Durée conservation** | Jusqu'à déconnexion Strava |
| **Sous-traitants** | Strava Inc. (États-Unis) |
| **Transfert hors UE** | Strava — États-Unis (Clauses contractuelles types) |
| **Consentement** | `POST /users/me/consents` type=`third_party_sharing` |

### 2.6 Google Calendar

| Champ | Détail |
|-------|--------|
| **Finalité** | Synchronisation réservations dans le calendrier Google (optionnel) |
| **Base légale** | Art. 6(1)(a) — Consentement |
| **Données traitées** | Token OAuth chiffré, titres et dates des événements |
| **Durée conservation** | Jusqu'à déconnexion Google Calendar |
| **Sous-traitants** | Google LLC (États-Unis) |
| **Transfert hors UE** | Clauses contractuelles types (Google EU) |

### 2.7 Consentements et registre

| Champ | Détail |
|-------|--------|
| **Finalité** | Preuve de recueil du consentement (RGPD Art. 7(1)) |
| **Base légale** | Art. 6(1)(c) — Obligation légale |
| **Données traitées** | Type, version, IP hashée (SHA-256), User-Agent hashé, date |
| **Durée conservation** | 5 ans après retrait du consentement |
| **Sous-traitants** | Aucun |

### 2.8 Authentification Google

| Champ | Détail |
|-------|--------|
| **Finalité** | Connexion via compte Google (SSO) |
| **Base légale** | Art. 6(1)(b) — Exécution d'un contrat |
| **Données traitées** | Google ID Token (vérifié, non stocké), email |
| **Durée conservation** | Token non stocké, uniquement email utilisé |
| **Sous-traitants** | Google LLC |

---

## 3. Droits des Personnes

| Droit | Endpoint | Délai de réponse |
|-------|----------|-----------------|
| **Accès (Art. 15)** | `GET /users/me/export?format=json` | Immédiat |
| **Portabilité (Art. 20)** | `GET /users/me/export?format=csv` | Immédiat |
| **Effacement (Art. 17)** | `DELETE /users/me` | J+30 (anonymisation) |
| **Rectification (Art. 16)** | `PUT /users/me` | Immédiat |
| **Opposition (Art. 21)** | `POST /users/me/consents` (accepted=false) | Immédiat |
| **Limitation (Art. 18)** | Contact DPO | 30 jours |

---

## 4. Mesures de Sécurité

| Mesure | Implémentation |
|--------|---------------|
| Chiffrement PII | Fernet AES-128 (`FIELD_ENCRYPTION_KEY`) |
| Chiffrement tokens OAuth | Fernet AES-128 (`TOKEN_ENCRYPTION_KEY`) |
| Hash email (recherche) | SHA-256 (non réversible) |
| Hash IP/UA (consentements) | SHA-256 (non réversible) |
| Transport | TLS 1.2+ (HSTS en production) |
| Headers HTTP | X-Content-Type-Options, X-Frame-Options, CSP |
| Rate limiting | 10 req/min login, 5 req/min register (slowapi) |
| Authentification | API Key SHA-256 (64 hex chars), rotation supportée |
| Accès DB | Utilisateur PostgreSQL dédié, pas de superuser |

---

## 5. Sous-traitants

| Sous-traitant | Pays | Traitement | Garanties |
|---------------|------|------------|-----------|
| Twilio | US | SMS | CCT + DPA |
| Stripe | US | Paiements | CCT + DPA |
| Google | US | OAuth, Calendar | CCT + DPA |
| Strava | US | Activités sportives | CCT |
| Withings | FR | Mesures balance | RGPD natif |
| Hetzner/OVH | EU | Infrastructure | RGPD natif |

---

## 6. Révisions

| Date | Version | Modifications |
|------|---------|---------------|
| 2026-02-26 | 1.0 | Création initiale |
