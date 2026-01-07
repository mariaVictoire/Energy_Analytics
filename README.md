# Energy Analytics

Prototype fonctionnel d'analyse du marché de l'électricité pour producteurs d'énergies renouvelables.

## 📋 Description

Ce projet permet d'analyser la performance financière d'une production d'énergie renouvelable sur le marché spot de l'électricité. Il calcule les revenus, identifie les pertes liées aux prix négatifs, et génère un rapport business structuré.

## 🏗️ Architecture

Le projet suit une architecture modulaire en pipeline :

```
Chargement → Normalisation → Fusion → Calculs → Rapport
```

Chaque étape est un script Python indépendant, ce qui permet une maintenance et des tests faciles.

## 📁 Structure du Projet

```
energy_analytics/
├── data/
│   ├── market/
│   │   └── spot_prices.csv      # Données de prix spot (start_date, end_date, price)
│   └── client/
│       └── production.csv       # Données de production (date, production)
│
├── scripts/
│   ├── load_data.py             # Chargement des CSV
│   ├── normalize_data.py         # Normalisation des dates et colonnes
│   ├── merge_data.py            # Fusion des datasets
│   ├── compute_metrics.py        # Calcul des métriques financières
│   ├── generate_report.py        # Génération du rapport Markdown/HTML
│   └── run_analysis.py          # Script principal (orchestre tout)
│
├── templates/
│   └── index.html               # Interface web
│
├── uploads/                     # Dossier temporaire pour fichiers uploadés
│
├── reports/
│   ├── monthly_report.md         # Rapport Markdown généré automatiquement
│   └── monthly_report.html      # Rapport HTML avec graphiques
│
├── prompts/
│   └── monthly_summary.txt      # Template pour résumé IA
│
├── app.py                       # Application web Flask
├── requirements.txt             # Dépendances Python
└── README.md
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pandas
- numpy
- matplotlib (optionnel, pour les graphiques dans le rapport HTML)
- Flask (pour l'application web)

### Installation des dépendances

**Option 1 : Installation complète (recommandée)**

```bash
pip install -r requirements.txt
```

**Option 2 : Installation manuelle**

```bash
pip install Flask pandas numpy matplotlib Werkzeug
```

**Note** : Si matplotlib n'est pas installé, le rapport HTML sera généré sans graphiques.

## 📊 Format des Données

### Données marché (`data/market/spot_prices.csv`)

Colonnes requises :
- `start_date` : Date de début de la période (format ISO avec timezone)
- `end_date` : Date de fin de la période
- `price` : Prix spot en €/MWh

Exemple :
```csv
start_date,end_date,price
2025-05-01T02:00:00+02:00,2025-05-01T03:00:00+02:00,22.59
```

### Données production (`data/client/production.csv`)

Colonnes requises :
- `date` : Date et heure (format ISO avec timezone)
- `production` : Production en MWh

Exemple :
```csv
date,production
2025-05-01T00:00:00+02:00,25.5
```

**Note** : Les formats de colonnes sont flexibles. Le script détecte automatiquement les noms de colonnes courants (`date`, `datetime`, `production`, `production_mwh`, etc.).

## 🎯 Utilisation

### Application Web (Recommandé)

L'application web offre une interface conviviale pour :
- Choisir un mois à analyser
- Charger un fichier CSV de production
- Générer et télécharger le rapport HTML

**Lancer l'application web :**

```bash
python app.py
```

Puis ouvrez votre navigateur à l'adresse : `http://localhost:5000`

L'interface vous permet de :
1. Sélectionner un mois dans la liste déroulante
2. Charger votre fichier CSV de production
3. Cliquer sur "Lancer l'analyse"
4. Télécharger automatiquement le rapport HTML généré

### Exécution en ligne de commande

Pour lancer l'analyse complète via script :

```bash
python scripts/run_analysis.py
```

Ce script exécute toutes les étapes :
1. Charge les données marché et production
2. Normalise les formats de dates
3. Fusionne les datasets
4. Calcule les métriques financières
5. Génère les rapports Markdown et HTML

Les rapports seront sauvegardés dans :
- `reports/monthly_report.md` (Markdown)
- `reports/monthly_report.html` (HTML avec graphiques)

### Exécution étape par étape

Vous pouvez aussi exécuter chaque script individuellement :

```bash
# Test du chargement
python scripts/load_data.py

# Test de normalisation
python scripts/normalize_data.py

# Test de fusion
python scripts/merge_data.py

# Test des calculs
python scripts/compute_metrics.py

# Génération du rapport
python scripts/generate_report.py
```

## 📈 Métriques Calculées

### Métriques horaires

- **Revenu horaire** : `production_mwh × price_eur_mwh`
- **Pertes prix négatifs** : `production_mwh × abs(price_eur_mwh)` si prix < 0
- **Heures à prix négatif** : Identification des périodes critiques

### Agrégations mensuelles

- Revenu total
- Pertes totales liées aux prix négatifs
- Production totale
- Prix moyen, minimum, maximum
- Nombre d'heures à prix négatif
- Production pendant les heures à prix négatif
- Pourcentage de perte par rapport au revenu

## 📄 Rapports Générés

Le système génère deux types de rapports :

### Rapport Markdown

Le rapport Markdown (`reports/monthly_report.md`) contient :

1. **Résumé exécutif** : Vue d'ensemble de l'analyse
2. **Chiffres clés** : Tableau récapitulatif des indicateurs principaux
3. **Analyse mensuelle** : Tableau détaillé par mois
4. **Analyse des pertes** : Explication des pertes liées aux prix négatifs
5. **Heures critiques** : Top 10 des heures avec les pertes les plus importantes
6. **Recommandations** : Suggestions génériques d'optimisation

