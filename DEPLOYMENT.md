# Guide de Déploiement - Energy Analytics

Ce guide vous explique comment passer votre application en production.

## 📋 Table des matières

1. [Préparation avec Git](#1-préparation-avec-git)
2. [Configuration pour la production](#2-configuration-pour-la-production)
3. [Choix de la plateforme](#3-choix-de-la-plateforme)
4. [Déploiement](#4-déploiement)
5. [Post-déploiement](#5-post-déploiement)

---

## 1. Préparation avec Git

### Pourquoi utiliser Git ?

✅ **Versioning** : Historique de toutes les modifications  
✅ **Backup** : Sauvegarde de votre code  
✅ **Collaboration** : Facilite le travail en équipe  
✅ **Rollback** : Possibilité de revenir en arrière en cas de problème  
✅ **Déploiement** : Intégration facile avec les plateformes de déploiement  

### Étapes initiales avec Git

```bash
# 1. Initialiser Git (si pas déjà fait)
git init

# 2. Créer un fichier .gitignore (déjà présent)
# Vérifier qu'il contient bien :
# - __pycache__/
# - *.pyc
# - uploads/
# - reports/*.html
# - reports/*.png
# - reports/*.json
# - .env
# - venv/

# 3. Ajouter tous les fichiers
git add .

# 4. Créer le premier commit
git commit -m "Initial commit: MVP Energy Analytics"

# 5. Créer un repository sur GitHub/GitLab/Bitbucket
# (via l'interface web de votre choix)

# 6. Lier votre repo local au repo distant
git remote add origin https://github.com/votre-username/energy_analytics.git

# 7. Pousser le code
git branch -M main
git push -u origin main
```

### Workflow Git recommandé

```bash
# Pour chaque nouvelle fonctionnalité
git checkout -b feature/nom-fonctionnalite
# ... faire vos modifications ...
git add .
git commit -m "Description des changements"
git push origin feature/nom-fonctionnalite
# Créer une Pull Request sur GitHub

# Pour la production
git checkout main
git merge feature/nom-fonctionnalite
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin main --tags
```

---

## 2. Configuration pour la production

### 2.1 Variables d'environnement

Créer un fichier `.env.example` :

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
HOST=0.0.0.0
PORT=5000

# Paths
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
DATA_MARKET_FOLDER=data/market
DATA_CLIENT_FOLDER=data/client

# Security
MAX_UPLOAD_SIZE=10485760  # 10MB en bytes
ALLOWED_EXTENSIONS=csv
```

Créer un fichier `.env` (ne pas commiter !) avec vos vraies valeurs.

### 2.2 Modifier app.py pour la production

```python
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'changez-moi-en-production')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 10485760))

# Désactiver le mode debug en production
if os.getenv('FLASK_ENV') == 'production':
    app.debug = False
```

### 2.3 Créer un fichier requirements.txt complet

```txt
Flask==3.0.0
pandas==2.1.3
numpy==1.26.2
matplotlib==3.8.2
Werkzeug==3.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 2.4 Créer un fichier Procfile (pour Heroku/Railway)

```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 2.5 Créer un fichier runtime.txt (pour spécifier la version Python)

```
python-3.11.0
```

---

## 3. Choix de la plateforme

### Option 1 : Heroku (Recommandé pour débuter)

**Avantages :**
- ✅ Simple à configurer
- ✅ Gratuit pour les petits projets (avec limitations)
- ✅ Intégration Git directe
- ✅ Add-ons disponibles

**Inconvénients :**
- ❌ Coûteux à l'échelle
- ❌ Limites sur le plan gratuit

**Prix :** ~$7/mois (Eco Dyno)

### Option 2 : Railway

**Avantages :**
- ✅ Très simple
- ✅ $5 de crédit gratuit/mois
- ✅ Déploiement automatique depuis Git
- ✅ Bon pour MVP

**Prix :** ~$5-10/mois

### Option 3 : Render

**Avantages :**
- ✅ Gratuit pour les services web
- ✅ Simple
- ✅ Auto-déploiement depuis Git

**Prix :** Gratuit (avec limitations) ou ~$7/mois

### Option 4 : DigitalOcean App Platform

**Avantages :**
- ✅ Flexible
- ✅ Bon contrôle
- ✅ Bon rapport qualité/prix

**Prix :** ~$5-12/mois

### Option 5 : VPS (DigitalOcean, Linode, etc.)

**Avantages :**
- ✅ Contrôle total
- ✅ Plus économique à grande échelle
- ✅ Pas de limitations

**Inconvénients :**
- ❌ Plus de configuration manuelle
- ❌ Maintenance requise

**Prix :** ~$5-20/mois

---

## 4. Déploiement

### 4.1 Déploiement sur Railway (Exemple)

1. **Créer un compte Railway**
   - Aller sur https://railway.app
   - Se connecter avec GitHub

2. **Créer un nouveau projet**
   - Cliquer sur "New Project"
   - Sélectionner "Deploy from GitHub repo"
   - Choisir votre repository

3. **Configurer les variables d'environnement**
   - Dans les settings du projet
   - Ajouter toutes les variables du `.env`

4. **Railway détecte automatiquement**
   - Détecte `requirements.txt`
   - Détecte `Procfile`
   - Lance le déploiement

5. **Obtenir l'URL**
   - Railway génère une URL automatique
   - Vous pouvez ajouter un domaine personnalisé

### 4.2 Déploiement sur Heroku

```bash
# 1. Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Se connecter
heroku login

# 3. Créer une app
heroku create energy-analytics

# 4. Configurer les variables d'environnement
heroku config:set SECRET_KEY=votre-cle-secrete
heroku config:set FLASK_ENV=production

# 5. Déployer
git push heroku main

# 6. Ouvrir l'app
heroku open
```

### 4.3 Déploiement sur VPS (Ubuntu)

```bash
# 1. Se connecter au serveur
ssh user@votre-serveur.com

# 2. Installer les dépendances système
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# 3. Cloner le repository
git clone https://github.com/votre-username/energy_analytics.git
cd energy_analytics

# 4. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 5. Installer les dépendances
pip install -r requirements.txt
pip install gunicorn

# 6. Créer le fichier .env
nano .env
# Ajouter vos variables d'environnement

# 7. Tester l'application
gunicorn app:app --bind 0.0.0.0:8000

# 8. Configurer systemd pour le service
sudo nano /etc/systemd/system/energy-analytics.service
```

Contenu du fichier systemd :

```ini
[Unit]
Description=Energy Analytics Web App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/energy_analytics
Environment="PATH=/path/to/energy_analytics/venv/bin"
ExecStart=/path/to/energy_analytics/venv/bin/gunicorn app:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

```bash
# 9. Activer et démarrer le service
sudo systemctl enable energy-analytics
sudo systemctl start energy-analytics

# 10. Configurer Nginx
sudo nano /etc/nginx/sites-available/energy-analytics
```

Configuration Nginx :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/energy_analytics/static;
    }
}
```

```bash
# 11. Activer le site
sudo ln -s /etc/nginx/sites-available/energy-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 12. Configurer SSL avec Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

