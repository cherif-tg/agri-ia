"""
Script de prédiction intégrant les données météo en temps réel
Fichier: predict_with_realtime_weather.py
"""

import joblib
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional


class AgriPredictorWithWeather:
    """Classe pour faire des prédictions avec données météo temps réel"""
    
    def __init__(self, model_path: str = "modele_rendement_agricole.pkl"):
        """
        Initialise le prédicteur
        
        Args:
            model_path: Chemin vers le modèle entraîné
        """
        try:
            self.model = joblib.load(model_path)
            self.model_loaded = True
        except FileNotFoundError:
            print(f"⚠️ Modèle non trouvé: {model_path}")
            self.model_loaded = False
        
        # Coordonnées des régions
        self.regions_coords = {
            "Maritime": {"lat": 6.1256, "lon": 1.2256},
            "Plateaux": {"lat": 6.9000, "lon": 0.8500},
            "Centrale": {"lat": 8.9711, "lon": 1.1056},
            "Kara": {"lat": 9.5511, "lon": 1.1856},
            "Savanes": {"lat": 10.5700, "lon": 0.2200}
        }
    
    def get_weather_data(self, region: str, days_back: int = 30) -> Dict:
        """
        Récupère les données météo en temps réel pour une région
        
        Args:
            region: Nom de la région togolaise
            days_back: Nombre de jours d'historique pour le cumul
            
        Returns:
            Dict avec température moyenne et pluviométrie
        """
        if region not in self.regions_coords:
            raise ValueError(f"Région inconnue: {region}")
        
        coords = self.regions_coords[region]
        
        # 1. Météo actuelle et prévisions (Open-Meteo - GRATUIT)
        url_current = "https://api.open-meteo.com/v1/forecast"
        params_current = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": ["temperature_2m", "relative_humidity_2m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", 
                     "temperature_2m_mean", "precipitation_sum"],
            "timezone": "Africa/Lome",
            "forecast_days": 7
        }
        
        try:
            response = requests.get(url_current, params=params_current, timeout=10)
            response.raise_for_status()
            current_data = response.json()
            
            # Extraction des données actuelles
            current = current_data.get("current", {})
            daily = current_data.get("daily", {})
            
            temp_mean_list = daily.get("temperature_2m_mean", [])
            precip_list = daily.get("precipitation_sum", [])
            
            # 2. Données historiques pour cumul de pluie
            date_end = datetime.now().strftime("%Y-%m-%d")
            date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            url_archive = "https://archive-api.open-meteo.com/v1/archive"
            params_archive = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "start_date": date_start,
                "end_date": date_end,
                "daily": ["temperature_2m_mean", "precipitation_sum"],
                "timezone": "Africa/Lome"
            }
            
            response_archive = requests.get(url_archive, params=params_archive, timeout=15)
            archive_data = response_archive.json()
            
            archive_daily = archive_data.get("daily", {})
            archive_precip = archive_daily.get("precipitation_sum", [])
            archive_temp = archive_daily.get("temperature_2m_mean", [])
            
            # Calculs
            temperature_moyenne = (
                sum(archive_temp) / len(archive_temp) 
                if archive_temp else current.get("temperature_2m", 27.0)
            )
            
            pluviometrie_cumul = sum(archive_precip) if archive_precip else sum(precip_list) * 4
            
            return {
                "success": True,
                "region": region,
                "temperature_actuelle": current.get("temperature_2m", 27.0),
                "temperature_moyenne": round(temperature_moyenne, 1),
                "pluviometrie_mm": round(pluviometrie_cumul, 1),
                "humidite": current.get("relative_humidity_2m", 70),
                "periode_jours": days_back,
                "date_mesure": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            print(f"⚠️ Erreur API météo: {e}")
            return {
                "success": False,
                "error": str(e),
                "temperature_moyenne": 27.0,
                "pluviometrie_mm": 800.0
            }
    
    def predict_rendement(self, 
                         region: str,
                         culture: str,
                         type_sol: str,
                         surface_ha: float,
                         use_real_weather: bool = True,
                         temperature_manuelle: Optional[float] = None,
                         pluviometrie_manuelle: Optional[float] = None) -> Dict:
        """
        Prédit le rendement agricole
        
        Args:
            region: Région agricole
            culture: Type de culture (Maïs, Sorgho, Mil)
            type_sol: Type de sol
            surface_ha: Superficie en hectares
            use_real_weather: Utiliser les données météo temps réel
            temperature_manuelle: Température manuelle (si use_real_weather=False)
            pluviometrie_manuelle: Pluviométrie manuelle (si use_real_weather=False)
            
        Returns:
            Dict avec prédiction et données météo utilisées
        """
        # Récupération des données météo
        if use_real_weather:
            print(f"📡 Récupération météo pour {region}...")
            weather = self.get_weather_data(region)
            
            if weather["success"]:
                temperature = weather["temperature_moyenne"]
                pluviometrie = weather["pluviometrie_mm"]
                print(f"✅ Météo récupérée: {temperature}°C, {pluviometrie}mm")
            else:
                print(f"⚠️ Erreur météo, valeurs par défaut")
                temperature = 27.0
                pluviometrie = 800.0
        else:
            temperature = temperature_manuelle or 27.0
            pluviometrie = pluviometrie_manuelle or 800.0
            weather = {
                "success": False,
                "source": "Manuel"
            }
        
        # Préparation des données pour le modèle
        data = pd.DataFrame([{
            "region": region,
            "culture": culture,
            "type_sol": type_sol,
            "surface_ha": surface_ha,
            "pluviometrie_mm": pluviometrie,
            "temperature_moyenne_c": temperature
        }])
        
        # Prédiction
        if self.model_loaded:
            rendement_prevu = self.model.predict(data)[0]
        else:
            # Simulation simple si modèle non disponible
            base = {"Maïs": 3.5, "Sorgho": 2.8, "Mil": 2.2}
            facteur_pluie = min(pluviometrie / 1000, 1.2)
            facteur_temp = 1.0 if 25 <= temperature <= 30 else 0.85
            rendement_prevu = base.get(culture, 3.0) * facteur_pluie * facteur_temp
        
        production_totale = rendement_prevu * surface_ha
        
        return {
            "rendement_t_ha": round(rendement_prevu, 2),
            "production_totale_t": round(production_totale, 2),
            "surface_ha": surface_ha,
            "donnees_meteo": {
                "temperature_c": temperature,
                "pluviometrie_mm": pluviometrie,
                "source": "Temps réel" if use_real_weather and weather["success"] else "Manuelle",
                "date": weather.get("date_mesure", datetime.now().strftime("%Y-%m-%d %H:%M"))
            },
            "parametres": {
                "region": region,
                "culture": culture,
                "type_sol": type_sol
            }
        }
    
    def predict_batch_regions(self, 
                             culture: str,
                             type_sol: str,
                             surface_ha: float) -> pd.DataFrame:
        """
        Prédit le rendement pour toutes les régions avec météo temps réel
        
        Args:
            culture: Type de culture
            type_sol: Type de sol
            surface_ha: Superficie
            
        Returns:
            DataFrame avec prédictions pour chaque région
        """
        results = []
        
        for region in self.regions_coords.keys():
            print(f"\n📍 Analyse de {region}...")
            prediction = self.predict_rendement(
                region=region,
                culture=culture,
                type_sol=type_sol,
                surface_ha=surface_ha,
                use_real_weather=True
            )
            
            results.append({
                "Région": region,
                "Rendement (t/ha)": prediction["rendement_t_ha"],
                "Production (t)": prediction["production_totale_t"],
                "Température (°C)": prediction["donnees_meteo"]["temperature_c"],
                "Pluviométrie (mm)": prediction["donnees_meteo"]["pluviometrie_mm"],
                "Source": prediction["donnees_meteo"]["source"]
            })
        
        return pd.DataFrame(results)


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Prédiction Agricole avec Météo Temps Réel ===\n")
    
    # Initialisation
    predictor = AgriPredictorWithWeather()
    
    # Exemple 1: Prédiction pour une région avec météo temps réel
    print("\n📊 Exemple 1: Prédiction Maritime avec météo temps réel")
    print("-" * 60)
    
    result = predictor.predict_rendement(
        region="Maritime",
        culture="Maïs",
        type_sol="Argilo-sableux",
        surface_ha=10.0,
        use_real_weather=True
    )
    
    print(f"\n✅ Résultats:")
    print(f"   Rendement prévu: {result['rendement_t_ha']} t/ha")
    print(f"   Production totale: {result['production_totale_t']} tonnes")
    print(f"   Température: {result['donnees_meteo']['temperature_c']}°C")
    print(f"   Pluviométrie: {result['donnees_meteo']['pluviometrie_mm']} mm")
    print(f"   Source: {result['donnees_meteo']['source']}")
    
    # Exemple 2: Comparaison toutes régions
    print("\n\n📊 Exemple 2: Comparaison toutes régions")
    print("-" * 60)
    
    df_regions = predictor.predict_batch_regions(
        culture="Maïs",
        type_sol="Argilo-sableux",
        surface_ha=5.0
    )
    
    print("\n" + df_regions.to_string(index=False))
    
    # Exemple 3: Prédiction avec données manuelles
    print("\n\n📊 Exemple 3: Prédiction avec données manuelles")
    print("-" * 60)
    
    result_manual = predictor.predict_rendement(
        region="Kara",
        culture="Sorgho",
        type_sol="Sableux",
        surface_ha=8.0,
        use_real_weather=False,
        temperature_manuelle=28.5,
        pluviometrie_manuelle=650.0
    )
    
    print(f"\n✅ Résultats:")
    print(f"   Rendement prévu: {result_manual['rendement_t_ha']} t/ha")
    print(f"   Production totale: {result_manual['production_totale_t']} tonnes")
    print(f"   Source météo: {result_manual['donnees_meteo']['source']}")
