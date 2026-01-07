# 🚀 Déploiement sur Streamlit Community Cloud

Guide rapide pour déployer Energy Analytics sur Streamlit Community Cloud.

## 📋 Prérequis

1. Un compte GitHub
2. Un compte Streamlit (gratuit)
3. Votre code versionné sur GitHub

## 🎯 Étapes de déploiement

### 1. Préparer le code pour Git

```bash
# Vérifier que tous les fichiers sont prêts
git status

# Ajouter tous les fichiers
git add .

# Créer un commit
git commit -m "Ready for Streamlit Cloud deployment"
```

### 2. Créer un repository GitHub

1. Aller sur https://github.com
2. Cliquer sur "New repository"
3. Nommer le repo (ex: `energy-analytics`)
4. **Ne PAS** cocher "Initialize with README"
5. Cliquer sur "Create repository"

### 3. Pousser le code sur GitHub

```bash
# Si Git n'est pas encore initialisé
git init
git add .
git commit -m "Initial commit"

# Lier au repository GitHub (remplacer par votre URL)
git remote add origin https://github.com/VOTRE-USERNAME/energy-analytics.git

# Pousser le code
git branch -M main
git push -u origin main
```

### 4. Déployer sur Streamlit Cloud

1. **Aller sur Streamlit Cloud**
   - https://share.streamlit.io/
   - Se connecter avec votre compte GitHub

2. **Créer une nouvelle app**
   - Cliquer sur "New app"
   - Sélectionner votre repository GitHub
   - Sélectionner la branche `main`
   - **Fichier principal** : `streamlit_app.py`
   - Cliquer sur "Deploy"

3. **Attendre le déploiement**
   - Streamlit va installer les dépendances
   - L'app sera disponible à une URL comme : `https://energy-analytics.streamlit.app`

### 5. Configuration (optionnel)

Dans les settings de votre app sur Streamlit Cloud, vous pouvez :
- Changer le nom de l'app
- Ajouter un domaine personnalisé
- Configurer les secrets (variables d'environnement)

## 📁 Fichiers nécessaires

Votre repository doit contenir :

```
energy-analytics/
├── streamlit_app.py          # Application principale Streamlit
├── requirements.txt          # Dépendances Python
├── .streamlit/
│   └── config.toml          # Configuration Streamlit (optionnel)
├── scripts/                 # Scripts d'analyse
├── data/
│   └── market/
│       └── spot_prices.csv  # Données de marché
└── templates/               # Templates HTML (si nécessaire)
```

## ✅ Checklist avant déploiement

- [ ] Code versionné sur Git
- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub
- [ ] `streamlit_app.py` présent à la racine
- [ ] `requirements.txt` à jour avec toutes les dépendances
- [ ] Fichier `data/market/spot_prices.csv` présent (ou données accessibles)
- [ ] Testé en local avec `streamlit run streamlit_app.py`

## 🧪 Tester en local avant déploiement

```bash
# Installer Streamlit
pip install streamlit

# Lancer l'application
streamlit run streamlit_app.py
```

L'application sera accessible sur `http://localhost:8501`

## 🔧 Configuration avancée

### Variables d'environnement (Secrets)

Si vous avez besoin de variables d'environnement :

1. Dans Streamlit Cloud, aller dans "Settings" → "Secrets"
2. Ajouter vos secrets au format TOML :

```toml
[secrets]
SECRET_KEY = "votre-cle-secrete"
API_KEY = "votre-api-key"
```

3. Utiliser dans le code :

```python
import streamlit as st

secret_key = st.secrets["SECRET_KEY"]
```

### Fichiers de données

Les fichiers dans votre repository sont accessibles directement. Pour `data/market/spot_prices.csv`, le chemin sera :

```python
data_path = Path(__file__).parent / "data" / "market" / "spot_prices.csv"
```

## 🐛 Dépannage

### Erreur : "Module not found"

- Vérifier que toutes les dépendances sont dans `requirements.txt`
- Vérifier que les imports sont corrects

### Erreur : "File not found"

- Vérifier que les fichiers de données sont bien dans le repository
- Vérifier les chemins relatifs dans le code

### L'app ne se met pas à jour

- Vérifier que vous avez bien poussé les changements sur GitHub
- Streamlit Cloud se met à jour automatiquement, mais peut prendre quelques minutes

## 📊 Avantages de Streamlit Cloud

✅ **Gratuit** : Pas de limite de temps  
✅ **Simple** : Déploiement en quelques clics  
✅ **Automatique** : Mise à jour automatique depuis GitHub  
✅ **Sécurisé** : HTTPS par défaut  
✅ **Rapide** : Déploiement en quelques minutes  

## 🔗 Ressources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Community](https://discuss.streamlit.io/)

---

**Votre application est maintenant en ligne ! 🎉**

