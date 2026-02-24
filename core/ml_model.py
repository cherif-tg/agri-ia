"""
core/ml_model.py
================
Modèle de Machine Learning optimisé pour la prédiction du rendement agricole.

Architecture :
- Modèle principal : XGBoost (meilleure performance sur données tabulaires)
- Modèle secondaire : LightGBM (vitesse + régularisation)
- Ensemble : moyenne pondérée des deux modèles
- Feature engineering : indices de stress hydrique, indices climatiques, interactions
- Optimisation : Optuna pour le tuning des hyperparamètres
- Évaluation : validation croisée 5-fold + métriques complètes
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, VotingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb

try:
    import lightgbm as lgb
    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────────────────────

CATEGORICAL_COLS = ["region", "culture", "type_sol"]
NUMERICAL_COLS   = ["surface_ha", "pluviometrie_mm", "temperature_moyenne_c"]
TARGET_COL       = "rendement_t_ha"

# Pluviométrie optimale par culture (mm/saison)
OPTIMAL_PLUVIO = {"Maïs": 900, "Sorgho": 750, "Mil": 600}

# Température optimale par culture (°C)
OPTIMAL_TEMP = {"Maïs": 26, "Sorgho": 28, "Mil": 30}


# ─────────────────────────────────────────────────────────────────────────────
# Feature engineering
# ─────────────────────────────────────────────────────────────────────────────

def _add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée des features supplémentaires à partir des données brutes.

    Features ajoutées :
    - ``indice_hydrique``   : ratio pluie / optimal par culture
    - ``stress_thermique``  : écart absolu à la température optimale
    - ``surface_log``       : log(surface) pour réduire l'asymétrie
    - ``pluvio_temp_inter`` : interaction pluie × température
    - ``score_region``      : encodage ordinal des régions par pluvio moyenne
    """
    result = df.copy()

    # --- Indice hydrique (0..1.5) ────────────────────────────────────────────
    def _hydro(row: pd.Series) -> float:
        opt = OPTIMAL_PLUVIO.get(str(row.get("culture", "Maïs")), 900)
        return round(min(row.get("pluviometrie_mm", opt) / opt, 1.5), 3)

    result["indice_hydrique"] = result.apply(_hydro, axis=1)

    # --- Stress thermique ────────────────────────────────────────────────────
    def _thermal(row: pd.Series) -> float:
        opt = OPTIMAL_TEMP.get(str(row.get("culture", "Maïs")), 27)
        return round(abs(row.get("temperature_moyenne_c", opt) - opt), 2)

    result["stress_thermique"] = result.apply(_thermal, axis=1)

    # --- Log surface ─────────────────────────────────────────────────────────
    result["surface_log"] = np.log1p(result["surface_ha"].fillna(1))

    # --- Interaction pluie × température ─────────────────────────────────────
    result["pluvio_temp_inter"] = (
        result["pluviometrie_mm"] * result["temperature_moyenne_c"]
    ) / 1000

    # --- Score régional (ordinal basé sur la pluvio moyenne) ─────────────────
    region_rank = {
        "Savanes": 0,
        "Kara": 1,
        "Centrale": 2,
        "Maritime": 3,
        "Plateaux": 4,
    }
    result["score_region"] = result["region"].map(region_rank).fillna(2)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Classe principale
# ─────────────────────────────────────────────────────────────────────────────

