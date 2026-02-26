# MyCoach — Flux Authentification

> Flux technico-fonctionnels entre l'application Android et le backend FastAPI.

---

## 1. Inscription (Email)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API
    participant E as Email Service

    U->>A: Saisit prénom, nom, email, password, accepte CGU
    A->>A: Validation temps réel (format email, force password)
    A->>B: POST /auth/register<br/>{first_name, last_name, email, password, role}
    alt Email déjà utilisé
        B-->>A: 409 Conflict<br/>{detail: "email_already_exists"}
        A-->>U: Message inline "Cette adresse email est déjà utilisée"
    else Succès
        B->>B: Hash bcrypt(password)<br/>Génère email_hash = SHA256(lower(email))<br/>Crée user (statut: unverified)
        B->>E: Envoie email de vérification (token 24h)
        B-->>A: 201 Created<br/>{user_id, email, role}
        A-->>U: Redirect → EmailVerificationScreen
    end
```

---

## 2. Vérification Email

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant L as Lien Email
    participant B as Backend API
    participant A as Android App

    U->>L: Clique sur le lien de vérification
    L->>B: GET /auth/verify-email?token=xxx
    alt Token valide
        B->>B: user.status = "verified"
        B-->>A: Deep link → mycoach://verify?success=true
        A-->>U: Redirect → OnboardingScreen (selon rôle)
    else Token expiré
        B-->>L: Page web "Lien expiré"
        L-->>U: Bouton "Renvoyer un nouveau lien"
    else Token invalide
        B-->>L: Page web "Lien invalide"
    end
```

---

## 3. Connexion (Email + Password)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant S as EncryptedSharedPrefs
    participant B as Backend API

    U->>A: Saisit email + password → "Se connecter"
    A->>B: POST /auth/login<br/>{email, password}

    alt Compte non vérifié
        B-->>A: 403 Forbidden<br/>{detail: "email_not_verified"}
        A-->>U: "Votre email n'est pas encore vérifié" + bouton Renvoyer
    else Mauvais credentials
        B-->>A: 401 Unauthorized<br/>{detail: "invalid_credentials"}
        A-->>U: "Email ou mot de passe incorrect"
    else 5 tentatives échouées
        B-->>A: 429 Too Many Requests<br/>{detail: "too_many_attempts", retry_after: 900}
        A-->>U: "Trop de tentatives, réessayez dans 15 min"
    else Succès
        B->>B: Vérifie bcrypt<br/>Génère API Key = SHA256(email+hash+salt)<br/>Stocke dans api_keys
        B-->>A: 200 OK<br/>{api_key: "abc123...", role: "coach|client"}
        A->>S: Stocke api_key (AES-256)
        A-->>U: Redirect → Dashboard (selon rôle)
    end
```

---

## 4. Connexion Google (OAuth2)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant G as Google SDK
    participant B as Backend API
    participant S as EncryptedSharedPrefs

    U->>A: Tap "Connexion avec Google"
    A->>G: Déclenche Google Sign-In
    G-->>A: Google ID Token (JWT)
    A->>B: POST /auth/google<br/>{id_token: "eyJ..."}
    B->>B: Vérifie signature via clés publiques Google<br/>Extrait: sub, email, name, picture
    alt Nouvel utilisateur
        B->>B: Crée user (statut: verified)<br/>Génère API Key = SHA256(sub+email+SECRET_SALT)
        B-->>A: 201 Created<br/>{api_key: "...", is_new: true}
        A->>S: Stocke api_key (AES-256)
        A-->>U: Redirect → RoleSelectionScreen (Coach ou Client ?)
    else Utilisateur existant
        B->>B: Récupère user existant<br/>Génère nouvelle API Key
        B-->>A: 200 OK<br/>{api_key: "...", role: "coach|client"}
        A->>S: Stocke api_key (AES-256)
        A-->>U: Redirect → Dashboard
    end
```

---

## 5. Auto-login au démarrage

