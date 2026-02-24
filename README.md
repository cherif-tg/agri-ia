# 🌾 AgroPredict Togo

Application de prévision agricole basée sur le Machine Learning pour le Togo.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## Fonctionnalités

- **Prévisions ML** : Modèle XGBoost + LightGBM optimisé par Optuna (R² ≈ 0.60)
- **Météo en temps réel** : Intégration Open-Meteo (sans clé API)
- **Module RAG** : Upload CSV / Excel / PDF → prédictions batch + visualisations
- **Chatbot AgroBot** : Assistant agricole via Groq API (llama-3.3-70b-versatile)
- **Historique & Rapports** : Suivi des prévisions et exports CSV
- **5 régions** : Maritime, Plateaux, Centrale, Kara, Savanes

## Lancement local

```bash
# 1. Cloner le dépôt
git clone https://github.com/cherif-tg/agri-ia.git
cd agri-ia

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API Groq (optionnel)
cp .env.example .env
# Éditer .env et ajouter GROQ_API_KEY=gsk_...

# 4. Lancer l'application
streamlit run app.py
```

## Déploiement Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez votre compte GitHub
3. Sélectionnez le repo `cherif-tg/agri-ia`
4. Fichier principal : `app.py`
5. Dans **Settings > Secrets**, ajoutez :
   ```toml
   GROQ_API_KEY = "gsk_votre_cle_groq"
   ```

## Structure du projet

```
app.py                  # Point d'entrée Streamlit
config.py               # Configuration centralisée
core/
  ml_model.py           # Modèle XGBoost + LightGBM + Optuna
  weather.py            # API météo Open-Meteo
  data_processor.py     # Traitement CSV/Excel/PDF
modules/
  prediction.py         # Page prévisions
  rag.py                # Upload & analyse de fichiers
  chatbot.py            # AgroBot (Groq)
  visualizations.py     # Graphiques interactifs
  history.py            # Historique
  report.py             # Rapports
data_togo/              # Données agricoles Togo (FAOSTAT)
models/                 # Modèle pré-entraîné (.pkl)
tests/                  # 53 tests pytest
```

## Technologies

| Catégorie | Outils |
|-----------|--------|
| Interface | Streamlit ≥ 1.32 |
| ML | XGBoost 2.0, LightGBM 4.0, Optuna 3.5 |
| Visualisation | Plotly 5.18 |
| Chatbot | Groq API — llama-3.3-70b-versatile |
| Météo | Open-Meteo (gratuit, sans clé) |
| Fichiers | pdfplumber, openpyxl, xlrd |
| Tests | pytest 53/53 ✅ |

## Données

Les données proviennent de [FAOSTAT](https://www.fao.org/faostat/) et couvrent la production agricole du Togo (maïs, sorgho, mil) de 1961 à 2023.

## Licence

MIT
