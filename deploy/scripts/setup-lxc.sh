#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MyCoach — Provisionnement LXC (Proxmox)
# ─────────────────────────────────────────────────────────────────────────────
# Usage : bash setup-lxc.sh
# À exécuter UNE SEULE FOIS sur le container LXC dédié à MyCoach.
# Le container doit être un LXC Debian 12 ou Ubuntu 22.04.
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  MyCoach — Setup LXC                     ║"
echo "╚══════════════════════════════════════════╝"

# ─── 1. Mise à jour système ────────────────────────────────────────────────
echo ""
echo ">>> [1/6] Mise à jour du système..."
apt-get update -q
apt-get upgrade -y -q

# ─── 2. Dépendances système ────────────────────────────────────────────────
echo ""
echo ">>> [2/6] Installation des dépendances..."
apt-get install -y -q \
  curl \
  wget \
  git \
  ca-certificates \
  gnupg \
  lsb-release \
  unzip \
  htop \
  nano

# ─── 3. Docker ────────────────────────────────────────────────────────────
echo ""
echo ">>> [3/6] Installation de Docker..."

if ! command -v docker &>/dev/null; then
  # Ajouter le repo Docker officiel
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  DISTRO=$(lsb_release -cs)
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian $DISTRO stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

  apt-get update -q
  apt-get install -y -q docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  systemctl enable docker
  systemctl start docker
  echo "  ✅ Docker installé : $(docker --version)"
else
  echo "  ✅ Docker déjà installé : $(docker --version)"
fi

# ─── 4. Répertoires de l'application ──────────────────────────────────────
echo ""
echo ">>> [4/6] Création des répertoires..."

APP_DIR="/opt/mycoach"
mkdir -p "$APP_DIR/deploy"
mkdir -p "$APP_DIR/data/postgres"
mkdir -p "$APP_DIR/data/uploads"
mkdir -p "$APP_DIR/logs"

chmod -R 750 "$APP_DIR"
echo "  ✅ Répertoires créés dans $APP_DIR"

# ─── 5. Copier les fichiers de déploiement ────────────────────────────────
echo ""
echo ">>> [5/6] Instructions de déploiement..."
echo ""
echo "  Pour finaliser le déploiement :"
echo ""
echo "  1. Cloner le repo :"
echo "     git clone https://github.com/gaelgael5/mycoach.git /tmp/mycoach"
echo ""
echo "  2. Copier les fichiers de déploiement :"
echo "     cp -r /tmp/mycoach/deploy/* $APP_DIR/deploy/"
echo ""
echo "  3. Créer le fichier .env.prod :"
echo "     cp $APP_DIR/deploy/.env.prod.example $APP_DIR/deploy/.env.prod"
echo "     nano $APP_DIR/deploy/.env.prod  # remplir les secrets"
echo ""
echo "  4. Lancer la stack :"
echo "     cd $APP_DIR/deploy"
echo "     docker compose --env-file .env.prod up -d"
echo ""

# ─── 6. Vérifications finales ─────────────────────────────────────────────
echo ">>> [6/6] Vérifications..."

docker --version && echo "  ✅ Docker OK"
docker compose version && echo "  ✅ Docker Compose OK"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup terminé ✅                         ║"
echo "╚══════════════════════════════════════════╝"