### Rapport HTML

Le rapport HTML (`reports/monthly_report.html`) est une version enrichie avec :

- **Design moderne** : Interface visuelle attrayante avec dégradés et animations
- **Graphiques interactifs** : Visualisations des prix, production, revenus et distributions
- **Cartes KPI** : Indicateurs clés présentés dans des cartes colorées
- **Mise en page responsive** : S'adapte à tous les écrans
- **Graphiques inclus** :
  - Évolution des prix spot au fil du temps
  - Évolution de la production
  - Revenus horaires (avec distinction positif/négatif)
  - Distribution des prix
  - Répartition des heures (prix positifs vs négatifs)

Le rapport HTML est généré automatiquement en même temps que le rapport Markdown.

**Note** : Les graphiques nécessitent matplotlib. Si matplotlib n'est pas installé, le rapport HTML sera généré sans graphiques.

## 🔧 Personnalisation

### Modifier les chemins des fichiers

Les scripts utilisent des chemins relatifs par défaut. Pour modifier les chemins, vous pouvez :

1. Modifier directement les chemins dans les fonctions `load_market_data()` et `load_production_data()`
2. Passer les chemins en paramètres lors de l'appel des fonctions

### Ajouter de nouvelles métriques

Pour ajouter de nouvelles métriques, modifiez `scripts/compute_metrics.py` :

1. Ajoutez votre fonction de calcul
2. Appelez-la dans `compute_all_metrics()`
3. Mettez à jour `generate_report.py` pour afficher la nouvelle métrique

## 🐛 Dépannage

### Erreur : "Fichier non trouvé"

Vérifiez que les fichiers CSV sont bien présents dans :
- `data/market/spot_prices.csv`
- `data/client/production.csv`

### Erreur : "Colonne non trouvée"

Vérifiez que vos CSV contiennent les colonnes attendues. Le script détecte automatiquement plusieurs noms de colonnes courants.

### Aucune correspondance de dates

Si les dates entre marché et production ne correspondent pas :
- Vérifiez les formats de dates (doivent être compatibles ISO)
- Vérifiez les timezones
- Le script utilisera un left join et mettra la production à 0 pour les dates manquantes

## 📝 Notes pour Développeurs

- **Code simple et lisible** : Pensé pour un MVP solo founder
- **Pas de dépendances lourdes** : Seulement pandas et numpy
- **Modulaire** : Chaque script a une responsabilité unique
- **Commenté** : Code documenté pour faciliter la maintenance

## 🌐 Application Web

L'application web Flask offre une interface utilisateur intuitive pour analyser vos données.

### Fonctionnalités

- **Sélection de mois** : Choisissez parmi les mois disponibles dans vos données de marché
- **Upload de fichiers** : Chargez facilement vos fichiers CSV de production
- **Analyse automatique** : Le système génère automatiquement le rapport HTML
- **Téléchargement** : Le rapport est téléchargé automatiquement après génération

### Utilisation

1. **Lancer l'application** :
   ```bash
   python app.py
   ```

2. **Ouvrir dans le navigateur** :
   - Accédez à `http://localhost:5000`

3. **Utiliser l'interface** :
   - Sélectionnez le mois à analyser
   - Chargez votre fichier CSV de production
   - Cliquez sur "Lancer l'analyse"
   - Le rapport HTML sera généré et téléchargé automatiquement

### Format du fichier CSV de production

Votre fichier CSV doit contenir au minimum :
- Une colonne de date : `date`, `datetime`, `start_date`, ou `timestamp`
- Une colonne de production : `production`, `production_mwh`, `value`, ou `power`

Exemple :
```csv
date,production
2025-05-01T00:00:00+02:00,25.5
2025-05-01T01:00:00+02:00,22.3
```

## 🚀 Déploiement en Production

L'application est maintenant disponible en deux versions :

### Version Streamlit (Recommandée)

- **Interface moderne** : Streamlit offre une meilleure UX pour les apps de data
- **Déploiement gratuit** : Streamlit Community Cloud est gratuit
- **Simple** : Déploiement en quelques clics

**Guide de déploiement :** [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

### Version Flask (Alternative)

- **Plus de contrôle** : Flask offre plus de flexibilité
- **Déploiement sur plusieurs plateformes** : Railway, Heroku, Render, etc.

**Guides de déploiement :**
- **[QUICK_START_GIT.md](QUICK_START_GIT.md)** : Guide rapide pour commencer avec Git
- **[DEPLOYMENT.md](DEPLOYMENT.md)** : Guide complet avec toutes les options

### Déploiement rapide Streamlit (5 minutes)

1. **Initialiser Git** (si pas déjà fait)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Créer un repository GitHub**
   - Aller sur https://github.com
   - Créer un nouveau repository
   - Pousser votre code

3. **Déployer sur Streamlit Cloud**
   - Aller sur https://share.streamlit.io/
   - Se connecter avec GitHub
   - "New app" → Sélectionner votre repo
   - Fichier principal : `streamlit_app.py`
   - C'est tout ! 🎉

Pour plus de détails, voir [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

## 🔮 Évolutions Possibles

- Export Excel en plus du Markdown
- Comparaison avec données historiques
- Prédictions basiques (régression linéaire)
- Intégration avec APIs de marché en temps réel
- Authentification utilisateur
- Historique des analyses

## 📄 Licence

Ce projet est un prototype. Utilisez-le comme base pour votre propre solution.

## 🤝 Contribution

Ce projet est conçu comme un MVP. Pour des fonctionnalités avancées, adaptez le code selon vos besoins.

---

**Développé pour l'analyse du marché de l'électricité renouvelable**
