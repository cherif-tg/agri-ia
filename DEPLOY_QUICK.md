# ⚡ DÉPLOIEMENT - GUIDE RAPIDE

Choisissez votre option et suivez les étapes.

---

## 🎯 OPTION 1 : STREAMLIT CLOUD (Gratuit - Recommandé pour démarrer)

### 5 minutes, 0 configurations techniques!

```bash
# 1. Go to GitHub
# Créer compte (https://github.com/signup) et repository PUBIC

# 2. Upload code
cd prevision
git init
git add .
git commit -m "Initial"
git branch -M main
git remote add origin https://github.com/VOTRE-USERNAME/agri-ia.git
git push -u origin main

# 3. Go to streamlit.io/cloud
# Sign in avec GitHub > Déployer > Select repo > Deploy

✅ DONE! App live en 2 minutes
URL: https://votre-username-agri-ia.streamlit.app
```

**⚠️ Voir DEPLOYMENT.md "OPTION 1" pour gérer le modèle ML**

---

## 🐳 OPTION 2 : DOCKER LOCAL (Pour tester avant production)

### 3 commandes!

```bash
# 1. Installer Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Lancer
./deploy-docker.sh rebuild
./deploy-docker.sh start

# 3. Accéder
# http://localhost:8501

✅ DONE! App running localement
```

---

## ☁️ OPTION 3 : HEROKU (7$/mois, simple production)

### 5 minutes

```bash
# 1. Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Script de déploiement
chmod +x deploy-heroku.sh
./deploy-heroku.sh

# 3. Attendre 2-3 min

✅ DONE! App live à:
https://agri-ia-prevision.herokuapp.com
```

---

## 🖥️ OPTION 4 : VPS (DigitalOcean, Linode, AWS)

### 15 minutes, meilleur contrôle

```bash
# 1. Créer VPS (5-10$/mois)
# DigitalOcean: https://digitalocean.com/

# 2. SSH dans VPS
ssh root@your-vps-ip

# 3. Sur le serveur
apt update && apt install docker.io docker-compose
git clone https://github.com/VOTRE-USERNAME/agri-ia.git
cd agri-ia
docker-compose up -d

# 4. Configuration domaine
# Pointer DNS vers l'IP du VPS
# Utiliser nginx.conf pour HTTPS

✅ DONE! App à: https://votre-domaine.tg
```

---

## 🔒 CHECKLIST AVANT DÉPLOIEMENT

- [ ] Modèle ML en place: `models/modele_rendement_agricole.pkl`
- [ ] Pas de `.env` ou secrets dans le code
- [ ] `requirements.txt` à jour
- [ ] `README.md` complètement rempli
- [ ] Tester localement: `streamlit run app.py`

---

## 📊 COMPARATIF RAPIDE

| | Streamlit | Docker | Heroku | VPS |
|---|-----------|--------|--------|-----|
| **Coût** | Gratuit | ~5$ | 7$ | 5-10$ |
| **Facilité** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |
| **Time** | 5min | 10min | 5min | 15min |
| **Idéal pour** | Test | Local | Prod | Prod+ |

---

## 🚀 MA RECOMMANDATION

### Étape 1 (MAINTENANT)
```
→ STREAMLIT CLOUD
   ✅ Gratuit, immédiat
   ✅ Idéal pour démo
```

### Étape 2 (Quand production)
```
→ DOCKER + VPS
   ✅ Contrôle total
   ✅ Coût bas
```

---

## ❓ MON APP MARCHE PAS?

```bash
# Logs locaux
streamlit run app.py --logger.level=debug

# Vérifier modèle
ls -la prevision/models/modele_rendement_agricole.pkl

# Vérifier dépendances
pip install -r requirements.txt

# Tester dans Docker
docker build -t test .
docker run -p 8501:8501 test
```

---

## 📞 BESOIN D'AIDE?

Voir [DEPLOYMENT.md](./DEPLOYMENT.md) pour guide complet avec toutes les options.

---

**Prêt à déployer? Commencer par Streamlit Cloud! 🚀**
