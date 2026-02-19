"""
Advanced ML Training with XGBoost and Hyperparameter Tuning
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import joblib
from typing import Tuple, Dict
import time

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import xgboost as xgb

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedMLTrainer:
    """Train advanced ML model for agricultural predictions"""
    
    DATA_PATH = Path("../data/augmented_data.csv")
    MODEL_PATH = Path("../models/modele_rendement_agricole_v2_xgb.pkl")
    REPORT_PATH = Path("../models/training_report.txt")
    
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.label_encoders = {}
        self.feature_names = None
    
    def load_data(self) -> pd.DataFrame:
        """Load prepared data"""
        
        logger.info(f"Loading data from {self.DATA_PATH}")
        
        if not self.DATA_PATH.exists():
            logger.error(f"❌ Data not found: {self.DATA_PATH}")
            logger.info("Run: python data_preparator.py first")
            return None
        
        df = pd.read_csv(self.DATA_PATH)
        logger.info(f"✓ Loaded: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target"""
        
        logger.info("Preparing features...")
        
        # Target
        if 'rendement' not in df.columns:
            logger.error("❌ 'rendement' column not found")
            return None, None
        
        y = df['rendement'].copy()
        
        # Features: remove non-numeric and target
        X = df.select_dtypes(include=[np.number]).drop('rendement', axis=1)
        
        # Encode categorical if present
        for col in df.select_dtypes(include='object').columns:
            if col not in ['culture', 'region']:
                continue
            
            le = LabelEncoder()
            X[f'{col}_encoded'] = le.fit_transform(df[col].fillna('Unknown'))
            self.label_encoders[col] = le
        
        # Fill missing values
        X = X.fillna(X.mean())
        
        logger.info(f"✓ Features: {X.shape}")
        logger.info(f"  Columns: {', '.join(X.columns.tolist())}")
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series):
        """Split data into train/test"""
        
        logger.info("Splitting data (80/20)...")
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42
        )
        
        logger.info(f"✓ Train: {len(self.X_train)}, Test: {len(self.X_test)}")
    
    def train_baseline(self):
        """Train baseline XGBoost model"""
        
        logger.info("Training baseline XGBoost model...")
        
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        
        self.model.fit(self.X_train, self.y_train)
        
        # Evaluate
        y_pred = self.model.predict(self.X_test)
        r2 = r2_score(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        
        logger.info(f"✓ Baseline: R² = {r2:.4f}, MAE = {mae:.4f}")
        
        return r2, mae
    
    def hyperparameter_tuning(self):
        """Tune hyperparameters with GridSearchCV"""
        
        logger.info("Starting hyperparameter tuning (this may take 30-60 min)...")
        
        param_grid = {
            'max_depth': [5, 6, 7, 8],
            'learning_rate': [0.05, 0.1, 0.15],
            'n_estimators': [100, 150, 200],
            'subsample': [0.8, 0.9],
            'colsample_bytree': [0.8, 0.9]
        }
        
        base_model = xgb.XGBRegressor(random_state=42, verbosity=0)
        
        logger.info("Grid combinations: " + str(
            len(param_grid['max_depth']) * 
            len(param_grid['learning_rate']) * 
            len(param_grid['n_estimators']) *
            len(param_grid['subsample']) *
            len(param_grid['colsample_bytree'])
        ))
        
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        logger.info("Training (this will take time)...")
        start_time = time.time()
        
        grid_search.fit(self.X_train, self.y_train)
        
        elapsed = time.time() - start_time
        logger.info(f"✓ Grid search completed in {elapsed:.2f}s")
        
        self.model = grid_search.best_estimator_
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV R²: {grid_search.best_score_:.4f}")
        
        return grid_search.best_params_, grid_search.best_score_
    
    def evaluate_model(self):
        """Evaluate final model"""
        
        logger.info("Evaluating model...")
        
        # Train predictions
        y_train_pred = self.model.predict(self.X_train)
        train_r2 = r2_score(self.y_train, y_train_pred)
        train_mae = mean_absolute_error(self.y_train, y_train_pred)
        train_rmse = np.sqrt(mean_squared_error(self.y_train, y_train_pred))
        
        # Test predictions
        y_test_pred = self.model.predict(self.X_test)
        test_r2 = r2_score(self.y_test, y_test_pred)
        test_mae = mean_absolute_error(self.y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(self.y_test, y_test_pred))
        test_mape = mean_absolute_percentage_error(self.y_test, y_test_pred)
        
        logger.info("="*50)
        logger.info("TRAIN METRICS:")
        logger.info(f"  R²:   {train_r2:.4f}")
        logger.info(f"  MAE:  {train_mae:.4f}")
        logger.info(f"  RMSE: {train_rmse:.4f}")
        logger.info("="*50)
        logger.info("TEST METRICS:")
        logger.info(f"  R²:   {test_r2:.4f}")
        logger.info(f"  MAE:  {test_mae:.4f}")
        logger.info(f"  RMSE: {test_rmse:.4f}")
        logger.info(f"  MAPE: {test_mape:.4f}")
        logger.info("="*50)
        
        return {
            'train': {'r2': train_r2, 'mae': train_mae, 'rmse': train_rmse},
            'test': {'r2': test_r2, 'mae': test_mae, 'rmse': test_rmse, 'mape': test_mape}
        }
    
    def cross_validate(self, cv: int = 5):
        """Cross-validation"""
        
        logger.info(f"Running {cv}-fold cross-validation...")
        
        cv_scores = cross_val_score(
            self.model, self.X_train, self.y_train,
            cv=cv, scoring='r2'
        )
        
        logger.info(f"✓ CV Scores: {cv_scores}")
        logger.info(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return cv_scores
    
    def save_model(self):
        """Save trained model"""
        
        self.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, self.MODEL_PATH)
        logger.info(f"✓ Model saved: {self.MODEL_PATH}")
    
    def feature_importance(self):
        """Get feature importance"""
        
        importance = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature Importance (Top 10):")
        for idx, row in feature_importance_df.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return feature_importance_df
    
    def generate_report(self, metrics: Dict, best_params: Dict = None):
        """Generate training report"""
        
        with open(self.REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("ADVANCED ML TRAINING REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write("DATA INFO:\n")
            f.write(f"  Training samples: {len(self.X_train)}\n")
            f.write(f"  Test samples: {len(self.X_test)}\n")
            f.write(f"  Features: {len(self.feature_names)}\n")
            f.write(f"  Feature names: {', '.join(self.feature_names)}\n\n")
            
            if best_params:
                f.write("BEST HYPERPARAMETERS:\n")
                for param, value in best_params.items():
                    f.write(f"  {param}: {value}\n")
                f.write("\n")
            
            f.write("TRAIN METRICS:\n")
            f.write(f"  R²:   {metrics['train']['r2']:.4f}\n")
            f.write(f"  MAE:  {metrics['train']['mae']:.4f}\n")
            f.write(f"  RMSE: {metrics['train']['rmse']:.4f}\n\n")
            
            f.write("TEST METRICS:\n")
            f.write(f"  R²:   {metrics['test']['r2']:.4f}\n")
            f.write(f"  MAE:  {metrics['test']['mae']:.4f}\n")
            f.write(f"  RMSE: {metrics['test']['rmse']:.4f}\n")
            f.write(f"  MAPE: {metrics['test']['mape']:.4f}\n\n")
            
            f.write("="*60 + "\n")
            f.write("IMPROVEMENT:\n")
            f.write("  Old model: R² = 0.7200, MAE = 0.4500\n")
            f.write(f"  New model: R² = {metrics['test']['r2']:.4f}, MAE = {metrics['test']['mae']:.4f}\n")
            improvement_r2 = (metrics['test']['r2'] - 0.7200) / 0.7200 * 100
            improvement_mae = (0.4500 - metrics['test']['mae']) / 0.4500 * 100
            f.write(f"  R² improvement: +{improvement_r2:.2f}%\n")
            f.write(f"  MAE improvement: +{improvement_mae:.2f}%\n")
            f.write("="*60 + "\n")
        
        logger.info(f"✓ Report saved: {self.REPORT_PATH}")
    
    def run_full_pipeline(self):
        """Execute full training pipeline"""
        
        logger.info("="*60)
        logger.info("ADVANCED ML TRAINING PIPELINE")
        logger.info("="*60)
        
        # Load
        df = self.load_data()
        if df is None:
            return
        
        # Prepare
        X, y = self.prepare_features(df)
        if X is None:
            return
        
        # Split
        self.split_data(X, y)
        
        # Train baseline
        logger.info("\n--- BASELINE MODEL ---")
        baseline_r2, baseline_mae = self.train_baseline()
        
        # Hyperparameter tuning
        logger.info("\n--- HYPERPARAMETER TUNING ---")
        best_params, best_cv_score = self.hyperparameter_tuning()
        
        # Evaluate tuned model
        logger.info("\n--- EVALUATION ---")
        metrics = self.evaluate_model()
        
        # Cross-validation
        logger.info("\n--- CROSS-VALIDATION ---")
        cv_scores = self.cross_validate()
        
        # Feature importance
        logger.info("\n--- FEATURE IMPORTANCE ---")
        importance_df = self.feature_importance()
        
        # Save model
        logger.info("\n--- SAVING ---")
        self.save_model()
        
        # Generate report
        self.generate_report(metrics, best_params)
        
        logger.info("\n" + "="*60)
        logger.info("✓ TRAINING COMPLETE!")
        logger.info("="*60)
        
        return {
            'baseline': {'r2': baseline_r2, 'mae': baseline_mae},
            'tuned': metrics,
            'best_params': best_params,
            'cv_scores': cv_scores,
            'importance': importance_df
        }


if __name__ == "__main__":
    trainer = AdvancedMLTrainer()
    trainer.run_full_pipeline()
