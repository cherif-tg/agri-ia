"""
Module pour récupérer des données météorologiques en temps réel
Supporte OpenWeatherMap et Open-Meteo (gratuit sans clé API)
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json


class WeatherAPI:
    """Classe pour gérer les appels aux API météo"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "open-meteo"):
        """
        Initialisation de l'API météo
        
        Args:
            api_key: Clé API pour OpenWeatherMap (optionnel si provider="open-meteo")
            provider: "openweathermap" ou "open-meteo" (gratuit, pas de clé nécessaire)
        """
        self.api_key = api_key
        self.provider = provider
        
        # Coordonnées des régions du Togo
        self.regions_coordinates = {
            "Maritime": {"lat": 6.1256, "lon": 1.2256},  # Lomé
            "Plateaux": {"lat": 6.9000, "lon": 0.8500},  # Kpalimé
            "Centrale": {"lat": 8.9711, "lon": 1.1056},  # Sokodé
            "Kara": {"lat": 9.5511, "lon": 1.1856},      # Kara
            "Savanes": {"lat": 10.5700, "lon": 0.2200}   # Dapaong
        }
    
    def get_current_weather_open_meteo(self, region: str) -> Dict:
        """
        Récupère la météo actuelle via Open-Meteo (GRATUIT, sans clé API)
        
        Args:
            region: Nom de la région togolaise
            
        Returns:
            Dict avec température et précipitations
        """
        if region not in self.regions_coordinates:
            raise ValueError(f"Région inconnue: {region}")
        
        coords = self.regions_coordinates[region]
        
        # API Open-Meteo - GRATUIT, pas de clé nécessaire
        url = "https://api.open-meteo.com/v1/forecast"
        
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": ["temperature_2m", "precipitation", "relative_humidity_2m", 
                       "wind_speed_10m", "weather_code"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                     "precipitation_hours"],
            "timezone": "Africa/Lome",
            "forecast_days": 7
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            # Calcul des cumuls
            precipitation_cumul = sum(daily.get("precipitation_sum", [])) if daily else 0
            temp_moyenne = (
                sum(daily.get("temperature_2m_max", [])) / len(daily.get("temperature_2m_max", []))
                if daily.get("temperature_2m_max") else current.get("temperature_2m", 0)
            )
            
            return {
                "success": True,
                "region": region,
                "temperature_actuelle": current.get("temperature_2m", 0),
                "temperature_moyenne": round(temp_moyenne, 1),
                "precipitation_actuelle": current.get("precipitation", 0),
                "precipitation_cumul_7j": round(precipitation_cumul, 1),
                "humidite": current.get("relative_humidity_2m", 0),
                "vitesse_vent": current.get("wind_speed_10m", 0),
                "timestamp": current.get("time", datetime.now().isoformat()),
                "provider": "Open-Meteo"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}",
                "region": region
            }
    
    def get_current_weather_openweathermap(self, region: str) -> Dict:
        """
        Récupère la météo actuelle via OpenWeatherMap (nécessite une clé API)
        
        Args:
            region: Nom de la région togolaise
            
        Returns:
            Dict avec température et précipitations
        """
        if not self.api_key:
            raise ValueError("Clé API OpenWeatherMap requise")
        
        if region not in self.regions_coordinates:
            raise ValueError(f"Région inconnue: {region}")
        
        coords = self.regions_coordinates[region]
        
        # API OpenWeatherMap - Météo actuelle
        url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": self.api_key,
            "units": "metric",  # Celsius
            "lang": "fr"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Récupération des prévisions 5 jours pour les cumuls
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params, timeout=10)
            forecast_data = forecast_response.json()
            
            # Calcul du cumul de pluie sur 5 jours
            precipitation_cumul = 0
            if "list" in forecast_data:
                for item in forecast_data["list"]:
                    if "rain" in item and "3h" in item["rain"]:
                        precipitation_cumul += item["rain"]["3h"]
            
            return {
                "success": True,
                "region": region,
                "temperature_actuelle": data["main"]["temp"],
                "temperature_moyenne": data["main"]["temp"],
                "temperature_min": data["main"]["temp_min"],
                "temperature_max": data["main"]["temp_max"],
                "precipitation_actuelle": data.get("rain", {}).get("1h", 0),
                "precipitation_cumul_5j": round(precipitation_cumul, 1),
                "humidite": data["main"]["humidity"],
                "pression": data["main"]["pressure"],
                "vitesse_vent": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
                "provider": "OpenWeatherMap"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}",
                "region": region
            }
    
    def get_historical_weather_open_meteo(self, region: str, 
                                          date_debut: str, 
                                          date_fin: str) -> Dict:
        """
        Récupère les données météo historiques
        
        Args:
            region: Nom de la région
            date_debut: Date de début (format: YYYY-MM-DD)
            date_fin: Date de fin (format: YYYY-MM-DD)
            
        Returns:
            Dict avec données historiques
        """
        if region not in self.regions_coordinates:
            raise ValueError(f"Région inconnue: {region}")
        
        coords = self.regions_coordinates[region]
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": date_debut,
            "end_date": date_fin,
            "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
                     "precipitation_sum"],
            "timezone": "Africa/Lome"
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            
            # Calculs statistiques
            temp_max_list = daily.get("temperature_2m_max", [])
            temp_min_list = daily.get("temperature_2m_min", [])
            temp_mean_list = daily.get("temperature_2m_mean", [])
            precip_list = daily.get("precipitation_sum", [])
            
            return {
                "success": True,
                "region": region,
                "periode": f"{date_debut} à {date_fin}",
                "temperature_max_moyenne": round(sum(temp_max_list) / len(temp_max_list), 1) if temp_max_list else 0,
                "temperature_min_moyenne": round(sum(temp_min_list) / len(temp_min_list), 1) if temp_min_list else 0,
                "temperature_moyenne": round(sum(temp_mean_list) / len(temp_mean_list), 1) if temp_mean_list else 0,
                "precipitation_totale": round(sum(precip_list), 1),
                "precipitation_moyenne_jour": round(sum(precip_list) / len(precip_list), 1) if precip_list else 0,
                "nombre_jours": len(temp_mean_list),
                "details": {
                    "dates": daily.get("time", []),
                    "temperatures_max": temp_max_list,
                    "temperatures_min": temp_min_list,
                    "precipitations": precip_list
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}",
                "region": region
            }
    
    def get_weather(self, region: str) -> Dict:
        """
        Méthode principale pour récupérer la météo
        Utilise automatiquement le bon provider
        
        Args:
            region: Nom de la région
            
        Returns:
            Dict avec données météo
        """
        if self.provider == "open-meteo":
            return self.get_current_weather_open_meteo(region)
        elif self.provider == "openweathermap":
            return self.get_current_weather_openweathermap(region)
        else:
            raise ValueError(f"Provider inconnu: {self.provider}")
    
    def get_weather_for_prediction(self, region: str, 
                                   jours_historique: int = 30) -> Tuple[float, float]:
        """
        Récupère les données météo formatées pour le modèle de prévision
        
        Args:
            region: Nom de la région
            jours_historique: Nombre de jours d'historique pour le cumul de pluie
            
        Returns:
            Tuple (temperature_moyenne_c, pluviometrie_mm)
        """
        # Météo actuelle
        current = self.get_weather(region)
        
        if not current["success"]:
            # Valeurs par défaut en cas d'erreur
            print(f"Avertissement: {current.get('error', 'Erreur inconnue')}")
            return (27.0, 800.0)  # Valeurs moyennes pour le Togo
        
        # Données historiques pour le cumul de pluie
        date_fin = datetime.now().strftime("%Y-%m-%d")
        date_debut = (datetime.now() - timedelta(days=jours_historique)).strftime("%Y-%m-%d")
        
        historical = self.get_historical_weather_open_meteo(region, date_debut, date_fin)
        
        temperature = current.get("temperature_moyenne", 27.0)
        
        if historical["success"]:
            pluviometrie = historical.get("precipitation_totale", 800.0)
        else:
            # Utiliser le cumul court terme si l'historique échoue
            pluviometrie = current.get("precipitation_cumul_7j", 800.0) * (jours_historique / 7)
        
        return (round(temperature, 1), round(pluviometrie, 1))


