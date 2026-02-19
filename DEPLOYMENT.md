# 🚀 Guide de Déploiement - Prévision Agricole IA

Plusieurs options pour déployer votre application Streamlit. Choisissez selon vos besoins.

---

## 🎯 Comparatif des Options

| Option | Coût | Facilité | Flexibilité | Performance | Idéal pour |
|--------|------|---------|-------------|-------------|-----------|
| **Streamlit Cloud** | 🟢 Gratuit | 🟢 Très facile | 🟡 Limitée | 🟡 Moyenne | Prototype/Test |
| **Heroku** | 🟡 7$/mois | 🟢 Facile | 🟡 Moyenne | 🟡 Moyenne | Démarrage |
| **Docker (VPS)** | 🟠 5-15$/mois | 🟠 Moyen | 🟢 Complète | 🟢 Excellente | Production |
| **AWS/GCP** | 🔴 Variable | 🔴 Difficile | 🟢 Complète | 🟢 Excellente | Enterprise |

---

## ✅ OPTION 1 : STREAMLIT CLOUD (Recommended - Gratuit!)

### Excellente pour: Prototypes, démonstrations, **Togo**

### Avantages
- ✅ **100% Gratuit** 
- ✅ 0$ par mois
- ✅ 1 clic de déploiement
- ✅ HTTPS automatique
- ✅ Pas de serveur à gérer
- ✅ Updatesauto du code

### Inconvénients
- ❌ Peut être lent avec beaucoup d'utilisateurs
- ❌ Besoin de GitHub obligatoire
- ❌ Limité à 1 GB RAM

### Étape 1 : Préparer GitHub

```bash
# 1. Créer compte GitHub (gratuit)
# https://github.com/signup

# 2. Créer nouveau repository "agri-ia-prevision"
# - Public (requis pour Streamlit Cloud gratuit)
# - Ajouter README.md

# 3. Cloner en local
git clone https://github.com/VOUS/agri-ia-prevision.git
cd agri-ia-prevision

# 4. Copier le dossier prevision/
cp -r ../prevision/* .

# 5. Créer .gitkeep pour dossier data/ 
touch data/.gitkeep

# 6. Pousser sur GitHub
git add .
git commit -m "Initial commit: Prévision Agricole IA"
git push origin main
```

### Étape 2 : Déployer sur Streamlit Cloud

1. **Aller à** https://share.streamlit.io
2. **Sign up** avec votre compte GitHub
3. **Cliquer** "New app"
4. **Remplir :**
   - Repository: `VOUS/agri-ia-prevision`
   - Branch: `main`
   - Main file path: `app.py`
5. **Cliquer** "Deploy" 🚀

**Attendre 2-3 minutes...**

L'app sera disponible à:
```
https://votre-username-agri-ia-prevision.streamlit.app
```

### Étape 3 : Mises à Jour

Pour mettre à jour l'app:

```bash
# 1. Modifier le code localement
# ...

# 2. Pousser sur GitHub
git add .
git commit -m "Update: [description]"
git push origin main

# 3. Streamlit redéploie AUTOMATIQUEMENT ✓
```

### ⚠️ Important : Gérer le Modèle ML

**Problème** : Le fichier `modele_rendement_agricole.pkl` est trop volumineux pour GitHub.

**Solution** : 

#### Option A : Utiliser Git LFS (Recommandé)

```bash
# 1. Installer Git LFS
# Windows : https://git-lfs.com/ (installer exe)
# Mac : brew install git-lfs
# Linux : sudo apt install git-lfs

# 2. Initialiser LFS
git lfs install

# 3. Ajouter le modèle à LFS
git lfs track "models/*.pkl"

# 4. Pousser
git add models/modele_rendement_agricole.pkl
git commit -m "Add ML model"
git push origin main
```

#### Option B : Télécharger à Runtime (Simple)

Créer `models/download_model.py`:

```python
import os
import urllib.request

MODEL_PATH = "models/modele_rendement_agricole.pkl"
MODEL_URL = "https://votre-url-du-modele"  # Dropbox, Cloud, etc

if not os.path.exists(MODEL_PATH):
    print("Téléchargement du modèle...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("✓ Modèle téléchargé")
```

Ajouter au début de `app.py`:

```python
from models.download_model import MODEL_PATH  # Télécharge auto si manquant
import sys
sys.path.insert(0, str(MODEL_PATH))
```

#### Option C : Héberger le modèle sur Dropbox

