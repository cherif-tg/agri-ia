#!/bin/bash
# Script de déploiement Docker local/VPS
# Usage: ./deploy-docker.sh [start|stop|logs|rebuild]

set -e

COMMAND=${1:-start}
COMPOSE_FILE="docker-compose.yml"

echo "🐳 Gestion Docker - Prévision Agricole IA"
echo "========================================="

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "📥 Installer: https://docs.docker.com/get-docker/"
    exit 1
fi

# Vérifier docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️ docker-compose n'est pas installé"
    echo "📥 Installer: https://docs.docker.com/compose/install/"
    exit 1
fi

case $COMMAND in
    start)
        echo "🚀 Démarrage du container..."
        docker-compose -f "$COMPOSE_FILE" up -d
        echo "✅ Container démarré!"
        echo "📍 Accès: http://localhost:8501"
        echo ""
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    
    stop)
        echo "⏹️ Arrêt du container..."
        docker-compose -f "$COMPOSE_FILE" down
        echo "✅ Container arrêté!"
        ;;
    
    restart)
        echo "🔄 Redémarrage du container..."
        docker-compose -f "$COMPOSE_FILE" restart
        echo "✅ Container redémarré!"
        ;;
    
    logs)
        echo "📋 Logs du container..."
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    
    rebuild)
        echo "🔨 Reconstruction de l'image..."
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        echo "✅ Image reconstruite!"
        echo ""
        echo "▶️ Pour démarrer: ./deploy-docker.sh start"
        ;;
    
    status)
        echo "📊 Statut des containers..."
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    
    shell)
        echo "🐚 Accès au container..."
        docker-compose -f "$COMPOSE_FILE" exec streamlit-app /bin/bash
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|logs|rebuild|status|shell}"
        echo ""
        echo "Commandes:"
        echo "  start    - Démarrer le container"
        echo "  stop     - Arrêter le container"
        echo "  restart  - Redémarrer le container"
        echo "  logs     - Voir les logs en temps réel"
        echo "  rebuild  - Reconstruire l'image Docker"
        echo "  status   - Voir le statut"
        echo "  shell    - Accès shell dans le container"
        exit 1
        ;;
esac
