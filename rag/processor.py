"""
Data processor module for RAG
Cleans and prepares uploaded data
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and clean RAG data"""
    
    @staticmethod
    def identify_columns(df: pd.DataFrame) -> Dict[str, str]:
        """Auto-identify important columns"""
        
        column_mapping = {
            'region': None,
            'culture': None,
            'superficie': None,
            'temperature': None,
            'pluviometrie': None,
            'type_sol': None,
            'rendement': None
        }
        
        col_lower = [col.lower().strip() for col in df.columns]
        
        patterns = {
            'region': ['région', 'region', 'loc', 'location', 'area', 'zone'],
            'culture': ['culture', 'crop', 'type_culture', 'crop_type'],
            'superficie': ['superfici', 'surface', 'hectare', 'ha', 'area_ha'],
            'temperature': ['temp', 'température', 'degree', '°c', 'celsius'],
            'pluviometrie': ['pluie', 'rainfall', 'précip', 'precipitation', 'pluvial'],
            'type_sol': ['sol', 'soil', 'type_sol', 'soil_type'],
            'rendement': ['rendement', 'yield', 'production', 'tonnes', 'tonneage']
        }
        
        for field, keywords in patterns.items():
            for i, col in enumerate(col_lower):
                for keyword in keywords:
                    if keyword in col or col in keyword:
                        column_mapping[field] = df.columns[i]
                        break
                if column_mapping[field]:
                    break
        
        logger.info(f"Identified columns: {column_mapping}")
        return column_mapping
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean data"""
        
        df_clean = df.copy()
        
        # Remove empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Remove empty columns
        df_clean = df_clean.dropna(axis=1, how='all')
        
        # Convert to numeric
        numeric_cols = df_clean.select_dtypes(include=['object']).columns
        
        for col in numeric_cols:
            try:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            except:
                pass
        
        # Remove duplicates
        initial_len = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        removed = initial_len - len(df_clean)
        
        if removed > 0:
            logger.info(f"Removed {removed} duplicates")
        
        logger.info(f"Data cleaned: {len(df_clean)} rows")
        return df_clean
    
    @staticmethod
    def normalize_values(df: pd.DataFrame, column_mapping: Dict) -> pd.DataFrame:
        """Normalize values for predictions"""
        
        df_norm = df.copy()
        
        # Normalize temperature (ensure Celsius)
        if column_mapping['temperature']:
            temp_col = column_mapping['temperature']
            if temp_col in df_norm.columns:
                max_temp = df_norm[temp_col].max()
                if max_temp > 100:  # Likely Fahrenheit
                    df_norm[temp_col] = (df_norm[temp_col] - 32) * 5/9
                    logger.info("Temperature converted F→C")
        
        # Normalize pluviometry (ensure mm)
        if column_mapping['pluviometrie']:
            rain_col = column_mapping['pluviometrie']
            if rain_col in df_norm.columns:
                max_rain = df_norm[rain_col].max()
                if max_rain > 10000:  # Not mm
                    df_norm[rain_col] = df_norm[rain_col] / 1000
                    logger.info("Pluviometry normalized")
        
        return df_norm
    
    @staticmethod
    def prepare_for_prediction(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Prepare data for predictions"""
        
        logger.info("Preparing data for predictions...")
        
        col_mapping = DataProcessor.identify_columns(df)
        df_clean = DataProcessor.clean_data(df)
        df_norm = DataProcessor.normalize_values(df_clean, col_mapping)
        
        logger.info(f"✓ Ready for predictions: {len(df_norm)} rows")
        
        return df_norm, col_mapping
