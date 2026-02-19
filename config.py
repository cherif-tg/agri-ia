"""
Configuration centralisée pour l'application Prévision Agricole
"""

import os
from pathlib import Path

# ============= CHEMINS =============
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"

# Créer les répertoires s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "predictions.db"
MODEL_PATH = MODELS_DIR / "modele_rendement_agricole.pkl"

# ============= STREAMLIT CONFIG =============
PAGE_CONFIG = {
    "page_title": "Prévision Agricole IA - Togo",
    "page_icon": "🌾",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ============= DONNÉES GÉOGRAPHIQUES =============
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]

REGIONS_COORDINATES = {
    "Maritime": {"lat": 6.1256, "lon": 1.2256},
    "Plateaux": {"lat": 6.9000, "lon": 0.8500},
    "Centrale": {"lat": 8.9711, "lon": 1.1056},
    "Kara": {"lat": 9.5511, "lon": 1.1856},
    "Savanes": {"lat": 10.5700, "lon": 0.2200}
}

# ============= CULTURES =============
CULTURES = ["Maïs", "Sorgho", "Mil"]

CULTURE_DUREE_JOURS = {
    "Maïs": {"min": 85, "max": 95},
    "Sorgho": {"min": 115, "max": 130},
    "Mil": {"min": 95, "max": 110}
}

# ============= PARAMETRES AGRICOLES =============
TYPES_SOL = ["Argileux", "Sableux", "Limoneux", "Argilo-sableux", "Argilo-limoneux"]

SYSTEMES_IRRIGATION = ["Aucun", "Traditionnel", "Goutte à goutte", "Aspersion"]

TYPES_FERTILISATION = ["Aucune", "Organique", "Chimique", "Mixte"]

# Facteurs d'ajustement pour prévisions
FACTEURS_IRRIGATION = {
    "Aucun": 1.0,
    "Traditionnel": 1.1,
    "Goutte à goutte": 1.25,
    "Aspersion": 1.15
}

FACTEURS_FERTILISATION = {
    "Aucune": 0.8,
    "Organique": 1.0,
    "Chimique": 1.2,
    "Mixte": 1.15
}

# ============= PARAMETRES CLIMATIQUES OPTIMAUX =============
OPTIMUMS_CLIMATIQUES = {
    "Maïs": {
        "temperature_min": 25,
        "temperature_max": 30,
        "pluviometrie_min": 500,
        "pluviometrie_optimal": 800,
        "pluviometrie_max": 1200
    },
    "Sorgho": {
        "temperature_min": 22,
        "temperature_max": 28,
        "pluviometrie_min": 400,
        "pluviometrie_optimal": 600,
        "pluviometrie_max": 900
    },
    "Mil": {
        "temperature_min": 20,
        "temperature_max": 27,
        "pluviometrie_min": 350,
        "pluviometrie_optimal": 500,
        "pluviometrie_max": 800
    }
}

# ============= SEUILS DE RISQUE =============
SEUIL_RISQUE_ELEVE = 60  # %
SEUIL_RISQUE_MOYEN = 30  # %

# ============= API MÉTÉO =============
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_TTL = 600  # 10 minutes
WEATHER_TIMEOUT = 10  # secondes

WEATHER_PARAMS = {
    "current": ["temperature_2m", "precipitation", "relative_humidity_2m", "wind_speed_10m"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "timezone": "Africa/Lome",
    "forecast_days": 7
}

# ============= STYLES CSS =============
CUSTOM_CSS = """
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #C8E6C9 0%, #A5D6A7 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #FF9800;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #F44336;
    }
    </style>
"""

# ============= CONTACT =============
CONTACT_INFO = {
    "email": "tengacherif@gmail.com",
    "telephone": "+228 71518061",
    "website": "www.agri-ia-togo.org"
}

# ============= VERSION =============
APP_VERSION = "1.0.0"
APP_YEAR = 2026

# ============= LOGGING =============
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = DATA_DIR / "app.log"
