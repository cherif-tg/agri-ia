"""
Module de gestion des données météorologiques en temps réel
"""

import requests
import logging
from typing import Dict, Optional
from config import (
    WEATHER_API_URL,
    WEATHER_TIMEOUT,
    WEATHER_PARAMS,
    REGIONS_COORDINATES
)

logger = logging.getLogger(__name__)


def get_real_time_weather(region: str) -> Dict:
    """
    Récupère les données météo en temps réel via Open-Meteo (GRATUIT)
    
    Args:
        region (str): Nom de la région agricole du Togo
        
    Returns:
        Dict: Données météorologiques avec clés:
            - success (bool): Succès de la requête
            - temperature_actuelle (float): Température actuelle en °C
            - temperature_moyenne (float): Température moyenne sur 7 jours
            - precipitation_cumul (float): Cumul de précipitations en mm
            - humidite (int): Humidité relative en %
            - vitesse_vent (float): Vitesse du vent en km/h
            - error (str, optional): Message d'erreur si success=False
    """
    if region not in REGIONS_COORDINATES:
        logger.error(f"Région inconnue: {region}")
        return {
            "success": False,
            "error": f"Région '{region}' non trouvée"
        }
    
    try:
        coords = REGIONS_COORDINATES[region]
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            **WEATHER_PARAMS
        }
        
        logger.info(f"Récupération météo pour {region}")
        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=WEATHER_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        # Calculs statistiques
        precipitation_sum = daily.get("precipitation_sum", [])
        precipitation_cumul = sum(precipitation_sum) if precipitation_sum else 0
        
        temp_max_list = daily.get("temperature_2m_max", [])
        temp_moyenne = (
            sum(temp_max_list) / len(temp_max_list)
            if temp_max_list
            else current.get("temperature_2m", 27)
        )
        
        logger.info(f"Météo récupérée avec succès pour {region}")
        return {
            "success": True,
            "temperature_actuelle": round(current.get("temperature_2m", 27), 1),
            "temperature_moyenne": round(temp_moyenne, 1),
            "precipitation_cumul": round(precipitation_cumul, 1),
            "humidite": current.get("relative_humidity_2m", 60),
            "vitesse_vent": round(current.get("wind_speed_10m", 0), 1)
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout API météo pour {region}")
        return {
            "success": False,
            "error": "Timeout - Vérifiez votre connexion Internet",
            "temperature_moyenne": 27.0,
            "precipitation_cumul": 800.0
        }
    except requests.exceptions.ConnectionError:
        logger.error(f"Erreur connexion API météo")
        return {
            "success": False,
            "error": "Erreur de connexion",
            "temperature_moyenne": 27.0,
            "precipitation_cumul": 800.0
        }
    except Exception as e:
        logger.error(f"Erreur API météo: {str(e)}")
        return {
            "success": False,
            "error": f"Erreur: {str(e)}",
            "temperature_moyenne": 27.0,
            "precipitation_cumul": 800.0
        }


def validate_weather_data(weather_data: Dict) -> bool:
    """
    Valide les données météorologiques récupérées
    
    Args:
        weather_data (Dict): Données météo à valider
        
    Returns:
        bool: True si valides, False sinon
    """
    if not weather_data.get("success"):
        return False
    
    required_keys = [
        "temperature_moyenne",
        "precipitation_cumul",
        "humidite",
        "vitesse_vent"
    ]
    
    return all(key in weather_data for key in required_keys)