---

## 5. Post-déploiement

### 5.1 Checklist de sécurité

- [ ] Secret key changé et sécurisé
- [ ] Mode debug désactivé
- [ ] HTTPS activé (SSL/TLS)
- [ ] Variables d'environnement configurées
- [ ] Fichiers sensibles dans .gitignore
- [ ] Limites de taille de fichier configurées
- [ ] Validation des inputs activée

### 5.2 Monitoring

**Options recommandées :**

1. **Sentry** (gestion d'erreurs)
   ```bash
   pip install sentry-sdk[flask]
   ```

2. **Uptime Robot** (surveillance de disponibilité)
   - Gratuit
   - Vérifie que votre site répond

3. **Logs**
   - Surveiller les logs de l'application
   - Configurer la rotation des logs

### 5.3 Backup

**Stratégie de backup :**

1. **Code** : Git (déjà fait)
2. **Données** : 
   - Backup régulier du dossier `data/`
   - Backup des rapports générés si important
   - Utiliser un service cloud (S3, etc.)

### 5.4 Mise à jour

```bash
# 1. Faire les modifications en local
git checkout -b fix/bug-ou-feature

# 2. Tester en local
python app.py

# 3. Commiter
git add .
git commit -m "Fix: description"
git push origin fix/bug-ou-feature

# 4. Merge sur main après tests
git checkout main
git merge fix/bug-ou-feature

# 5. Déployer
git push origin main
# (Déploiement automatique si configuré)
```

---

## 📝 Checklist de déploiement

### Avant le déploiement

- [ ] Code versionné sur Git
- [ ] `.env` créé avec les bonnes valeurs
- [ ] `requirements.txt` à jour
- [ ] `Procfile` créé (si nécessaire)
- [ ] Tests effectués en local
- [ ] Secret key généré et sécurisé

### Déploiement

- [ ] Compte créé sur la plateforme choisie
- [ ] Repository lié
- [ ] Variables d'environnement configurées
- [ ] Déploiement réussi
- [ ] URL accessible

### Après le déploiement

- [ ] Application fonctionne
- [ ] HTTPS configuré
- [ ] Monitoring en place
- [ ] Backup configuré
- [ ] Documentation mise à jour

---

## 🚀 Quick Start (Railway - Le plus simple)

1. **Préparer le code**
   ```bash
   git add .
   git commit -m "Ready for production"
   git push origin main
   ```

2. **Sur Railway**
   - Créer un compte
   - New Project → Deploy from GitHub
   - Sélectionner votre repo
   - Ajouter les variables d'environnement
   - C'est tout ! 🎉

3. **Obtenir l'URL**
   - Railway génère automatiquement une URL
   - Votre app est en ligne !

---

## 📚 Ressources

- [Flask Production Best Practices](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Git Documentation](https://git-scm.com/doc)
- [Railway Docs](https://docs.railway.app/)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)

---

## ❓ Questions fréquentes

**Q: Dois-je absolument utiliser Git ?**  
R: Oui, c'est fortement recommandé. C'est la base du développement moderne et nécessaire pour la plupart des plateformes de déploiement.

**Q: Quelle plateforme choisir pour commencer ?**  
R: Railway ou Render sont les plus simples pour un MVP. Heroku est aussi une bonne option.

**Q: Combien ça coûte ?**  
R: Pour un MVP, vous pouvez commencer gratuitement ou pour ~$5-10/mois.

**Q: Puis-je déployer sans Git ?**  
R: Techniquement oui (upload manuel), mais c'est déconseillé et compliqué.

---

**Bon déploiement ! 🚀**

