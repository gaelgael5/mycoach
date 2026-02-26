# MyCoach — Flux Intégrations & RGPD

> Flux technico-fonctionnels entre l'application Android et le backend FastAPI.

---

## 1. Connexion Google Calendar (OAuth2)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API
    participant G as Google OAuth

    U->>A: Profil → Intégrations → "Connecter Google Calendar"
    A->>B: GET /integrations/google-calendar/auth-url
    B-->>A: {auth_url: "https://accounts.google.com/o/oauth2/auth?...scope=calendar.events"}
    A->>G: Ouvre WebView avec auth_url
    U->>G: Approuve les permissions
    G-->>A: Redirect avec code=AUTH_CODE

    A->>B: POST /integrations/google-calendar/callback<br/>{code: "AUTH_CODE"}
    B->>G: Échange code → access_token + refresh_token
    B->>B: Chiffre tokens avec Fernet (TOKEN_ENCRYPTION_KEY)<br/>Stocke dans oauth_tokens
    B-->>A: 200 OK {connected: true}
    A-->>U: "Google Calendar connecté ✓"

    note over B: Synchronisation automatique à chaque changement de statut
    B->>G: Crée événement GCal (séance confirmée)<br/>Titre: "Séance avec [Coach/Client]"<br/>Lieu: [salle]
    G-->>B: {event_id}
    B->>B: Stocke event_id pour les mises à jour futures

    note over B: Annulation d'une séance
    B->>G: DELETE /calendar/v3/calendars/primary/events/{event_id}
    G-->>B: 204 No Content
```

---

## 2. Connexion Strava (OAuth2)

```mermaid
sequenceDiagram
    actor C as Client
    participant A as Android App
    participant B as Backend API
    participant S as Strava API

    C->>A: Profil → Intégrations → "Connecter Strava"
    A->>B: GET /integrations/strava/auth-url
    B-->>A: {auth_url: "https://www.strava.com/oauth/authorize?...scope=activity:write,read"}
    A->>S: Ouvre WebView
    C->>S: Approuve
    S-->>A: code=AUTH_CODE

    A->>B: POST /integrations/strava/callback<br/>{code: "AUTH_CODE"}
    B->>S: Échange code → {access_token, refresh_token, expires_at}
    B->>B: Chiffre access_token + refresh_token (Fernet IV aléatoire)<br/>Stocke expires_at en clair
    B-->>A: 200 OK {connected: true}
    A-->>C: "Strava connecté ✓"

    note over B: Push séance vers Strava
    B->>B: Déchiffre access_token<br/>Si expiré → refresh via refresh_token
    B->>S: POST /api/v3/activities<br/>{name, type, start_date, elapsed_time, description}
    S-->>B: {activity_id, url}
    B-->>A: {strava_activity_url}

    note over B: Import activités Strava (optionnel)
    B->>S: GET /api/v3/athlete/activities (nouvelles seulement)
    S-->>B: [{strava_id, type, start_date, elapsed_time}]
    B->>B: Crée workout_sessions avec source="strava" (lecture seule)
```

---

## 3. Balance connectée Withings (OAuth2)

```mermaid
sequenceDiagram
    actor C as Client
    participant A as Android App
    participant B as Backend API
    participant W as Withings API

    C->>A: Profil → Intégrations → "Connecter ma balance"
    A->>B: GET /integrations/withings/auth-url
    B-->>A: {auth_url: "https://account.withings.com/oauth2_user/..."}
    A->>W: Ouvre WebView
    C->>W: Approuve
    W-->>A: code=AUTH_CODE

    A->>B: POST /integrations/withings/callback<br/>{code: "AUTH_CODE"}
    B->>W: Échange code → tokens
    B->>B: Chiffre + stocke tokens (Fernet)
    B-->>A: 200 OK

    note over B: Import des mesures (tâche périodique ou déclenchée manuellement)
    B->>W: GET /v2/measure?meastype=1 (poids)
    W-->>B: [{date, weight_kg}]
    B->>B: Upsert dans body_measurements<br/>Recalcule IMC si taille connue
    B-->>A: {measurements_imported: N}
    A-->>C: Graphique courbe poids mis à jour