1. Uploader `modele_rendement_agricole.pkl` sur Dropbox
2. Créer un lien de partage
3. Remplacer `dl=0` par `dl=1` à la fin
4. Utiliser dans `download_model.py`

---

## ✅ OPTION 2 : HEROKU (7$/mois)

### Excellente pour: Production légère, plus de contrôle

### Prérequis
- Compte Heroku (https://heroku.com)
- Carte de crédit (facturation mensuelle)

### Étape 1 : Préparer Heroku

```bash
# 1. Installer Heroku CLI
# Windows/Mac/Linux : https://devcenter.heroku.com/articles/heroku-cli

# 2. Se connecter
heroku login

# 3. Créer app
heroku create agri-ia-prevision

# 4. Vérifier
heroku apps
```

### Étape 2 : Créer `Procfile` (fichier requiert)

```bash
# À la racine du projet
echo "web: streamlit run app.py" > Procfile
```

### Étape 3 : Créer `runtime.txt`

```bash
echo "python-3.10.12" > runtime.txt
```

### Étape 4 : Mettre à jour `requirements.txt`

Ajouter à la fin:

```
# Pour Heroku
gunicorn==20.1.0
```

### Étape 5 : Créer `.streamlit/config.toml`

Déjà créé! Mais ajouter:

```toml
[server]
headless = true
port = $PORT
enableCORS = false
```

### Étape 6 : Déployer

```bash
# 1. Initialiser Git (si pas déjà fait)
git init
git add .
git commit -m "Deploy to Heroku"

# 2. Ajouter remote Heroku
heroku git:remote -a agri-ia-prevision

# 3. Pousser
git push heroku main

# 4. Voir les logs
heroku logs --tail
```

### Étape 7 : Accéder l'app

```
https://agri-ia-prevision.herokuapp.com
```

### Mise à jour

```bash
git add .
git commit -m "Update"
git push heroku main
```

---

## ✅ OPTION 3 : DOCKER + VPS (Self-Hosted)

### Excellente pour: Production, **Contrôle total**, **Togo**

### Avantages
- ✅ **Contrôle 100%** de l'infrastructure
- ✅ Coût bas (~5-15$ VPS)
- ✅ Performance excellente
- ✅ Données locales
- ✅ Pas de dépendance externe

### Étape 1 : Créer `Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier fichiers
COPY requirements.txt .
COPY . .

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Créer dossiers
RUN mkdir -p data

# Exposer port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Lancer app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Étape 2 : Créer `docker-compose.yml`

```yaml
version: '3.8'

services:
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
    restart: unless-stopped
```

### Étape 3 : Construire l'image

```bash
# À partir du dossier prevision/
docker build -t agri-ia:latest .

# Vérifier
docker images
```

### Étape 4 : Tester localement

```bash
# Lancer container
docker run -p 8501:8501 agri-ia:latest

# Accéder à http://localhost:8501
```

### Étape 5 : Déployer sur VPS

#### Option A : DigitalOcean AppPlatform (Recommendation)

1. **Créer account** https://digitalocean.com
2. **Ajouter carte** (5$/mois basic droplet)
3. **Créer App** :
   - Connecter GitHub
   - Sélectionner repo
   - Branch: main
   - Dockerfile: auto-détecté
4. **Deploy** 🚀

**URL fournie automatiquement**

#### Option B : AWS EC2

```bash
# 1. Créer instance t2.micro (gratuit première année)
# 2. SSH dans instance
ssh -i key.pem ubuntu@instance-ip

# 3. Installer Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# 4. Cloner repo
git clone https://github.com/VOUS/agri-ia-prevision.git
cd agri-ia-prevision

# 5. Lancer
docker-compose up -d

# 6. Vérifier
docker ps
```

**Accéder à** : `http://instance-ip:8501`

#### Option C : Nginx Reverse Proxy (Production)

```nginx
server {
    listen 80;
    server_name agri-ia-prevision.tg;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## ✅ OPTION 4 : AWS/GCP (Enterprise)

### Pour: **Très haute charge**, production critique

### Services
- **AWS EC2** : Instances virtuelles
- **AWS RDS** : Base de données sécurisée
- **AWS S3** : Stockage fichiers
- **CloudFront** : CDN global
- **Lambda** : Fonctions sans serveur

**Trop complexe pour cette doc, consulter AWS/GCP docs**

---

## 🔒 SÉCURITÉ EN PRODUCTION

### Éléments Critiques

#### 1. Variables d'environnement

Créer `.env.production`:

```
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```

Charger dans app:

```python
from dotenv import load_dotenv
import os

load_dotenv(".env.production")
```

#### 2. Authentification (si nécessaire)

Ajouter `components/auth.py`:

```python
import streamlit as st
import hashlib

USERS = {
    "admin": "hashed_password_here",
    "agri_togo": "another_hash"
}

def login():
    """Page de login simple"""
    st.title("LOGIN")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign in"):
        if username in USERS:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if hashed == USERS[username]:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Bad password")
        else:
            st.error("User not found")
```

Utiliser dans `app.py`:

```python
from components.auth import login

if 'logged_in' not in st.session_state:
    login()
    st.stop()

# Rest de l'app...
```

#### 3. HTTPS/SSL

**Streamlit Cloud** : Automatique ✓

**Heroku** : 
```bash
# Activer SSL
heroku config:set FORCE_HTTPS=true
```

**VPS** : Utiliser Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d agri-ia.tg
```

#### 4. Limiter requêtes API

Ajouter rate limiting:

```python
from functools import wraps
import time

call_times = {}

def rate_limit(seconds=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if func.__name__ in call_times:
                if now - call_times[func.__name__] < seconds:
                    st.warning("Trop de requêtes, attendez un peu...")
                    return None
            call_times[func.__name__] = now
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(seconds=30)
def get_real_time_weather(region):
    # ...
```

---

## 📊 MONITORING & LOGS

### Streamlit Cloud

Dans la console Streamlit Cloud:

```
App > Logs > Voir en temps réel
```

### VPS/Docker

```bash
# Voir les logs
docker logs -f agri-ia

# Persister les logs
docker logs agri-ia > app.log 2>&1
tail -f app.log
```

### External : Sentry (Monitoring d'erreurs)

```bash
pip install sentry-sdk
```

```python
# Dans app.py
import sentry_sdk

sentry_sdk.init(
    "https://YOUR-SENTRY-KEY@sentry.io/PROJECT-ID",
    traces_sample_rate=0.1
)
```

---

## 🌍 DOMAINE PERSONNALISÉ

### Ajouter un domaine .tg

1. **Registrar** : OVH, Namecheap, etc
2. **Acheter** : agri-ia-prevision.tg
3. **DNS Records** :

```
A Record: votre-ip-hote
CNAME: yourappdomain.com
```

### Configuration par plateforme

**Streamlit Cloud** :
```
Settings > Custom Domain > Ajouter agri-ia.tg
```

**Heroku** :
```bash
heroku domains:add agri-ia.tg -a agri-ia-prevision
```

---

## 📈 SCALING FUTUR

### Phase 1 : Prototype (ACTUELLEMENT ✓)
- Streamlit Cloud
- 1 instance
- SQLite local

### Phase 2 : Production Légère
- VPS simple Docker
- PostgreSQL sur VPS
- Backup automatique

### Phase 3 : Production à Grande Échelle
- Kubernetes cluster
- PostgreSQL managed
- Redis cache
- CDN global
- Load balancer

---

## ✅ CHECKLIST DÉPLOIEMENT

### Avant de déployer

- [ ] `requirements.txt` à jour
- [ ] `config.py` sans données sensibles
- [ ] Modèle ML en place (`models/`)
- [ ] `.gitignore` correctement setup
- [ ] Pas de print() debugging (utiliser logs)
- [ ] `data/` initialisé (`.gitkeep`)
- [ ] README.md à jour
- [ ] LICENCE ajoutée

### Après déploiement

- [ ] App accessible
- [ ] Toutes les pages chargent
- [ ] Prévisions fonctionnent
- [ ] Exports fonctionnent
- [ ] Logs clairs
- [ ] Performance acceptable

---

## 🎯 RECOMMANDATION FINALE

Pour **Togo** et **démarrage** :

```
1️⃣ STREAMLIT CLOUD (Gratuit)
   → Test rapidement
   → Pas de coûts
   → Ideal pour demo

2️⃣ DOCKER + VPS (5-10$/mois)
   → Une fois validé
   → Contrôle total
   → Plus performant
```

---

## 📞 Support Déploiement

En cas d'erreur:

```bash
# Logs Streamlit Cloud
# Aller dans: App > Logs

# Logs Heroku
heroku logs --tail

# Logs Docker
docker logs -f agri-ia

# Vérifier connexion
curl -v https://votre-app.com
```

---

**Il est maintenant temps de montrer votre app au monde! 🚀🌾**