class AgroPredictModel:
    """
    Modèle ensemble XGBoost + LightGBM pour la prédiction du rendement.

    Usage
    -----
    >>> model = AgroPredictModel()
    >>> model.train(df)
    >>> pred = model.predict({"region": "Kara", "culture": "Maïs", ...})
    >>> model.save("models/agro_predict_model.pkl")
    >>> loaded = AgroPredictModel.load("models/agro_predict_model.pkl")
    """

    def __init__(self) -> None:
        self.xgb_model: Optional[xgb.XGBRegressor] = None
        self.lgb_model = None            # LightGBM si disponible
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: list[str] = []
        self.training_metrics: Dict[str, Any] = {}
        self._trained = False

    # ── Entraînement ─────────────────────────────────────────────────────────

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = TARGET_COL,
        n_trials: int = 30,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        Entraîne le modèle ensemble avec optimisation Optuna.

        Paramètres
        ----------
        df        : DataFrame contenant les données d'entraînement
        target_col: Colonne cible (rendement)
        n_trials  : Nombre d'itérations Optuna (défaut 30)
        cv_folds  : Nombre de folds pour la validation croisée

        Retourne
        --------
        dict avec MAE, RMSE, R², MAPE et les importances de features
        """
        logger.info("Démarrage de l'entraînement du modèle AgroPredict...")

        # 1. Feature engineering
        df = _add_engineered_features(df)

        # 2. Encodage des catégorielles
        df_enc = df.copy()
        for col in CATEGORICAL_COLS:
            le = LabelEncoder()
            df_enc[col] = le.fit_transform(df_enc[col].astype(str))
            self.label_encoders[col] = le

        # 3. Sélection des features
        extra_features = [
            "indice_hydrique",
            "stress_thermique",
            "surface_log",
            "pluvio_temp_inter",
            "score_region",
        ]
        all_features = CATEGORICAL_COLS + NUMERICAL_COLS + extra_features
        self.feature_names = all_features

        X = df_enc[all_features]
        y = df_enc[target_col]

        # 4. Split train / test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 5. Optimisation XGBoost via Optuna
        logger.info(f"Optimisation XGBoost ({n_trials} trials)...")
        best_xgb_params = self._optimize_xgboost(X_train, y_train, n_trials)

        # 6. Entraînement XGBoost final
        self.xgb_model = xgb.XGBRegressor(
            **best_xgb_params,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )
        self.xgb_model.fit(X_train, y_train)

        # 7. Entraînement LightGBM
        if _HAS_LGB:
            logger.info("Entraînement LightGBM...")
            best_lgb_params = self._optimize_lightgbm(X_train, y_train, n_trials)
            self.lgb_model = lgb.LGBMRegressor(
                **best_lgb_params,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            )
            self.lgb_model.fit(X_train, y_train)

        # 8. Prédictions ensemble sur test
        y_pred = self._ensemble_predict(X_test)

        # 9. Métriques
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2   = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100

        # 10. Validation croisée (R²)
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.xgb_model, X, y, cv=cv, scoring="r2")

        self.training_metrics = {
            "MAE":       round(mae, 4),
            "RMSE":      round(rmse, 4),
            "R2":        round(r2, 4),
            "MAPE_pct":  round(mape, 2),
            "CV_R2_mean": round(cv_scores.mean(), 4),
            "CV_R2_std":  round(cv_scores.std(), 4),
            "n_train":   len(X_train),
            "n_test":    len(X_test),
            "feature_importance": self._get_feature_importance(),
        }

        self._trained = True
        logger.info(
            f"Entraînement terminé ✓ | R²={r2:.3f} | MAE={mae:.3f} | RMSE={rmse:.3f}"
        )
        return self.training_metrics

    # ── Optimisation hyperparamètres ──────────────────────────────────────────

    def _optimize_xgboost(
        self, X_train: pd.DataFrame, y_train: pd.Series, n_trials: int
    ) -> Dict:
        """Optimise les hyperparamètres XGBoost avec Optuna."""

        def objective(trial: optuna.Trial) -> float:
            params = {
                "n_estimators":      trial.suggest_int("n_estimators", 100, 600),
                "max_depth":         trial.suggest_int("max_depth", 3, 10),
                "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample":         trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha":         trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda":        trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_weight":  trial.suggest_int("min_child_weight", 1, 10),
                "gamma":             trial.suggest_float("gamma", 1e-8, 1.0, log=True),
            }
            model = xgb.XGBRegressor(**params, random_state=42, verbosity=0, n_jobs=-1)
            cv = KFold(n_splits=3, shuffle=True, random_state=42)
            scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2")
            return scores.mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        return study.best_params

    def _optimize_lightgbm(
        self, X_train: pd.DataFrame, y_train: pd.Series, n_trials: int
    ) -> Dict:
        """Optimise les hyperparamètres LightGBM avec Optuna."""

        def objective(trial: optuna.Trial) -> float:
            params = {
                "n_estimators":     trial.suggest_int("n_estimators", 100, 500),
                "num_leaves":       trial.suggest_int("num_leaves", 20, 150),
                "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "max_depth":        trial.suggest_int("max_depth", 3, 12),
                "subsample":        trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha":        trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda":       trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            }
            model = lgb.LGBMRegressor(**params, random_state=42, verbose=-1, n_jobs=-1)
            cv = KFold(n_splits=3, shuffle=True, random_state=42)
            scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2")
            return scores.mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        return study.best_params

    # ── Prédiction ────────────────────────────────────────────────────────────

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit le rendement à partir des données d'une exploitation.

        Paramètres
        ----------
        input_data : dict avec les clés
            - region, culture, type_sol (str)
            - surface_ha, pluviometrie_mm, temperature_moyenne_c (float)
            - irrigation (str, optionnel)
            - fertilisation (str, optionnel)

        Retourne
        --------
        dict avec rendement prédit, intervalle de confiance, niveau de risque
        """
        if not self._trained:
            raise RuntimeError("Le modèle n'a pas encore été entraîné. Appelez .train() d'abord.")

        # Préparer le DataFrame
        row = {
            "region":               input_data.get("region", "Maritime"),
            "culture":              input_data.get("culture", "Maïs"),
            "type_sol":             input_data.get("type_sol", "Argileux"),
            "surface_ha":           float(input_data.get("surface_ha", 1.0)),
            "pluviometrie_mm":      float(input_data.get("pluviometrie_mm", 800)),
            "temperature_moyenne_c": float(input_data.get("temperature_moyenne_c", 27)),
        }
        df_input = pd.DataFrame([row])

        # Feature engineering
        df_input = _add_engineered_features(df_input)

        # Encodage
        df_enc = df_input.copy()
        for col in CATEGORICAL_COLS:
            le = self.label_encoders.get(col)
            if le is not None:
                val = str(df_enc[col].iloc[0])
                if val in le.classes_:
                    df_enc[col] = le.transform([val])
                else:
                    df_enc[col] = le.transform([le.classes_[0]])

        X = df_enc[self.feature_names]

        # Prédiction ensemble
        rendement_base = float(self._ensemble_predict(X)[0])

        # Facteurs d'ajustement (irrigation, fertilisation)
        facteur_irrig = {
            "Aucun": 1.0,
            "Traditionnel": 1.08,
            "Goutte à goutte": 1.22,
            "Aspersion": 1.14,
        }
        facteur_ferti = {
            "Aucune": 0.82,
            "Organique": 1.02,
            "Chimique": 1.18,
            "Mixte": 1.13,
        }

        f_irrig = facteur_irrig.get(input_data.get("irrigation", "Aucun"), 1.0)
        f_ferti = facteur_ferti.get(input_data.get("fertilisation", "Aucune"), 1.0)

        rendement_ajuste = rendement_base * f_irrig * f_ferti

        # Intervalle de confiance (±8%)
        ci_low  = round(rendement_ajuste * 0.92, 3)
        ci_high = round(rendement_ajuste * 1.08, 3)

        # Niveau de risque basé sur l'écart à l'optimal
        pluvio    = row["pluviometrie_mm"]
        opt_pluvio = OPTIMAL_PLUVIO.get(row["culture"], 900)
        ecart_pluvio = abs(pluvio - opt_pluvio) / opt_pluvio

        if ecart_pluvio > 0.35 or pluvio < 400:
            niveau_risque = "Élevé"
            score_risque  = 75
        elif ecart_pluvio > 0.20 or pluvio < 600:
            niveau_risque = "Modéré"
            score_risque  = 45
        else:
            niveau_risque = "Faible"
            score_risque  = 18

        return {
            "rendement_t_ha":      round(rendement_ajuste, 3),
            "rendement_base_t_ha": round(rendement_base, 3),
            "ci_low":              ci_low,
            "ci_high":             ci_high,
            "production_total_t":  round(rendement_ajuste * row["surface_ha"], 2),
            "niveau_risque":       niveau_risque,
            "score_risque_pct":    score_risque,
            "facteur_irrigation":  f_irrig,
            "facteur_fertilisation": f_ferti,
        }

    def _ensemble_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Moyenne pondérée XGBoost (60%) + LightGBM (40%)."""
        pred_xgb = self.xgb_model.predict(X)
        if _HAS_LGB and self.lgb_model is not None:
            pred_lgb = self.lgb_model.predict(X)
            return 0.60 * pred_xgb + 0.40 * pred_lgb
        return pred_xgb

    # ── Utilitaires ───────────────────────────────────────────────────────────

    def _get_feature_importance(self) -> Dict[str, float]:
        """Retourne les importances de features XGBoost triées par ordre décroissant."""
        if self.xgb_model is None:
            return {}
        importances = self.xgb_model.feature_importances_
        return dict(
            sorted(
                zip(self.feature_names, importances.tolist()),
                key=lambda x: x[1],
                reverse=True,
            )
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques d'entraînement."""
        return self.training_metrics

    # ── Persistance ───────────────────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        """Sauvegarde le modèle sur disque."""
        state = {
            "xgb_model":      self.xgb_model,
            "lgb_model":      self.lgb_model,
            "label_encoders": self.label_encoders,
            "feature_names":  self.feature_names,
            "metrics":        self.training_metrics,
            "_trained":       self._trained,
        }
        joblib.dump(state, path)
        logger.info(f"Modèle sauvegardé → {path}")

    @classmethod
    def load(cls, path: str | Path) -> "AgroPredictModel":
        """Charge un modèle sauvegardé."""
        state = joblib.load(path)
        m = cls()
        m.xgb_model      = state["xgb_model"]
        m.lgb_model      = state.get("lgb_model")
        m.label_encoders = state["label_encoders"]
        m.feature_names  = state["feature_names"]
        m.training_metrics = state.get("metrics", {})
        m._trained       = state.get("_trained", True)
        logger.info(f"Modèle chargé depuis {path}")
        return m

    def is_trained(self) -> bool:
        """Retourne True si le modèle est entraîné."""
        return self._trained


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires publiques
# ─────────────────────────────────────────────────────────────────────────────

def get_or_train_model(model_path: Path, data_path: Path) -> AgroPredictModel:
    """
    Charge le modèle depuis le disque si disponible,
    sinon l'entraîne à partir du CSV de données.

    Paramètres
    ----------
    model_path : chemin vers le fichier .pkl
    data_path  : chemin vers le CSV d'entraînement
    """
    if model_path.exists():
        logger.info("Chargement du modèle existant...")
        return AgroPredictModel.load(model_path)

    logger.info("Entraînement d'un nouveau modèle (premier lancement)...")
    df = pd.read_csv(data_path)
    model = AgroPredictModel()
    model.train(df)
    model.save(model_path)
    return model
