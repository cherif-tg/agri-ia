"""
Module de validation des données d'entrée
"""

import logging
from typing import Tuple, Optional
from config import (
    REGIONS,
    CULTURES,
    TYPES_SOL,
    SYSTEMES_IRRIGATION,
    TYPES_FERTILISATION
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception levée lors d'une erreur de validation"""
    pass


def validate_region(region: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le nom de la région
    
    Args:
        region (str): Nom de la région
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if not region:
        return False, "Region vide"
    
    if region not in REGIONS:
        return False, f"Région '{region}' non valide. Choisir parmi: {', '.join(REGIONS)}"
    
    return True, None


def validate_culture(culture: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le nom de la culture
    
    Args:
        culture (str): Nom de la culture
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if not culture:
        return False, "Culture vide"
    
    if culture not in CULTURES:
        return False, f"Culture '{culture}' non valide. Choisir parmi: {', '.join(CULTURES)}"
    
    return True, None


def validate_superficie(superficie: float) -> Tuple[bool, Optional[str]]:
    """
    Valide la superficie en hectares
    
    Args:
        superficie (float): Surface en hectares
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if superficie <= 0:
        return False, "La superficie doit être positive"
    
    if superficie > 10000:
        return False, "La superficie dépasse la limite raisonnable (10000 ha)"
    
    return True, None


def validate_temperature(temperature: float) -> Tuple[bool, Optional[str]]:
    """
    Valide la température en °C
    
    Args:
        temperature (float): Température en °C
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if temperature < 10:
        return False, "Température trop basse (minimum 10°C)"
    
    if temperature > 50:
        return False, "Température trop haute (maximum 50°C)"
    
    return True, None


def validate_pluviometrie(pluviometrie: float) -> Tuple[bool, Optional[str]]:
    """
    Valide la pluviométrie en mm
    
    Args:
        pluviometrie (float): Cumul de pluie en mm
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if pluviometrie < 0:
        return False, "La pluviométrie ne peut pas être négative"
    
    if pluviometrie > 5000:
        return False, "Pluviométrie trop élevée (maximum 5000 mm)"
    
    return True, None


def validate_type_sol(type_sol: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le type de sol
    
    Args:
        type_sol (str): Type de sol
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if not type_sol:
        return False, "Type de sol vide"
    
    if type_sol not in TYPES_SOL:
        return False, f"Type de sol '{type_sol}' non valide"
    
    return True, None


def validate_irrigation(irrigation: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le système d'irrigation
    
    Args:
        irrigation (str): Système d'irrigation
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if not irrigation:
        return False, "Système d'irrigation vide"
    
    if irrigation not in SYSTEMES_IRRIGATION:
        return False, f"Système d'irrigation '{irrigation}' non valide"
    
    return True, None


def validate_fertilisation(fertilisation: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le type de fertilisation
    
    Args:
        fertilisation (str): Type de fertilisation
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    if not fertilisation:
        return False, "Type de fertilisation vide"
    
    if fertilisation not in TYPES_FERTILISATION:
        return False, f"Type de fertilisation '{fertilisation}' non valide"
    
    return True, None


def validate_all_inputs(
    region: str,
    culture: str,
    superficie: float,
    temperature: float,
    pluviometrie: float,
    type_sol: str,
    irrigation: str,
    fertilisation: str
) -> Tuple[bool, Optional[str]]:
    """
    Valide tous les inputs d'un formulaire de prévision
    
    Args:
        Tous les paramètres de prévision
        
    Returns:
        Tuple[bool, Optional[str]]: (valide, message d'erreur)
    """
    validators = [
        (validate_region, region, "région"),
        (validate_culture, culture, "culture"),
        (validate_superficie, superficie, "superficie"),
        (validate_temperature, temperature, "température"),
        (validate_pluviometrie, pluviometrie, "pluviométrie"),
        (validate_type_sol, type_sol, "type_sol"),
        (validate_irrigation, irrigation, "irrigation"),
        (validate_fertilisation, fertilisation, "fertilisation")
    ]
    
    for validator, value, field_name in validators:
        is_valid, error_msg = validator(value)
        if not is_valid:
            logger.warning(f"Validation échouée pour {field_name}: {error_msg}")
            return False, error_msg
    
    return True, None