```

---

## 4. Architecture de chiffrement des tokens OAuth

```mermaid
flowchart LR
    subgraph Android
        A[ApiKeyInterceptor<br/>X-API-Key header]
    end

    subgraph Backend
        B[oauth_tokens table]
        F[Fernet AES-128\nTOKEN_ENCRYPTION_KEY]
        B -- chiffré --> F
        F -- déchiffré --> EX[External API calls]
    end

    subgraph External
        GC[Google Calendar API]
        ST[Strava API]
        WI[Withings API]
    end

    A --> B
    EX --> GC
    EX --> ST
    EX --> WI

    note1[IV aléatoire Fernet :\n2 chiffrements du même token\n→ ciphertexts différents\n✅ Non déterministe]
```

---

## 5. RGPD — Export des données utilisateur

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API

    U->>A: Profil → "Exporter mes données"
    A-->>U: Choix format : JSON ou CSV
    U->>A: Sélectionne format → "Demander l'export"
    A->>B: POST /users/me/export<br/>{format: "json|csv"}
    B->>B: Génère token HMAC SHA-256<br/>Payload: {user_id}:{fmt}:{expires_unix}:{sig}<br/>Valide 24h, téléchargeable sans API Key
    B-->>A: {download_url: "/users/me/export?token=xxx"}
    A-->>U: "Lien de téléchargement valable 24h"

    U->>A: Tap sur le lien
    A->>B: GET /users/me/export?token=xxx
    B->>B: Vérifie HMAC + expiration<br/>Génère export : profil, séances, performances, paiements, consentements
    B-->>A: Fichier JSON ou CSV (PII déchiffrées à la volée)
    A-->>U: Téléchargement démarré
```

---

## 6. RGPD — Suppression du compte

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API
    participant E as Email Service

    U->>A: Profil → "Supprimer mon compte"
    A-->>U: Modale : "Votre compte sera définitivement supprimé dans 30 jours.<br/>Vous pouvez annuler depuis l'email de confirmation."
    U->>A: Confirme
    A->>B: DELETE /users/me
    B->>B: user.deletion_requested_at = now()<br/>user.status = "pending_deletion"
    B->>E: Email confirmation avec lien d'annulation
    B-->>A: 200 OK
    A-->>U: "Demande prise en compte. Email de confirmation envoyé."

    note over B: Après 30 jours (tâche planifiée)
    B->>B: Anonymise les données PII :<br/>first_name = "Utilisateur"<br/>last_name = "Supprimé"<br/>email_hash = NULL<br/>Supprime oauth_tokens, api_keys<br/>Conserve statistiques anonymisées
```

---

## 7. RGPD — Gestion des consentements

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API

    note over U,B: Premier lancement — acceptation des CGU
    U->>A: Coche "J'accepte les CGU et la politique de confidentialité"
    A->>B: POST /consents<br/>{type: "terms_of_service", accepted: true, version: "1.0"}
    B->>B: Crée ligne immuable dans consents<br/>(pas d'UPDATE/DELETE — chaque action = nouvelle ligne)<br/>Stocke ip_hash = SHA256(IP), ua_hash = SHA256(UserAgent)
    B-->>A: 201 Created

    note over U,B: Retrait d'un consentement
    U->>A: Profil → Confidentialité → désactive "Emails marketing"
    A->>B: POST /consents<br/>{type: "marketing_emails", accepted: false}
    B->>B: Nouvelle ligne avec accepted=false<br/>Le dernier consentement par type fait foi
    B-->>A: 201 Created

    note over U,B: Consultation de l'historique
    A->>B: GET /consents/me
    B-->>A: [{type, accepted, created_at, version}] (toutes les lignes)
    A-->>U: Historique des consentements
```

---

## 8. Headers de sécurité (middleware)

```mermaid
flowchart TD
    REQ[Requête Android<br/>GET|POST|PATCH|DELETE] --> MW[ASGI Security Middleware]

    MW --> H1[X-Content-Type-Options: nosniff]
    MW --> H2[X-Frame-Options: DENY]
    MW --> H3[X-XSS-Protection: 1; mode=block]
    MW --> H4[Referrer-Policy: strict-origin-when-cross-origin]
    MW --> H5[Cache-Control: no-store<br/>sur les routes /auth/*]

    H1 & H2 & H3 & H4 & H5 --> RESP[Réponse au client]

    note1[Server: header supprimé\npour ne pas révéler la stack technique]
    RESP --> note1
```
