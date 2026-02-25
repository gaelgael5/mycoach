# MyCoach — Environnement de Développement

> Version : 1.0 — 2026-02-25
> Auteur : Tom ⚡

Ce document décrit l'environnement de développement recommandé pour les deux composantes de MyCoach :
- **Backend** : Python 3.12 + FastAPI + PostgreSQL 16
- **Android** : Kotlin 1.9 + Android SDK 34

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Environnement commun](#2-environnement-commun)
3. [Backend Python — Setup](#3-backend-python--setup)
4. [Android Kotlin — Setup](#4-android-kotlin--setup)
5. [VSCode — Configuration recommandée](#5-vscode--configuration-recommandée)
6. [Workflows de build locaux](#6-workflows-de-build-locaux)
7. [CI/CD AppVeyor](#7-cicd-appveyor)
8. [Déploiement — Vue d'ensemble](#8-déploiement--vue-densemble)

---

## 1. Vue d'ensemble

```
mycoach/
├── backend/              ← Python/FastAPI (source principale)
├── android/              ← App Kotlin/Android
├── docs/                 ← Documentation (ce fichier, specs, tâches…)
├── deploy/               ← Fichiers de déploiement (Compose, Nginx, scripts)
│   ├── docker-compose.yml
│   ├── nginx/
│   └── scripts/
├── appveyor.yml          ← CI/CD backend (Python → Docker Hub)
└── android/appveyor.yml  ← CI/CD Android (APK → Artifacts)
```

**Flux de développement :**
```
Code local (VSCode)
    → git push → GitHub
        → AppVeyor CI → Tests + Build
            → Docker Hub (backend) / APK artifact (Android)
                → Proxmox LXC via Watchtower (backend auto-deploy)
```

---

## 2. Environnement commun

### Outils requis (à installer une seule fois)

| Outil | Version | Usage |
|-------|---------|-------|
| Git | ≥ 2.40 | Versioning |
| Docker Desktop | ≥ 25 | PostgreSQL local + build images |
| VSCode | ≥ 1.87 | Éditeur principal |
| Python | 3.12.x | Backend |
| JDK | 17 (LTS) | Android Gradle build |
| Android SDK | 34 (API 34) | Android build |

### Installation JDK 17 (Windows)

```powershell
# Via winget
winget install Microsoft.OpenJDK.17

# Vérifier
java -version  # doit afficher 17.x
```

### Installation JDK 17 (macOS)

```bash
brew install openjdk@17
echo 'export JAVA_HOME=$(brew --prefix openjdk@17)' >> ~/.zshrc
```

### Variables d'environnement globales

```bash
# À ajouter dans ~/.bashrc ou ~/.zshrc (ou variables système Windows)
export JAVA_HOME=/path/to/jdk17
export ANDROID_HOME=$HOME/Android/Sdk        # Windows: %USERPROFILE%\AppData\Local\Android\Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

---

## 3. Backend Python — Setup

### Prérequis

- Python 3.12 installé (via [python.org](https://python.org) ou `pyenv`)
- Docker Desktop en cours d'exécution (pour PostgreSQL local)

### 1. Cloner et créer l'environnement virtuel

```bash
git clone https://github.com/gaelgael5/mycoach.git
cd mycoach/backend

# Créer un virtualenv Python 3.12
python3.12 -m venv .venv

# Activer
# Linux/macOS :
source .venv/bin/activate
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest, ruff, mypy, pre-commit
```

### 3. PostgreSQL local (Docker)

```bash
# Lancer PostgreSQL 16 en local pour le développement
docker run -d \
  --name mycoach-pg \
  -e POSTGRES_DB=mycoach \
  -e POSTGRES_USER=mycoach \
  -e POSTGRES_PASSWORD=mycoach_dev \
  -p 5432:5432 \
  postgres:16-alpine

# Vérifier
docker ps | grep mycoach-pg
```

### 4. Variables d'environnement locales

Créer un fichier `backend/.env` (ne jamais committer — déjà dans `.gitignore`) :

```env
# Base de données
DATABASE_URL=postgresql+asyncpg://mycoach:mycoach_dev@localhost:5432/mycoach

# Sécurité
SECRET_KEY=dev_secret_key_change_in_production
API_KEY_LENGTH=64

# Google OAuth (optionnel en dev)
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# App
APP_ENV=development
APP_DEBUG=true
APP_PORT=8000

# CORS (dev : accepter localhost Android emulator)
CORS_ORIGINS=["http://localhost:8000","http://10.0.2.2:8000"]
```

> 📌 **10.0.2.2** est l'IP qui permet à l'émulateur Android d'atteindre `localhost` de la machine hôte.

### 5. Migrations Alembic

```bash
# Créer la base de données (première fois)
alembic upgrade head

# Après modification d'un modèle SQLAlchemy :
alembic revision --autogenerate -m "description_de_la_migration"
alembic upgrade head
```

### 6. Lancer le serveur de développement

```bash
cd backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API disponible sur :
# http://localhost:8000
# http://localhost:8000/docs  (Swagger UI)
# http://localhost:8000/redoc
```

### 7. Lancer les tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing

# Lint
ruff check app/
mypy app/
```

### Structure du répertoire `backend/`

```
backend/
├── app/
│   ├── main.py                  ← Point d'entrée FastAPI
│   ├── core/
│   │   ├── config.py            ← Settings (pydantic-settings)
│   │   ├── database.py          ← Engine AsyncPG + session factory
│   │   ├── security.py          ← Hash API Key, verify Google ID Token
│   │   └── dependencies.py      ← Injection de dépendances (get_current_user…)
│   ├── models/                  ← SQLAlchemy 2 ORM models
│   ├── schemas/                 ← Pydantic v2 schemas (request/response)
│   ├── repositories/            ← Accès DB (async SQLAlchemy)
│   ├── services/                ← Logique métier
│   ├── routers/                 ← Endpoints FastAPI
│   └── locales/                 ← i18n JSON (fr.json, en.json…)
├── alembic/                     ← Migrations
├── tests/
│   ├── conftest.py              ← Fixtures pytest (DB en mémoire, client test)
│   ├── test_auth.py
│   └── …
├── requirements.txt
├── requirements-dev.txt
├── .env.example                 ← Template env (commité)
├── .env                         ← Secrets locaux (JAMAIS commité)
├── Dockerfile
└── alembic.ini
```

---

## 4. Android Kotlin — Setup

### Option A : Android Studio (recommandé pour debug/émulateur)

1. Télécharger [Android Studio](https://developer.android.com/studio) (Meerkat 2024.3.1+)
2. Ouvrir le dossier `android/` (pas la racine du repo)
3. Laisser Gradle sync se terminer
4. Créer un AVD (Android Virtual Device) : API 34, Pixel 6

> Android Studio sert principalement pour :
> - Lancer l'émulateur
> - Déboguer (breakpoints, Logcat, profiler)
> - Inspecter le layout (Layout Inspector)

### Option B : VSCode + Gradle en ligne de commande (pour les modifications manuelles)

VSCode peut éditer les fichiers Kotlin/XML. Le build se fait via terminal.

**Extensions VSCode recommandées pour Android :**
- `mathiasfrohlich.Kotlin` — Kotlin language support
- `vscjava.vscode-java-pack` — Java/JVM support (utile pour Gradle)
- `esbenp.prettier-vscode` — formatage XML layouts

**Build via terminal :**

```bash
cd android/

# Compiler en mode debug
./gradlew assembleDebug

# APK généré dans :
# app/build/outputs/apk/debug/app-debug.apk

# Compiler en mode release (nécessite keystore)
./gradlew assembleRelease

# Lancer les tests unitaires
./gradlew test

# Lancer les tests instrumentés (émulateur ou device requis)
./gradlew connectedAndroidTest

# Vérifier le code (Lint Android)
./gradlew lint
```

**Déployer sur device/émulateur depuis terminal :**

```bash
# Vérifier les devices connectés
adb devices

# Installer l'APK debug
adb install app/build/outputs/apk/debug/app-debug.apk

# Ou directement via Gradle (émulateur doit tourner)
./gradlew installDebug
```

### Keystore pour release (à créer une seule fois)

```bash
# Générer le keystore (à stocker hors du repo — en sécurité)
keytool -genkey -v \
  -keystore mycoach-release.keystore \
  -alias mycoach \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Le keystore ne doit PAS être commité dans GitHub
# Le stocker dans un coffre (ex: Bitwarden, 1Password)
# Pour AppVeyor : utiliser les variables secrètes (voir §7)
```

### Structure du répertoire `android/`

```
android/
├── app/
│   ├── build.gradle.kts
│   ├── google-services.json          ← Firebase config (JAMAIS commité)
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── kotlin/com/mycoach/app/
│       │   │   ├── MyCoachApplication.kt   ← Hilt Application
│       │   │   ├── core/
│       │   │   │   ├── di/              ← Modules Hilt
│       │   │   │   ├── network/         ← Retrofit, OkHttp, interceptors
│       │   │   │   ├── security/        ← EncryptedSharedPreferences
│       │   │   │   └── util/            ← Extensions, DateUtils…
│       │   │   ├── data/
│       │   │   │   ├── api/             ← ApiService (Retrofit interfaces)
│       │   │   │   ├── dto/             ← Data Transfer Objects
│       │   │   │   ├── local/           ← Room DB + DAOs
│       │   │   │   ├── mapper/          ← DTO ↔ Domain ↔ Entity
│       │   │   │   └── repository/      ← Implémentations des repos
│       │   │   ├── domain/
│       │   │   │   ├── model/           ← Modèles domaine (purs Kotlin)
│       │   │   │   ├── repository/      ← Interfaces des repos
│       │   │   │   └── usecase/         ← Use cases
│       │   │   └── ui/
│       │   │       ├── auth/            ← Login / Register screens
│       │   │       ├── coach/           ← Espace coach
│       │   │       ├── client/          ← Espace client
│       │   │       ├── common/          ← Composants partagés
│       │   │       └── MainActivity.kt
│       │   └── res/
│       │       ├── layout/              ← XML layouts
│       │       ├── values/strings.xml   ← Strings (langue par défaut = EN)
│       │       ├── values-fr/strings.xml
│       │       └── drawable/
│       └── test/                       ← Tests unitaires (JUnit5)
│       └── androidTest/                ← Tests instrumentés (Espresso)
├── build.gradle.kts                    ← Projet Gradle (root)
├── settings.gradle.kts
├── gradle.properties
├── local.properties                    ← JAMAIS commité (sdk.dir=…)
└── appveyor.yml                        ← CI/CD Android
```

---

## 5. VSCode — Configuration recommandée

### Extensions à installer (identifiants officiels)

**Backend Python :**
```
ms-python.python
ms-python.pylance
charliermarsh.ruff
ms-python.mypy-type-checker
ms-azuretools.vscode-docker
```

**Android Kotlin :**
```
mathiasfrohlich.Kotlin
vscjava.vscode-java-pack
redhat.vscode-xml
esbenp.prettier-vscode
```

**Général :**
```
eamodio.gitlens
github.vscode-pull-request-github
yzhang.markdown-all-in-one
streetsidesoftware.code-spell-checker
```

### `.vscode/settings.json` recommandé (à la racine du repo)

```json
{
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",

  "[kotlin]": {
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  },

  "ruff.lint.args": ["--config", "${workspaceFolder}/backend/pyproject.toml"],

  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/build": true,
    "**/.gradle": true
  }
}
```

### `.vscode/launch.json` — Debug FastAPI

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI — Dev",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "console": "integratedTerminal"
    }
  ]
}
```

---

## 6. Workflows de build locaux

### Backend — Makefile

Un `Makefile` à la racine de `backend/` pour simplifier les commandes :

```makefile
.PHONY: install dev test lint migrate docker-pg

install:
	pip install -r requirements.txt -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/
	mypy app/

migrate:
	alembic upgrade head

migrate-new:
	@read -p "Migration name: " name; alembic revision --autogenerate -m "$$name"

docker-pg:
	docker run -d --name mycoach-pg \
	  -e POSTGRES_DB=mycoach \
	  -e POSTGRES_USER=mycoach \
	  -e POSTGRES_PASSWORD=mycoach_dev \
	  -p 5432:5432 postgres:16-alpine

docker-pg-stop:
	docker stop mycoach-pg && docker rm mycoach-pg
```

### Android — commandes rapides

```bash
# Build debug + install sur device/émulateur connecté
cd android && ./gradlew installDebug

# Tests unitaires avec rapport HTML
./gradlew test && open app/build/reports/tests/testDebugUnitTest/index.html

# Nettoyer le build
./gradlew clean

# Vérifier les dépendances obsolètes
./gradlew dependencyUpdates
```

---

## 7. CI/CD AppVeyor

### Vue d'ensemble

| Pipeline | Fichier | Trigger | Output |
|----------|---------|---------|--------|
| Backend Python | `appveyor.yml` (racine) | push sur `main` ou PR | Docker image → Docker Hub |
| Android | `android/appveyor.yml` | push sur `main` ou PR | APK debug → Artifact AppVeyor |

### 7.1 Backend — `appveyor.yml`

Voir le fichier `appveyor.yml` à la racine du repo.

**Ce que fait le pipeline :**
1. Ubuntu image avec Python 3.12
2. Install dépendances
3. Lancer PostgreSQL (service AppVeyor)
4. Exécuter `pytest` avec couverture
5. Sur `main` seulement : build image Docker + push `blackbeardteam/mycoach-api:latest`

### 7.2 Android — `android/appveyor.yml`

Voir le fichier `android/appveyor.yml`.

**Ce que fait le pipeline :**
1. Ubuntu image avec Android SDK 34 préinstallé
2. Gradle cache
3. `./gradlew assembleDebug`
4. Publier `app-debug.apk` comme artifact AppVeyor téléchargeable

> ⚠️ **Limitation AppVeyor / Android :**
> AppVeyor ne peut pas pousser directement sur le Google Play Store.
> Pour une distribution automatique, utiliser **Fastlane** (future évolution).
> Pour l'instant, l'APK debug est disponible en artifact AppVeyor → téléchargement manuel.

### Variables secrètes AppVeyor (à configurer dans l'UI AppVeyor)

**Projet backend (`mycoach-api`) :**

| Variable | Valeur |
|----------|--------|
| `DOCKER_USERNAME` | `blackbeardteam` |
| `DOCKER_PASSWORD` | *(token Docker Hub)* |
| `SECRET_KEY` | *(clé secrète production)* |
| `GOOGLE_CLIENT_ID` | *(OAuth Client ID)* |
| `GOOGLE_CLIENT_SECRET` | *(OAuth Client Secret)* |

**Projet Android (`mycoach-android`) :**

| Variable | Valeur |
|----------|--------|
| `KEYSTORE_BASE64` | *(keystore encodé en base64)* |
| `KEYSTORE_PASSWORD` | *(mot de passe keystore)* |
| `KEY_ALIAS` | `mycoach` |
| `KEY_PASSWORD` | *(mot de passe clé)* |

> Encoder le keystore en base64 :
> ```bash
> base64 -w 0 mycoach-release.keystore > keystore.b64
> cat keystore.b64  # copier dans AppVeyor
> ```

---

## 8. Déploiement — Vue d'ensemble

### Architecture cible (Proxmox LXC)

```
Proxmox
└── LXC 103 (mycoach) — IP: 192.168.10.6x
    └── Docker Compose
        ├── mycoach-api      ← blackbeardteam/mycoach-api:latest
        ├── mycoach-postgres ← postgres:16-alpine
        ├── mycoach-nginx    ← Reverse proxy (port 80/443)
        └── watchtower       ← Auto-update mycoach-api sur nouvelle image
```

### Fichiers de déploiement

```
deploy/
├── docker-compose.yml      ← Stack complète (voir §8.2)
├── .env.prod               ← Variables de production (JAMAIS commité)
├── nginx/
│   └── mycoach.conf        ← Config Nginx
└── scripts/
    ├── setup-lxc.sh        ← Provision LXC (Docker install, dirs…)
    └── deploy.sh           ← Deploy/update manuel
```

### Détails dans `docker-compose.yml`

Voir le fichier `deploy/docker-compose.yml`.

### Workflow de mise en production

```
1. git push main
    ↓
2. AppVeyor : tests → build Docker → push blackbeardteam/mycoach-api:latest
    ↓
3. Watchtower (sur LXC 103) : détecte nouvelle image → pull → restart
    ↓
4. Zéro intervention manuelle ✅
```

> Pour les migrations Alembic lors d'un déploiement :
> Ajouter un entrypoint dans le Dockerfile qui exécute `alembic upgrade head`
> avant de démarrer uvicorn.

### HTTPS (optionnel, si Tailscale)

Avec Tailscale, le trafic est chiffré end-to-end entre les devices.
L'app Android peut se connecter directement à `http://<tailscale-ip>:8000` en dev.
Pour la production mobile publique, un certificat SSL via Let's Encrypt + domaine public sera nécessaire.

---

## Annexe — Checklist avant premier `git push`

### Backend
- [ ] `.env` ajouté à `.gitignore`
- [ ] `requirements.txt` à jour (`pip freeze > requirements.txt`)
- [ ] `alembic.ini` référence bien `DATABASE_URL` depuis l'env
- [ ] Tests passent (`pytest`)
- [ ] Lint OK (`ruff check`)
- [ ] `Dockerfile` présent dans `backend/`

### Android
- [ ] `local.properties` ajouté à `.gitignore`
- [ ] `google-services.json` ajouté à `.gitignore`
- [ ] Keystore **hors** du repo
- [ ] Build debug OK (`./gradlew assembleDebug`)
- [ ] Tests unitaires OK (`./gradlew test`)
- [ ] `android/appveyor.yml` présent

---

*Document maintenu par Tom ⚡ — à mettre à jour à chaque changement d'outil ou de workflow*
