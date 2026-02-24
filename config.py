"""
Configuration globale de l'application AgroPredict Togo.
Centralise toutes les constantes, paramètres et clés d'environnement.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
DATA_DIR      = BASE_DIR / "data_togo"
MODELS_DIR    = BASE_DIR / "models"
ASSETS_DIR    = BASE_DIR / "assets"
TEMP_DIR      = BASE_DIR / "temp"

# Créer les dossiers manquants au démarrage
for _dir in [MODELS_DIR, TEMP_DIR]:
    _dir.mkdir(exist_ok=True)

# ─── Chemins des fichiers modèle ─────────────────────────────────────────────
MODEL_PATH    = MODELS_DIR / "agro_predict_model.pkl"
DATA_CSV_PATH = DATA_DIR  / "donnees_agricoles_togo.csv"

# ─── API Keys ─────────────────────────────────────────────────────────────────
# Lit depuis Streamlit Cloud Secrets (priorité) ou .env (local)
def _get_groq_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    except Exception:
        return os.getenv("GROQ_API_KEY", "")

GROQ_API_KEY  = _get_groq_key()

# ─── Paramètres métier ────────────────────────────────────────────────────────
APP_NAME      = "AgroPredict Togo"
APP_VERSION   = "2.0"
APP_ICON      = "🌾"

REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]

CULTURES = ["Maïs", "Sorgho", "Mil"]

TYPES_SOL = [
    "Argileux",
    "Sableux",
    "Limoneux",
    "Argilo-sableux",
    "Argilo-limoneux",
]

REGIONS_COORDINATES = {
    "Maritime": {"lat": 6.1256,  "lon": 1.2256,  "ville": "Lomé"},
    "Plateaux": {"lat": 6.9000,  "lon": 0.8500,  "ville": "Kpalimé"},
    "Centrale": {"lat": 8.9711,  "lon": 1.1056,  "ville": "Sokodé"},
    "Kara":     {"lat": 9.5511,  "lon": 1.1856,  "ville": "Kara"},
    "Savanes":  {"lat": 10.5700, "lon": 0.2200,  "ville": "Dapaong"},
}

# Pluviométrie moyenne annuelle par région (mm)
PLUVIO_REGION = {
    "Maritime": 900,
    "Plateaux": 1200,
    "Centrale": 1100,
    "Kara":     1000,
    "Savanes":  800,
}

# ─── Groq / LLM ───────────────────────────────────────────────────────────────
GROQ_MODEL    = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 1024
GROQ_TEMPERATURE = 0.5

SYSTEM_PROMPT_CHATBOT = (
    "Tu es AgroBot, un assistant expert en agronomie et agriculture tropicale spécialisé "
    "sur le Togo et l'Afrique de l'Ouest. Tu aides les agriculteurs et les techniciens "
    "agricoles à analyser leurs données, interpréter les prévisions de rendement, "
    "comprendre les conditions climatiques et prendre de meilleures décisions. "
    "Tes réponses sont précises, bienveillantes et adaptées au contexte local. "
    "Tu t'exprimes en français sauf si on te demande autrement."
)

# ─── Thème couleurs ───────────────────────────────────────────────────────────
COLOR_PRIMARY   = "#1B5E20"   # Vert foncé
COLOR_SECONDARY = "#4CAF50"   # Vert
COLOR_ACCENT    = "#FF8F00"   # Orange/ambre
COLOR_BG        = "#F1F8E9"   # Vert très clair
COLOR_CARD_BG   = "#FFFFFF"
COLOR_TEXT      = "#212121"
COLOR_MUTED     = "#757575"
COLOR_DANGER    = "#C62828"
COLOR_WARNING   = "#F57F17"
COLOR_SUCCESS   = "#2E7D32"
