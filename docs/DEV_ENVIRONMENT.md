# MyCoach — Environnement de Développement

> Version : 2.0 — 2026-02-27
> Auteur : Tom ⚡

Ce document décrit l'environnement de développement recommandé pour les deux composantes de MyCoach :
- **Backend** : Python 3.12 + FastAPI + PostgreSQL 16
- **Frontend** : Flutter 3.x (Android · iOS · Web)

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Environnement commun](#2-environnement-commun)
3. [Backend Python — Setup](#3-backend-python--setup)
4. [Frontend Flutter — Setup](#4-frontend-flutter--setup)
5. [VSCode — Configuration recommandée](#5-vscode--configuration-recommandée)
6. [Workflows de build locaux](#6-workflows-de-build-locaux)
7. [CI/CD AppVeyor](#7-cicd-appveyor)
8. [Déploiement — Vue d'ensemble](#8-déploiement--vue-densemble)

---

## 1. Vue d'ensemble

```
mycoach/
├── backend/              ← Python/FastAPI (source principale)
├── frontend/             ← App Flutter (Android · iOS · Web)
├── docs/                 ← Documentation (ce fichier, specs, tâches…)
├── deploy/               ← Fichiers de déploiement (Compose, Nginx, scripts)
│   ├── docker-compose.yml
│   ├── nginx/
│   └── scripts/
└── appveyor.yml          ← CI/CD backend (Python → Docker Hub)
```

**Flux de développement :**
```
Code local (VSCode / Android Studio)
    → git push → GitHub
        → AppVeyor CI → Tests + Build
            → Docker Hub (backend) / APK+IPA artifacts (Flutter)
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
| Flutter SDK | 3.x | Frontend Flutter (Android · iOS · Web) |
| Android Studio | 2024.x | Émulateur Android + debug Flutter |
| Xcode | 15+ | Builds iOS (macOS uniquement) |

### Installation Flutter SDK (Windows/Linux)

```bash
# Télécharger depuis https://flutter.dev/docs/get-started/install
# Ajouter au PATH
export PATH="$PATH:/path/to/flutter/bin"

# Vérifier l'installation
flutter doctor
```

### Installation Flutter SDK (macOS)

```bash
brew install flutter
# ou téléchargement manuel depuis flutter.dev
flutter doctor
```

### Variables d'environnement globales

```bash
# À ajouter dans ~/.bashrc ou ~/.zshrc (ou variables système Windows)
export PATH="$PATH:/path/to/flutter/bin"
# Android SDK (pour builds Android via Flutter)
export ANDROID_HOME=$HOME/Android/Sdk
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

## 4. Frontend Flutter — Setup

### Prérequis
- Flutter SDK 3.x : https://flutter.dev/docs/get-started/install
- Dart SDK (inclus avec Flutter)
- Android Studio (avec plugin Flutter) ou VS Code (avec extension Flutter)
- Xcode 15+ (macOS uniquement — pour builds iOS)
- Chrome (pour développement web)

### Installation

```bash
# Vérifier l'installation
flutter doctor

# Cloner et installer les dépendances
git clone https://github.com/gaelgael5/mycoach.git
cd mycoach/frontend
flutter pub get

# Générer les fichiers de code (json_serializable, riverpod_generator, drift)
dart run build_runner build --delete-conflicting-outputs
```

### Lancer l'application

```bash
# Web (développement)
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000

# Android (émulateur ou device)
flutter run -d android --dart-define=API_BASE_URL=http://192.168.10.63:8200

# iOS (simulateur — macOS requis)
flutter run -d ios --dart-define=API_BASE_URL=http://192.168.10.63:8200
```

### Tests

```bash
flutter test                    # Unit + widget tests
flutter test integration_test/  # Integration tests
```

### Structure du répertoire `frontend/`

```
frontend/
├── lib/
│   ├── main.dart                    ← Point d'entrée (ProviderScope + MaterialApp.router)
│   ├── core/
│   │   ├── api/                     ← Client Dio + ApiKeyInterceptor
│   │   ├── storage/                 ← flutter_secure_storage wrapper
│   │   ├── theme/                   ← AppTheme (light/dark, Inter font)
│   │   ├── router/                  ← go_router configuration
│   │   └── providers/               ← Providers globaux (dio, storage…)
│   ├── features/
│   │   ├── auth/                    ← Login, Register, OTP, Email verify
│   │   ├── home/                    ← Dashboard client / coach
│   │   ├── booking/                 ← Réservation, agenda, liste d'attente
│   │   ├── profile/                 ← Profil, liens sociaux, paramètres santé
│   │   ├── performances/            ← Saisie, historique, graphiques, PRs
│   │   ├── programs/                ← Programmes assignés / création
│   │   ├── payments/                ← Forfaits, paiements, solde
│   │   ├── integrations/            ← Strava, Withings, Google Calendar
│   │   ├── feedback/                ← Suggestions, bug reports
│   │   ├── health/                  ← Paramètres de santé, partage
│   │   └── admin/                   ← Back-office admin (web uniquement)
│   └── shared/
│       ├── widgets/                 ← Widgets réutilisables
│       ├── models/                  ← Modèles Dart partagés
│       └── utils/                   ← Helpers, formatters, validators
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
├── assets/
│   ├── avatars/                     ← Avatars SVG par défaut
│   ├── images/
│   ├── icons/
│   └── fonts/                       ← Inter font family
├── pubspec.yaml                     ← Dépendances Flutter
├── .gitignore
└── README.md
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

**Flutter / Dart :**
```
dart-code.flutter
dart-code.dart-code
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

  "[dart]": {
    "editor.tabSize": 2,
    "editor.insertSpaces": true,
    "editor.formatOnSave": true
  },

  "ruff.lint.args": ["--config", "${workspaceFolder}/backend/pyproject.toml"],

  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/build": true,
    "**/.dart_tool": true
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

### Flutter — commandes rapides

```bash
# Installer les dépendances
cd frontend && flutter pub get

# Lancer sur web (Chrome)
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000

# Tests unitaires + widget
flutter test

# Générer les fichiers de code
dart run build_runner build --delete-conflicting-outputs

# Analyser le code
flutter analyze

# Nettoyer le build
flutter clean
```

---

## 7. CI/CD AppVeyor

### Vue d'ensemble

| Pipeline | Fichier | Trigger | Output |
|----------|---------|---------|--------|
| Backend Python | `appveyor.yml` (racine) | push sur `main` ou PR | Docker image → Docker Hub |
| Flutter | `frontend/appveyor.yml` | push sur `main` ou PR | APK/web build → Artifact AppVeyor |

### 7.1 Backend — `appveyor.yml`

Voir le fichier `appveyor.yml` à la racine du repo.

**Ce que fait le pipeline :**
1. Ubuntu image avec Python 3.12
2. Install dépendances
3. Lancer PostgreSQL (service AppVeyor)
4. Exécuter `pytest` avec couverture
5. Sur `main` seulement : build image Docker + push `blackbeardteam/mycoach-api:latest`

### 7.2 Flutter — `frontend/appveyor.yml`

**Ce que fait le pipeline :**
1. Ubuntu image avec Flutter SDK préinstallé
2. `flutter pub get`
3. `flutter test` (unit + widget tests)
4. `flutter build apk --debug` (Android)
5. `flutter build web` (Web)
6. Publier les artifacts AppVeyor téléchargeables

> ⚠️ **Distribution :**
> Pour une distribution automatique sur Google Play/App Store, utiliser **Fastlane** (future évolution).

### Variables secrètes AppVeyor (à configurer dans l'UI AppVeyor)

**Projet backend (`mycoach-api`) :**

| Variable | Valeur |
|----------|--------|
| `DOCKER_USERNAME` | `blackbeardteam` |
| `DOCKER_PASSWORD` | *(token Docker Hub)* |
| `SECRET_KEY` | *(clé secrète production)* |
| `GOOGLE_CLIENT_ID` | *(OAuth Client ID)* |
| `GOOGLE_CLIENT_SECRET` | *(OAuth Client Secret)* |

**Projet Flutter (`mycoach-flutter`) :**

| Variable | Valeur |
|----------|--------|
| `KEYSTORE_BASE64` | *(keystore Android encodé en base64)* |
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
L'app Flutter peut se connecter directement à `http://<tailscale-ip>:8000` en dev (via `--dart-define=API_BASE_URL=...`).
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

### Flutter
- [ ] `google-services.json` ajouté à `.gitignore`
- [ ] Keystore Android **hors** du repo
- [ ] Build web OK (`flutter build web`)
- [ ] Tests unitaires OK (`flutter test`)
- [ ] `frontend/pubspec.yaml` présent et à jour

---

*Document maintenu par Tom ⚡ — à mettre à jour à chaque changement d'outil ou de workflow*
