"""
Module d'export des rapports et données (PDF, CSV, etc.)
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def export_prediction_to_csv(prediction: Dict, output_path: Optional[Path] = None) -> str:
    """
    Exporte une prévision unique au format CSV
    
    Args:
        prediction (Dict): Données de prévision à exporter
        output_path (Path): Chemin de sortie (optionnel)
        
    Returns:
        str: Contenu CSV encodé en UTF-8
    """
    try:
        df = pd.DataFrame([prediction])
        
        # Réordonner les colonnes pour une meilleure lisibilité
        column_order = [
            'date', 'region', 'culture', 'superficie', 'type_sol',
            'irrigation', 'fertilisation', 'temperature_moyenne',
            'pluviometrie', 'rendement', 'production', 'risque', 'date_recolte'
        ]
        
        # Garder seulement les colonnes existantes
        available_cols = [col for col in column_order if col in df.columns]
        df = df[available_cols]
        
        csv_content = df.to_csv(index=False).encode('utf-8')
        
        logger.info(f"Prévision exportée en CSV")
        return csv_content
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export CSV: {str(e)}")
        return "".encode('utf-8')


def export_predictions_to_csv(df: pd.DataFrame) -> str:
    """
    Exporte plusieurs prévisions au format CSV
    
    Args:
        df (pd.DataFrame): DataFrame contenant les prévisions
        
    Returns:
        str: Contenu CSV encodé en UTF-8
    """
    try:
        if df.empty:
            logger.warning("Tentative d'export d'un DataFrame vide")
            return "".encode('utf-8')
        
        # Tri par date de création (plus récent en premier)
        if 'created_at' in df.columns:
            df = df.sort_values('created_at', ascending=False)
        
        csv_content = df.to_csv(index=False).encode('utf-8')
        
        logger.info(f"Export de {len(df)} prévisions en CSV")
        return csv_content
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export CSV: {str(e)}")
        return "".encode('utf-8')


def generate_simple_report(prediction: Dict) -> str:
    """
    Génère un rapport texte simple (peut être convertible en PDF)
    
    Args:
        prediction (Dict): Données de prévision
        
    Returns:
        str: Contenu du rapport en texte
    """
    try:
        report = f"""
================================
    RAPPORT DE PRÉVISION AGRICOLE
================================

Date: {prediction.get('date', 'N/A')}

----- INFORMATIONS EXPLOITATION -----
Région: {prediction.get('region', 'N/A')}
Culture: {prediction.get('culture', 'N/A')}
Superficie: {prediction.get('superficie', 'N/A')} ha
Type de sol: {prediction.get('type_sol', 'N/A')}
Système d'irrigation: {prediction.get('irrigation', 'N/A')}
Type de fertilisation: {prediction.get('fertilisation', 'N/A')}

----- CONDITIONS CLIMATIQUES -----
Température moyenne: {prediction.get('temperature_moyenne', 'N/A')}°C
Pluviométrie: {prediction.get('pluviometrie', 'N/A')} mm

----- RÉSULTATS PRÉVISION -----
Rendement prévu: {prediction.get('rendement', 'N/A')} t/ha
Production totale: {prediction.get('production', 'N/A')} t
Niveau de risque: {prediction.get('risque', 'N/A')}
Date de récolte optimale: {prediction.get('date_recolte', 'N/A')}

================================
    Généré par Système de Prévision Agricole IA - Togo
    Version 1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================
        """
        logger.info("Rapport généré avec succès")
        return report.strip()
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        return ""


def generate_historical_report(df: pd.DataFrame) -> str:
    """
    Génère un rapport d'historique et statistiques
    
    Args:
        df (pd.DataFrame): DataFrame des prévisions
        
    Returns:
        str: Contenu du rapport
    """
    try:
        if df.empty:
            return "Aucune donnée d'historique disponible"
        
        report = f"""
================================
    RAPPORT HISTORIQUE
================================

Date du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

----- STATISTIQUES GLOBALES -----
Nombre total de prévisions: {len(df)}
Rendement moyen: {df['rendement_prevu'].mean():.2f} t/ha
Production totale moyenne: {df['production_totale'].mean():.2f} t
Niveau de risque moyen: {df['niveau_risque'].mean():.1f}%

----- PAR CULTURE -----
"""
        
        for culture in df['culture'].unique():
            df_culture = df[df['culture'] == culture]
            report += f"""
{culture}:
  - Nombre de prévisions: {len(df_culture)}
  - Rendement moyen: {df_culture['rendement_prevu'].mean():.2f} t/ha
  - Production moyenne: {df_culture['production_totale'].mean():.2f} t
  - Risque moyen: {df_culture['niveau_risque'].mean():.1f}%
"""
        
        report += f"""
----- PAR RÉGION -----
"""
        
        for region in df['region'].unique():
            df_region = df[df['region'] == region]
            report += f"""
{region}:
  - Nombre de prévisions: {len(df_region)}
  - Rendement moyen: {df_region['rendement_prevu'].mean():.2f} t/ha
  - Risque moyen: {df_region['niveau_risque'].mean():.1f}%
"""
        
        report += f"""
================================
    Généré par Système de Prévision Agricole IA - Togo
================================
        """
        
        logger.info("Rapport historique généré")
        return report.strip()
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport historique: {str(e)}")
        return ""


def get_export_filename(prefix: str, extension: str) -> str:
    """
    Génère un nom de fichier avec timestamp
    
    Args:
        prefix (str): Préfixe du fichier
        extension (str): Extension du fichier
        
    Returns:
        str: Nom du fichier avec timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"
