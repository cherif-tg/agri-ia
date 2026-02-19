"""
Data preparation from FAOSTAT and local data for ML training
Loads and augments agricultural data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Dict
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparator:
    """Prepare data for ML training"""
    
    FAOSTAT_FOLDER = Path("../data_togo")
    OUTPUT_PATH = Path("../data/augmented_data.csv")
    
    # Expected columns mapping
    EXPECTED_COLUMNS = {
        'temperature': ['temperature', 'temp', 'temperature_moyenne', 'mean_temperature'],
        'pluviometrie': ['pluviometrie', 'rainfall', 'precip', 'precipitation', 'pluvial'],
        'rendement': ['rendement', 'yield', 'production', 'tonnage'],
        'culture': ['culture', 'crop', 'type_culture', 'crop_type'],
        'region': ['region', 'area', 'location', 'zone']
    }
    
    @staticmethod
    def load_faostat_data() -> pd.DataFrame:
        """Load all FAOSTAT CSV files"""
        
        logger.info("Loading FAOSTAT files...")
        
        all_files = list(Path(DataPreparator.FAOSTAT_FOLDER).glob("FAOSTAT_*.csv"))
        
        if not all_files:
            logger.warning("⚠️ No FAOSTAT files found")
            return pd.DataFrame()
        
        dataframes = []
        
        for file in all_files:
            try:
                df = pd.read_csv(file, on_bad_lines='skip')
                logger.info(f"✓ Loaded: {file.name} ({len(df)} rows)")
                dataframes.append(df)
            except Exception as e:
                logger.warning(f"Skip {file.name}: {e}")
        
        if not dataframes:
            return pd.DataFrame()
        
        combined = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Total FAOSTAT: {len(combined)} rows")
        
        return combined
    
    @staticmethod
    def load_local_agricultural_data() -> pd.DataFrame:
        """Load local agricultural data"""
        
        local_file = Path(DataPreparator.FAOSTAT_FOLDER) / "donnees_agricoles_togo.csv"
        
        if not local_file.exists():
            logger.warning(f"⚠️ Local data not found: {local_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(local_file)
            logger.info(f"✓ Local data: {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error loading local data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def find_matching_column(df: pd.DataFrame, target_col: str) -> str:
        """Find matching column in dataframe"""
        
        keywords = DataPreparator.EXPECTED_COLUMNS.get(target_col, [target_col])
        col_lower = [c.lower() for c in df.columns]
        
        for keyword in keywords:
            for i, col_name in enumerate(col_lower):
                if keyword.lower() in col_name or col_name in keyword.lower():
                    return df.columns[i]
        
        return None
    
    @staticmethod
    def clean_and_merge_data(dfs: list) -> pd.DataFrame:
        """Clean and merge multiple dataframes"""
        
        logger.info("Cleaning and merging data...")
        
        merged_data = []
        
        for df in dfs:
            if df.empty:
                continue
            
            # Find key columns
            temp_col = DataPreparator.find_matching_column(df, 'temperature')
            rain_col = DataPreparator.find_matching_column(df, 'pluviometrie')
            yield_col = DataPreparator.find_matching_column(df, 'rendement')
            culture_col = DataPreparator.find_matching_column(df, 'culture')
            region_col = DataPreparator.find_matching_column(df, 'region')
            
            # Extract relevant columns
            df_clean = pd.DataFrame()
            
            if temp_col:
                df_clean['temperature'] = pd.to_numeric(df[temp_col], errors='coerce')
            if rain_col:
                df_clean['pluviometrie'] = pd.to_numeric(df[rain_col], errors='coerce')
            if yield_col:
                df_clean['rendement'] = pd.to_numeric(df[yield_col], errors='coerce')
            if culture_col:
                df_clean['culture'] = df[culture_col].astype(str)
            if region_col:
                df_clean['region'] = df[region_col].astype(str)
            
            # Remove rows with key missing values
            df_clean = df_clean.dropna(subset=['rendement']) if 'rendement' in df_clean else df_clean
            
            if len(df_clean) > 0:
                merged_data.append(df_clean)
        
        if not merged_data:
            logger.warning("⚠️ No valid data after cleaning")
            return pd.DataFrame()
        
        result = pd.concat(merged_data, ignore_index=True)
        logger.info(f"✓ Merged: {len(result)} clean rows")
        
        return result
    
    @staticmethod
    def augment_with_synthetic_data(df: pd.DataFrame, multiplier: int = 3) -> pd.DataFrame:
        """Augment data with synthetic variations"""
        
        logger.info(f"Augmenting data (multiplier={multiplier})...")
        
        if df.empty or 'rendement' not in df:
            return df
        
        additional_data = []
        
        for _ in range(multiplier - 1):
            df_aug = df.copy()
            
            # Add noise to numeric columns
            numeric_cols = df_aug.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                noise = np.random.normal(0, df_aug[col].std() * 0.1, len(df_aug))
                df_aug[col] = df_aug[col] + noise
                df_aug[col] = df_aug[col].clip(lower=0)
            
            additional_data.append(df_aug)
        
        augmented = pd.concat([df] + additional_data, ignore_index=True)
        logger.info(f"✓ Augmented: {len(augmented)} rows (from {len(df)})")
        
        return augmented
    
    @staticmethod
    def add_missing_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add missing features for model"""
        
        logger.info("Adding missing features...")
        
        required_features = [
            'temperature', 'pluviometrie', 'type_sol',
            'irrigation', 'fertilisation', 'rendement'
        ]
        
        for feature in required_features:
            if feature not in df.columns:
                if feature == 'temperature':
                    df[feature] = np.random.uniform(20, 35, len(df))
                elif feature == 'pluviometrie':
                    df[feature] = np.random.uniform(400, 1200, len(df))
                elif feature == 'type_sol':
                    df[feature] = np.random.choice(['Sableux', 'Argileux', 'Limoneux'], len(df))
                elif feature == 'irrigation':
                    df[feature] = np.random.choice([0, 1], len(df))
                elif feature == 'fertilisation':
                    df[feature] = np.random.uniform(0, 1, len(df))
                elif feature == 'rendement':
                    df[feature] = np.random.uniform(2, 5, len(df))
        
        logger.info("✓ Features added")
        return df
    
    @staticmethod
    def prepare_final_data(df: pd.DataFrame) -> pd.DataFrame:
        """Final data preparation"""
        
        logger.info("Final data preparation...")
        
        df = df.dropna(subset=['rendement'])
        df = df[df['rendement'] > 0]
        
        # Ensure numeric types
        numeric_cols = ['temperature', 'pluviometrie', 'irrigation', 'fertilisation', 'rendement']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=numeric_cols)
        
        logger.info(f"✓ Final: {len(df)} valid rows")
        
        return df
    
    @staticmethod
    def run():
        """Execute full data preparation pipeline"""
        
        logger.info("="*50)
        logger.info("DATA PREPARATION STARTED")
        logger.info("="*50)
        
        # Load data
        dfs = []
        
        faostat_df = DataPreparator.load_faostat_data()
        if not faostat_df.empty:
            dfs.append(faostat_df)
        
        local_df = DataPreparator.load_local_agricultural_data()
        if not local_df.empty:
            dfs.append(local_df)
        
        if not dfs:
            logger.error("❌ No data loaded")
            return
        
        # Process
        df = DataPreparator.clean_and_merge_data(dfs)
        
        if df.empty:
            logger.error("❌ Failed to merge data")
            return
        
        # Add features
        df = DataPreparator.add_missing_features(df)
        
        # Augment
        df = DataPreparator.augment_with_synthetic_data(df, multiplier=3)
        
        # Final prep
        df = DataPreparator.prepare_final_data(df)
        
        # Save
        output_dir = DataPreparator.OUTPUT_PATH.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(DataPreparator.OUTPUT_PATH, index=False)
        
        logger.info("="*50)
        logger.info(f"✓ DATA SAVED: {DataPreparator.OUTPUT_PATH}")
        logger.info(f"  Rows: {len(df)}")
        logger.info(f"  Columns: {', '.join(df.columns)}")
        logger.info("="*50)
        
        return df


if __name__ == "__main__":
    DataPreparator.run()
