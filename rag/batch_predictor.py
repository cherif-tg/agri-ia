"""
Batch predictions for RAG
Make predictions on multiple rows
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import logging
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)


class BatchPredictor:
    """Make batch predictions"""
    
    def __init__(self, model_path: Path = None):
        """Load model"""
        
        if model_path is None:
            model_path = Path("models/modele_rendement_agricole_v2_xgb.pkl")
        
        try:
            self.model = joblib.load(model_path)
            logger.info(f"✓ Model loaded: {model_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Model not found: {model_path}")
    
    @staticmethod
    def prepare_features(df: pd.DataFrame, col_mapping: dict) -> pd.DataFrame:
        """Prepare features for prediction"""
        
        df_features = pd.DataFrame()
        
        required_cols = {k: v for k, v in col_mapping.items() if v is not None}
        
        for feature_name, df_col in required_cols.items():
            if df_col in df.columns:
                df_features[feature_name] = df[df_col]
        
        # Fill missing values
        df_features = df_features.fillna(df_features.mean(numeric_only=True))
        
        logger.info(f"Features prepared: {df_features.shape}")
        return df_features
    
    def predict_batch(self, df: pd.DataFrame, col_mapping: dict) -> pd.DataFrame:
        """Make batch predictions"""
        
        logger.info(f"Making predictions on {len(df)} rows...")
        
        df_features = self.prepare_features(df, col_mapping)
        
        predictions = self.model.predict(df_features)
        
        df_results = df.copy()
        df_results['rendement_predit'] = predictions
        
        # Calculate production
        if col_mapping['superficie'] and col_mapping['superficie'] in df.columns:
            df_results['production_estimee'] = (
                predictions * df[col_mapping['superficie']].fillna(5)
            )
        else:
            df_results['production_estimee'] = predictions * 5
        
        # Evaluate risk
        df_results['risque'] = df_results['rendement_predit'].apply(
            lambda x: BatchPredictor._evaluate_risk(x)
        )
        
        logger.info(f"✓ {len(predictions)} predictions completed")
        
        return df_results
    
    @staticmethod
    def _evaluate_risk(rendement: float) -> str:
        """Simple risk evaluation"""
        if rendement < 2:
            return "Élevé"
        elif rendement < 3:
            return "Moyen"
        else:
            return "Faible"
    
    @staticmethod
    def get_summary_stats(df_results: pd.DataFrame) -> dict:
        """Get summary statistics"""
        
        stats = {
            'total_rows': len(df_results),
            'rendement_moyen': df_results['rendement_predit'].mean(),
            'rendement_min': df_results['rendement_predit'].min(),
            'rendement_max': df_results['rendement_predit'].max(),
            'production_totale': df_results['production_estimee'].sum(),
        }
        
        if 'risque' in df_results.columns:
            risk_counts = df_results['risque'].value_counts()
            stats['risque_moyen'] = risk_counts.idxmax() if len(risk_counts) > 0 else "N/A"
        else:
            stats['risque_moyen'] = "N/A"
        
        return stats
