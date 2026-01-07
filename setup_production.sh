#!/bin/bash
# Script de configuration pour la production

echo "🚀 Configuration pour la production..."

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Modifiez le fichier .env avec vos vraies valeurs !"
    echo "   - Changez SECRET_KEY"
    echo "   - Vérifiez les autres variables"
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p uploads
mkdir -p reports
mkdir -p data/market
mkdir -p data/client

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "✅ Configuration terminée !"
echo ""
echo "Prochaines étapes:"
echo "1. Modifiez le fichier .env"
echo "2. Testez l'application: python app.py"
echo "3. Déployez sur votre plateforme choisie"

