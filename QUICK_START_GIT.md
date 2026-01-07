# 🚀 Guide Rapide Git pour Production

## Étape 1 : Initialiser Git (si pas déjà fait)

```bash
# Vérifier si Git est déjà initialisé
ls -la .git

# Si le dossier n'existe pas, initialiser Git
git init
```

## Étape 2 : Créer le fichier .env

Créez un fichier `.env` à la racine du projet avec ce contenu :

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire-ici
HOST=0.0.0.0
PORT=5000
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
MAX_UPLOAD_SIZE=10485760
```

**⚠️ IMPORTANT :** Changez `SECRET_KEY` par une clé aléatoire !  
Vous pouvez en générer une avec Python :
```python
import secrets
print(secrets.token_hex(32))
```

## Étape 3 : Premier commit

```bash
# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Initial commit: Energy Analytics MVP"
```

## Étape 4 : Créer un repository sur GitHub

1. Aller sur https://github.com
2. Cliquer sur "New repository"
3. Nommer le repo (ex: `energy-analytics`)
4. Ne PAS cocher "Initialize with README"
5. Cliquer sur "Create repository"

## Étape 5 : Lier et pousser le code

```bash
# Remplacer par votre URL GitHub
git remote add origin https://github.com/VOTRE-USERNAME/energy-analytics.git

# Renommer la branche en main
git branch -M main

# Pousser le code
git push -u origin main
```

## Étape 6 : Déployer sur Streamlit Cloud (Le plus simple)

1. Aller sur https://share.streamlit.io/
2. Se connecter avec GitHub
3. Cliquer sur "New app"
4. Sélectionner votre repository `energy-analytics`
5. Sélectionner la branche `main`
6. **Fichier principal** : `streamlit_app.py`
7. Cliquer sur "Deploy"
8. Votre app est en ligne ! 🎉

**Alternative : Railway (Flask)**
- Si vous préférez utiliser Flask, voir [DEPLOYMENT.md](DEPLOYMENT.md)

## Commandes Git utiles

```bash
# Voir l'état des fichiers
git status

# Ajouter des fichiers modifiés
git add .

# Créer un commit
git commit -m "Description des changements"

# Pousser vers GitHub
git push origin main

# Voir l'historique
git log

# Créer une branche pour une nouvelle fonctionnalité
git checkout -b feature/nom-fonctionnalite

# Revenir sur la branche main
git checkout main
```

## Checklist avant déploiement

- [ ] Git initialisé
- [ ] Fichier `.env` créé avec SECRET_KEY changé
- [ ] Code commité et poussé sur GitHub
- [ ] Repository GitHub créé
- [ ] Variables d'environnement configurées sur la plateforme
- [ ] Application testée en local

## Problèmes courants

**Erreur : "remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/energy-analytics.git
```

**Erreur : "Permission denied"**
- Vérifier que vous êtes connecté à GitHub
- Utiliser un token d'accès personnel si nécessaire

**Fichiers non commités**
```bash
git status  # Voir quels fichiers ne sont pas suivis
git add .    # Ajouter tous les fichiers
git commit -m "Message"
```

---

**C'est tout ! Votre application est prête pour la production 🚀**