# Fonction utilitaire pour une utilisation simple
def obtenir_meteo_region(region: str, api_key: Optional[str] = None) -> Dict:
    """
    Fonction simple pour obtenir la météo d'une région
    
    Args:
        region: Nom de la région togolaise
        api_key: Clé API OpenWeatherMap (optionnel, utilise Open-Meteo par défaut)
        
    Returns:
        Dict avec les données météo
    
    Exemple:
        >>> meteo = obtenir_meteo_region("Maritime")
        >>> print(f"Température: {meteo['temperature_actuelle']}°C")
    """
    provider = "openweathermap" if api_key else "open-meteo"
    api = WeatherAPI(api_key=api_key, provider=provider)
    return api.get_weather(region)


# Exemple d'utilisation
if __name__ == "__main__":
    # Test avec Open-Meteo (GRATUIT, pas de clé nécessaire)
    print("=== Test avec Open-Meteo (GRATUIT) ===\n")
    
    api_gratuit = WeatherAPI(provider="open-meteo")
    
    for region in ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]:
        print(f"\n Région: {region}")
        meteo = api_gratuit.get_weather(region)
        
        if meteo["success"]:
            print(f"   Temperature actuelle: {meteo['temperature_actuelle']}°C")
            print(f"   Temperature moyenne: {meteo['temperature_moyenne']}°C")
            print(f"   Precipitations (7j): {meteo['precipitation_cumul_7j']} mm")
            print(f"   Humidité: {meteo['humidite']}%")
        else:
            print(f"    Erreur: {meteo['error']}")
    
    # Test données pour prévision
    print("\n\n=== Données formatées pour le modèle ===\n")
    temp, pluie = api_gratuit.get_weather_for_prediction("Maritime")
    print(f"Temperature moyenne: {temp}°C")
    print(f"Pluviometrie cumulee (30j): {pluie} mm")
    
    # Test avec OpenWeatherMap (nécessite une clé API)
    # Décommentez et ajoutez votre clé pour tester
    """
    print("\n\n=== Test avec OpenWeatherMap ===\n")
    api_owm = WeatherAPI(api_key="VOTRE_CLE_API_ICI", provider="openweathermap")
    meteo_owm = api_owm.get_weather("Maritime")
    print(json.dumps(meteo_owm, indent=2, ensure_ascii=False))
    """
