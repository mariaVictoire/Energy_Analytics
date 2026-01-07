# 🚀 Guide Rapide : Push sur GitHub pour Streamlit Cloud

## ✅ Checklist avant de push

Vérifiez que vous avez :
- [ ] `streamlit_app.py` à la racine
- [ ] `requirements.txt` avec streamlit
- [ ] `data/market/spot_prices.csv` (ou vos données)
- [ ] Tous les scripts dans `scripts/`

## 📝 Commandes Git (copier-coller)

### Si Git n'est pas encore initialisé :

```bash
# 1. Initialiser Git
git init

# 2. Ajouter tous les fichiers
git add .

# 3. Créer le premier commit
git commit -m "Initial commit: Energy Analytics avec Streamlit"

# 4. Créer un repository sur GitHub (via le site web)
#    https://github.com → New repository
#    Nom : energy-analytics
#    Ne PAS cocher "Initialize with README"

# 5. Lier votre repo local au repo GitHub
#    REMPLACER "VOTRE-USERNAME" par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE-USERNAME/energy-analytics.git

# 6. Renommer la branche en main
git branch -M main

# 7. Pousser le code
git push -u origin main
```

### Si Git est déjà initialisé :

```bash
# 1. Vérifier l'état
git status

# 2. Ajouter tous les fichiers modifiés
git add .

# 3. Créer un commit
git commit -m "Ready for Streamlit Cloud deployment"

# 4. Pousser vers GitHub
git push origin main
```

## 🎯 Après le push

1. **Aller sur Streamlit Cloud**
   - https://share.streamlit.io/
   - Se connecter avec GitHub

2. **Créer une nouvelle app**
   - Cliquer sur "New app"
   - Sélectionner votre repository
   - Sélectionner la branche `main`
   - **Fichier principal** : `streamlit_app.py`
   - Cliquer sur "Deploy"

3. **Attendre 2-3 minutes**
   - Streamlit installe les dépendances
   - Votre app est en ligne ! 🎉

## ⚠️ Fichiers à NE PAS commit

Ces fichiers sont automatiquement ignorés (dans `.gitignore`) :
- `__pycache__/`
- `*.pyc`
- `uploads/`
- `reports/*.html`
- `reports/*.json`
- `.env`
- `venv/`

## 🐛 Problèmes courants

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/VOTRE-USERNAME/energy-analytics.git
```

### "Permission denied"
- Vérifier que vous êtes connecté à GitHub
- Utiliser un token d'accès personnel si nécessaire

### "Nothing to commit"
```bash
# Vérifier les fichiers ignorés
git status

# Si vous voulez forcer l'ajout d'un fichier ignoré
git add -f nom-du-fichier
```

## 📚 Prochaines étapes

Une fois déployé sur Streamlit Cloud :
- Votre app sera accessible à une URL comme : `https://energy-analytics.streamlit.app`
- Les mises à jour sont automatiques : push sur GitHub → Streamlit se met à jour
- Vous pouvez partager l'URL avec vos utilisateurs

---

**C'est tout ! Votre application est prête pour Streamlit Cloud 🚀**