```mermaid
sequenceDiagram
    participant A as Android App
    participant S as EncryptedSharedPrefs
    participant B as Backend API

    A->>S: Lecture api_key au démarrage
    alt API Key absente
        A-->>A: Redirect → LoginScreen
    else API Key présente
        A->>B: GET /auth/me<br/>Header: X-API-Key: abc123...
        alt Clé valide
            B-->>A: 200 OK<br/>{user_id, email, role, first_name, ...}
            A-->>A: Auto-login silencieux → Dashboard
        else Clé révoquée / expirée
            B-->>A: 401 Unauthorized
            A->>S: Supprime api_key
            A-->>A: Redirect → LoginScreen
        end
    end
```

---

## 6. Déconnexion

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant S as EncryptedSharedPrefs
    participant B as Backend API

    U->>A: Profil → "Se déconnecter" → Confirmation
    A->>B: DELETE /auth/logout<br/>Header: X-API-Key: abc123...
    B->>B: api_keys.revoked = TRUE
    B-->>A: 200 OK
    A->>S: Supprime api_key locale
    A-->>U: Redirect → LoginScreen

    note over U,B: Déconnexion tous appareils
    U->>A: "Déconnecter tous mes appareils"
    A->>B: DELETE /auth/logout-all<br/>Header: X-API-Key: abc123...
    B->>B: UPDATE api_keys SET revoked=TRUE<br/>WHERE user_id = ? (toutes les clés)
    B-->>A: 200 OK
    A->>S: Supprime api_key locale
    A-->>U: Redirect → LoginScreen
```

---

## 7. Réinitialisation du mot de passe

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant A as Android App
    participant B as Backend API
    participant E as Email Service

    U->>A: Saisit email → "Envoyer le lien"
    A->>B: POST /auth/forgot-password<br/>{email: "..."}
    B->>B: Cherche user (silencieux si non trouvé)
    B->>E: Envoie lien reset (token 1h) si email trouvé
    B-->>A: 200 OK (toujours, même si email inconnu)
    A-->>U: "Si cet email existe, un lien vous a été envoyé"

    U->>A: Clique sur le lien → saisit nouveau password
    A->>B: POST /auth/reset-password<br/>{token: "xxx", new_password: "..."}
    alt Token valide
        B->>B: Hash bcrypt(new_password)<br/>Révoque tous les tokens actifs
        B-->>A: 200 OK
        A-->>U: Toast "Mot de passe modifié" → LoginScreen
    else Token expiré / invalide
        B-->>A: 400 Bad Request
        A-->>U: "Lien invalide ou expiré"
    end
```

---

## 8. Schéma général de l'authentification

```mermaid
flowchart TD
    START([Démarrage App]) --> CHECK{API Key en<br/>EncryptedSharedPrefs ?}
    CHECK -->|Non| LOGIN[LoginScreen]
    CHECK -->|Oui| VERIFY[GET /auth/me]
    VERIFY -->|200 OK| DASH[Dashboard]
    VERIFY -->|401| LOGIN

    LOGIN --> EMAIL_LOGIN[Email + Password]
    LOGIN --> GOOGLE[Google Sign-In]
    LOGIN --> REGISTER[Inscription]

    EMAIL_LOGIN --> POST_LOGIN[POST /auth/login]
    GOOGLE --> POST_GOOGLE[POST /auth/google]
    REGISTER --> POST_REGISTER[POST /auth/register]

    POST_LOGIN -->|Succès| STORE[Stocke API Key<br/>EncryptedSharedPrefs AES-256]
    POST_GOOGLE -->|Succès| STORE
    POST_REGISTER -->|Succès| EMAIL_VERIF[Vérification Email]
    EMAIL_VERIF -->|Token vérifié| STORE

    STORE --> DASH

    DASH --> ALL_REQUESTS[Toutes les requêtes API]
    ALL_REQUESTS --> HEADER["Header: X-API-Key: SHA256(...)"]
    HEADER -->|401| LOGIN
```
