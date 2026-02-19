#!/bin/bash
# Script de déploiement Heroku facile
# Usage: ./deploy-heroku.sh

set -e

APP_NAME="agri-ia-prevision"
HEROKU_APP="${HEROKU_APP:-$APP_NAME}"

echo "🚀 Déploiement sur Heroku"
echo "========================"

# Vérifier Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI non installée"
    echo "📥 Installer: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Vérifier Git
if ! command -v git &> /dev/null; then
    echo "❌ Git non installé"
    exit 1
fi

# Se connecter Heroku
echo "🔐 Connexion Heroku..."
heroku login

# Vérifier .git
if [ ! -d ".git" ]; then
    echo "📦 Initialisant Git..."
    git init
    git config user.email "agri@ia.tg"
    git config user.name "Agri IA"
fi

# Créer app si elle existe pas
echo "🏗️ Vérifying Heroku app..."
if ! heroku apps:info -a "$HEROKU_APP" &> /dev/null; then
    echo "📝 Créant app: $HEROKU_APP"
    heroku create "$HEROKU_APP"
fi

# Ajouter remote
echo "🔗 Configuration Git remote..."
if ! git remote | grep -q heroku; then
    heroku git:remote -a "$HEROKU_APP"
fi

# Ajouter les fichiers
echo "📤 Staging fichiers..."
git add .
git commit -m "Deploy: $(date +'%Y-%m-%d %H:%M:%S')" || echo "⚠️ Rien à commiter"

# Déployer
echo "🚀 Pushing vers Heroku..."
git push heroku main 2>&1 || git push heroku master 2>&1

# Voir les logs
echo ""
echo "✅ Déploiement complete!"
echo ""
echo "🔗 App URL : https://$HEROKU_APP.herokuapp.com"
echo ""
echo "📋 Voulez-vous voir les logs? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    heroku logs --tail -a "$HEROKU_APP"
fi
