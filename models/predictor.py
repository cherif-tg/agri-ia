"""
Module des modèles de prédiction machine learning
Gestion du cache du modèle et calculs de prévisions
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import joblib

from config import (
    MODEL_PATH,
    FACTEURS_IRRIGATION,
    FACTEURS_FERTILISATION,
    SEUIL_RISQUE_ELEVE,
    SEUIL_RISQUE_MOYEN,
    CULTURE_DUREE_JOURS
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache du modèle en mémoire pour éviter les rechargements
_model_cache = None


def load_model(model_path: Path = MODEL_PATH):
    """
    Charge le modèle ML avec cache
    
    Args:
        model_path (Path): Chemin du modèle
        
    Returns:
        object: Modèle ML
        
    Raises:
        FileNotFoundError: Si le modèle n'existe pas
    """
    global _model_cache
    
    if _model_cache is not None:
        logger.debug("Modèle récupéré du cache")
        return _model_cache
    
    if not model_path.exists():
        logger.error(f"Modèle non trouvé: {model_path}")
        raise FileNotFoundError(
            f"Le modèle '{model_path}' n'existe pas. "
            "Veuillez entraîner le modèle d'abord."
        )
    
    try:
        _model_cache = joblib.load(model_path)
        logger.info(f"Modèle chargé: {model_path}")
        return _model_cache
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
        raise


def predict_base_rendement(
    region: str,
    culture: str,
    type_sol: str,
    superficie: float,
    pluviometrie: float,
    temperature: float
) -> float:
    """
    Prédiction de base du rendement via Random Forest
    
    Args:
        region (str): Région agricole
        culture (str): Type de culture
        type_sol (str): Type de sol
        superficie (float): Surface en ha
        pluviometrie (float): Pluviométrie en mm
        temperature (float): Température moyenne en °C
        
    Returns:
        float: Rendement prévu en t/ha
    """
    try:
        model = load_model()
        
        # Préparation des données
        data = pd.DataFrame([{
            "region": region,
            "culture": culture,
            "type_sol": type_sol,
            "surface_ha": superficie,
            "pluviometrie_mm": pluviometrie,
            "temperature_moyenne_c": temperature
        }])
        
        prediction = model.predict(data)
        rendement = round(float(prediction[0]), 2)
        
        logger.info(f"Prédiction: {culture} ({region}) = {rendement} t/ha")
        return rendement
        
    except FileNotFoundError as e:
        logger.error(f"Modèle indisponible: {str(e)}")
        # Retourner une estimation simple basée sur les facteurs
        return estimate_rendement_fallback(culture, pluviometrie, temperature)
    except Exception as e:
        logger.error(f"Erreur prédiction: {str(e)}")
        return estimate_rendement_fallback(culture, pluviometrie, temperature)


def estimate_rendement_fallback(
    culture: str,
    pluviometrie: float,
    temperature: float
) -> float:
    """
    Estimation simple du rendement (fallback si modèle indisponible)
    
    Args:
        culture (str): Type de culture
        pluviometrie (float): Pluviométrie en mm
        temperature (float): Température moyenne
        
    Returns:
        float: Rendement estimé
    """
    logger.warning("Utilisation de l'estimation fallback du rendement")
    
    # Rendements de base approximatifs
    rendements_base = {
        "Maïs": 2.5,
        "Sorgho": 1.8,
        "Mil": 1.5
    }
    
    rendement = rendements_base.get(culture, 2.0)
    
    # Ajustement pluviométrie
    if pluviometrie < 500:
        rendement *= 0.7
    elif pluviometrie < 800:
        rendement *= 0.9
    elif pluviometrie > 1200:
        rendement *= 0.95
    
    # Ajustement température
    if temperature < 20 or temperature > 32:
        rendement *= 0.85
    
    return round(rendement, 2)


def calculate_adjusted_rendement(
    culture: str,
    rendement_base: float,
    pluviometrie: float,
    temperature: float,
    irrigation: str,
    fertilisation: str
) -> float:
    """
    Calcule le rendement ajusté avec facteurs agricoles
    
    Args:
        culture (str): Culture
        rendement_base (float): Rendement de base
        pluviometrie (float): Pluviométrie en mm
        temperature (float): Température en °C
        irrigation (str): Système d'irrigation
        fertilisation (str): Type de fertilisation
        
    Returns:
        float: Rendement ajusté
    """
    # Facteur pluviométrie
    facteur_pluie = min(pluviometrie / 1000, 1.2)
    
    # Facteur température
    facteur_temp = 1.0
    if culture == "Maïs" and (temperature < 25 or temperature > 30):
        facteur_temp = 0.85
    elif culture == "Sorgho" and (temperature < 22 or temperature > 28):
        facteur_temp = 0.85
    elif culture == "Mil" and (temperature < 20 or temperature > 27):
        facteur_temp = 0.85
    
    # Facteurs agricoles
    facteur_irrig = FACTEURS_IRRIGATION.get(irrigation, 1.0)
    facteur_ferti = FACTEURS_FERTILISATION.get(fertilisation, 1.0)
    
    # Variation aléatoire (+/- 5%)
    variation = np.random.uniform(0.95, 1.05)
    
    rendement_ajuste = (
        rendement_base *
        facteur_pluie *
        facteur_temp *
        facteur_irrig *
        facteur_ferti *
        variation
    )
    
    # S'assurer que le rendement est positif
    return round(max(rendement_ajuste, 0.1), 2)


def calculate_risk_level(
    pluviometrie: float,
    temperature: float,
    culture: str
) -> Tuple[str, int]:
    """
    Calcule le niveau de risque climatique
    
    Args:
        pluviometrie (float): Pluviométrie en mm
        temperature (float): Température en °C
        culture (str): Type de culture
        
    Returns:
        Tuple[str, int]: (niveau_risque, pourcentage)
    """
    risque_score = 0
    
    # Paramètres optimaux par culture
    optimums = {
        "Maïs": {"pluie_min": 500, "pluie_opt": 800, "pluie_max": 1200},
        "Sorgho": {"pluie_min": 400, "pluie_opt": 600, "pluie_max": 900},
        "Mil": {"pluie_min": 350, "pluie_opt": 500, "pluie_max": 800}
    }
    
    opt = optimums.get(culture, optimums["Maïs"])
    
    # Évaluation pluviométrie
    if pluviometrie < opt["pluie_min"]:
        risque_score += 50
    elif pluviometrie < opt["pluie_opt"] * 0.8:
        risque_score += 30
    elif pluviometrie > opt["pluie_max"] * 1.2:
        risque_score += 25
    
    # Évaluation température
    if culture == "Maïs":
        if temperature < 20 or temperature > 35:
            risque_score += 20
    elif culture == "Sorgho":
        if temperature < 15 or temperature > 33:
            risque_score += 20
    
    # Déterminer le niveau
    risque_score = min(risque_score, 100)
    
    if risque_score >= SEUIL_RISQUE_ELEVE:
        niveau = "Élevé"
    elif risque_score >= SEUIL_RISQUE_MOYEN:
        niveau = "Moyen"
    else:
        niveau = "Faible"
    
    return niveau, risque_score


def calculate_harvest_date(
    date_semis,
    culture: str
) -> datetime:
    """
    Calcule la date de récolte optimale
    
    Args:
        date_semis: Date de semis
        culture (str): Type de culture
        
    Returns:
        datetime: Date de récolte estimée
    """
    duree = CULTURE_DUREE_JOURS.get(culture, {"min": 90, "max": 120})
    # Prendre une durée moyenne avec légère variation
    jours = int((duree["min"] + duree["max"]) / 2) + np.random.randint(-5, 5)
    
    date_recolte = date_semis + timedelta(days=jours)
    return date_recolte


def generate_prediction(
    region: str,
    culture: str,
    superficie: float,
    date_semis,
    type_sol: str,
    temperature_moy: float,
    pluviometrie: float,
    irrigation: str,
    fertilisation: str
) -> Dict:
    """
    Génère une prévision complète
    
    Args:
        Tous les paramètres de prévision
        
    Returns:
        Dict: Dictionnaire avec tous les résultats
    """
    logger.info(f"Génération prévision: {culture} ({region})")
    
    try:
        # Prédiction de base
        rendement_base = predict_base_rendement(
            region, culture, type_sol, superficie, pluviometrie, temperature_moy
        )
        
        # Ajustement avec facteurs agricoles
        rendement_prevu = calculate_adjusted_rendement(
            culture, rendement_base, pluviometrie, temperature_moy, irrigation, fertilisation
        )
        
        # Production totale
        production_totale = rendement_prevu * superficie
        
        # Évaluation risque
        niveau_risque_str, niveau_risque_int = calculate_risk_level(
            pluviometrie, temperature_moy, culture
        )
        
        # Date récolte
        date_recolte = calculate_harvest_date(date_semis, culture)
        
        prediction = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'region': region,
            'culture': culture,
            'superficie': superficie,
            'type_sol': type_sol,
            'temperature_moyenne': temperature_moy,
            'pluviometrie': pluviometrie,
            'irrigation': irrigation,
            'fertilisation': fertilisation,
            'rendement': rendement_prevu,
            'rendement_base': rendement_base,
            'production': round(production_totale, 2),
            'risque': niveau_risque_str,
            'niveau_risque': niveau_risque_int,
            'date_recolte': date_recolte.strftime("%Y-%m-%d")
        }
        
        logger.info(f"Prévision générée: {rendement_prevu} t/ha - Risque: {niveau_risque_str}")
        return prediction
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de prévision: {str(e)}")
        raise
