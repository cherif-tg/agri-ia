"""
Configuration pour les API météo
Fichier: config_weather.py
"""

import os
from typing import Optional

class WeatherConfig:
    """Configuration centralisée pour les API météo"""
    
    # API Open-Meteo (GRATUIT - recommandé)
    # Pas de clé nécessaire, limite: ~10,000 requêtes/jour
    USE_OPEN_METEO = True
    OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    # API OpenWeatherMap (nécessite inscription)
    # Plan gratuit: 1,000 appels/jour
    # Inscrivez-vous sur: https://openweathermap.org/api
    OPENWEATHERMAP_API_KEY: Optional[str] = os.getenv("OPENWEATHERMAP_API_KEY", None)
    OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    # Configuration générale
    REQUEST_TIMEOUT = 10  # secondes
    CACHE_DURATION = 600  # 10 minutes
    
    # Coordonnées géographiques des régions du Togo
    REGIONS_TOGO = {
        "Maritime": {
            "lat": 6.1256,
            "lon": 1.2256,
            "altitude": 20,
            "description": "Région de Lomé, climat tropical"
        },
        "Plateaux": {
            "lat": 6.9000,
            "lon": 0.8500,
            "altitude": 450,
            "description": "Région de Kpalimé, climat sub-équatorial"
        },
        "Centrale": {
            "lat": 8.9711,
            "lon": 1.1056,
            "altitude": 340,
            "description": "Région de Sokodé, climat tropical de transition"
        },
        "Kara": {
            "lat": 9.5511,
            "lon": 1.1856,
            "altitude": 370,
            "description": "Région de Kara, climat soudanien"
        },
        "Savanes": {
            "lat": 10.5700,
            "lon": 0.2200,
            "altitude": 300,
            "description": "Région de Dapaong, climat sahélien"
        }
    }
    
    # Valeurs par défaut en cas d'erreur API
    DEFAULT_VALUES = {
        "temperature_moyenne": 27.0,  # °C
        "pluviometrie_annuelle": 800.0,  # mm
        "humidite": 70,  # %
        "vitesse_vent": 10  # km/h
    }
    
    @classmethod
    def get_api_provider(cls) -> str:
        """Retourne le provider API à utiliser"""
        if cls.USE_OPEN_METEO:
            return "open-meteo"
        elif cls.OPENWEATHERMAP_API_KEY:
            return "openweathermap"
        else:
            return "open-meteo"  # Fallback sur le gratuit
    
    @classmethod
    def is_configured(cls) -> bool:
        """Vérifie si au moins une API est configurée"""
        return cls.USE_OPEN_METEO or cls.OPENWEATHERMAP_API_KEY is not None


# Instructions pour obtenir une clé API OpenWeatherMap (optionnel)
OPENWEATHERMAP_SETUP_INSTRUCTIONS = """
Pour utiliser OpenWeatherMap (optionnel):

1. Créez un compte sur: https://openweathermap.org/api
2. Allez dans "API Keys" de votre profil
3. Copiez votre clé API
4. Ajoutez-la dans un fichier .env:
   
   OPENWEATHERMAP_API_KEY=votre_cle_ici

5. Ou définissez la variable d'environnement:
   
   export OPENWEATHERMAP_API_KEY=votre_cle_ici

Note: Open-Meteo est GRATUIT et ne nécessite aucune clé API.
Il est recommandé pour ce projet.
"""


if __name__ == "__main__":
    print("=== Configuration API Météo ===\n")
    print(f"Provider actif: {WeatherConfig.get_api_provider()}")
    print(f"Configuration valide: {WeatherConfig.is_configured()}")
    print(f"\nRégions disponibles: {list(WeatherConfig.REGIONS_TOGO.keys())}")
    
    if not WeatherConfig.USE_OPEN_METEO and not WeatherConfig.OPENWEATHERMAP_API_KEY:
        print("\n⚠️ Aucune API configurée!")
        print(OPENWEATHERMAP_SETUP_INSTRUCTIONS)
