"""
Module de gestion de la base de données SQLite
Persistance des prévisions historiques
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire de la base de données SQLite"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialise le gestionnaire de base de données
        
        Args:
            db_path (Path): Chemin vers la base de données
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """
        Crée une connexion à la base de données
        
        Returns:
            sqlite3.Connection: Connexion à la DB
        """
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialise la structure de la base de données"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Table des prévisions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_creation TEXT NOT NULL,
                        region TEXT NOT NULL,
                        culture TEXT NOT NULL,
                        superficie REAL NOT NULL,
                        temperature_moyenne REAL NOT NULL,
                        pluviometrie REAL NOT NULL,
                        type_sol TEXT NOT NULL,
                        irrigation TEXT NOT NULL,
                        fertilisation TEXT NOT NULL,
                        rendement_prevu REAL NOT NULL,
                        production_totale REAL NOT NULL,
                        niveau_risque INTEGER NOT NULL,
                        risque_niveau TEXT NOT NULL,
                        date_recolte TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Base de données initialisée / vérifiée")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation DB: {str(e)}")
            raise
    
    def save_prediction(self, prediction: Dict) -> bool:
        """
        Sauvegarde une prévision dans la base de données
        
        Args:
            prediction (Dict): Dictionnaire contenant les données de prévision
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO predictions (
                        date_creation, region, culture, superficie,
                        temperature_moyenne, pluviometrie, type_sol,
                        irrigation, fertilisation, rendement_prevu,
                        production_totale, niveau_risque, risque_niveau,
                        date_recolte
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prediction.get('date', datetime.now().strftime("%Y-%m-%d %H:%M")),
                    prediction.get('region'),
                    prediction.get('culture'),
                    prediction.get('superficie'),
                    prediction.get('temperature_moyenne'),
                    prediction.get('pluviometrie'),
                    prediction.get('type_sol'),
                    prediction.get('irrigation'),
                    prediction.get('fertilisation'),
                    prediction.get('rendement'),
                    prediction.get('production'),
                    prediction.get('niveau_risque', 0),
                    prediction.get('risque'),
                    prediction.get('date_recolte')
                ))
                
                conn.commit()
                logger.info(f"Prévision sauvegardée: {prediction.get('culture')} - {prediction.get('region')}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    def get_all_predictions(self) -> pd.DataFrame:
        """
        Récupère toutes les prévisions
        
        Returns:
            pd.DataFrame: DataFrame contenant toutes les prévisions
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM predictions ORDER BY created_at DESC",
                    conn
                )
                logger.info(f"Récupération de {len(df)} prévisions")
                return df
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération: {str(e)}")
            return pd.DataFrame()
    
    def get_predictions_by_region(self, region: str) -> pd.DataFrame:
        """
        Récupère les prévisions d'une région spécifique
        
        Args:
            region (str): Nom de la région
            
        Returns:
            pd.DataFrame: Prévisions de la région
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM predictions WHERE region = ? ORDER BY created_at DESC",
                    conn,
                    params=(region,)
                )
                return df
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération par région: {str(e)}")
            return pd.DataFrame()
    
    def get_predictions_by_culture(self, culture: str) -> pd.DataFrame:
        """
        Récupère les prévisions d'une culture spécifique
        
        Args:
            culture (str): Nom de la culture
            
        Returns:
            pd.DataFrame: Prévisions de la culture
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    "SELECT * FROM predictions WHERE culture = ? ORDER BY created_at DESC",
                    conn,
                    params=(culture,)
                )
                return df
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération par culture: {str(e)}")
            return pd.DataFrame()
    
    def delete_all_predictions(self) -> bool:
        """
        Supprime toutes les prévisions (attention!)
        
        Returns:
            bool: True si succès
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM predictions")
                conn.commit()
                logger.warning("Toutes les prévisions ont été supprimées")
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Récupère les statistiques globales
        
        Returns:
            Dict: Statistiques (moyennes, totaux, etc.)
        """
        try:
            df = self.get_all_predictions()
            
            if df.empty:
                return {
                    "total_predictions": 0,
                    "average_yield": 0,
                    "total_production": 0,
                    "average_risk": 0
                }
            
            return {
                "total_predictions": len(df),
                "average_yield": round(df['rendement_prevu'].mean(), 2),
                "total_production": round(df['production_totale'].sum(), 2),
                "average_risk": round(df['niveau_risque'].mean(), 1),
                "cultures": df['culture'].unique().tolist(),
                "regions": df['region'].unique().tolist()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats: {str(e)}")
            return {}
