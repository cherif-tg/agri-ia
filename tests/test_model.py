"""
tests/test_model.py
===================
Tests unitaires pour le modèle ML AgroPredict (core/ml_model.py).

Exécution :
    pytest tests/test_model.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ajout du répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ml_model import (
    AgroPredictModel,
    _add_engineered_features,
    OPTIMAL_PLUVIO,
    OPTIMAL_TEMP,
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
    TARGET_COL,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_df() -> pd.DataFrame:
    """
    Jeu de données synthétique avec une relation forte entre features et cible.
    La relation est volontairement forte pour permettre au modèle d'apprendre.
    """
    rng = np.random.default_rng(42)
    n = 200
    regions   = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]
    cultures  = ["Maïs", "Sorgho", "Mil"]
    sols      = ["Argileux", "Sableux", "Limoneux", "Argilo-sableux"]

    region_arr  = rng.choice(regions, n)
    culture_arr = rng.choice(cultures, n)
    sol_arr     = rng.choice(sols, n)
    pluvio      = rng.uniform(400, 1500, n)
    temp        = rng.uniform(22, 34, n)
    surface     = rng.uniform(0.5, 10, n)

    # Relation forte et déterministe pour permettre l'apprentissage
    rendement = (
        1.0
        + 0.002 * pluvio
        - 0.08 * np.abs(temp - 27)
        + 0.05 * (surface ** 0.3)
        + rng.normal(0, 0.15, n)  # bruit faible
    ).clip(0.3, 6.0).round(2)

    data = {
        "region":               region_arr,
        "culture":              culture_arr,
        "type_sol":             sol_arr,
        "surface_ha":           surface.round(2),
        "pluviometrie_mm":      pluvio.round(1),
        "temperature_moyenne_c": temp.round(1),
        "rendement_t_ha":       rendement,
    }
    return pd.DataFrame(data)


@pytest.fixture(scope="module")
def trained_model(sample_df) -> AgroPredictModel:
    """Modèle entraîné sur le jeu synthétique (n_trials minimal pour la vitesse)."""
    model = AgroPredictModel()
    model.train(sample_df, n_trials=5, cv_folds=3)
    return model


# ─── Tests : feature engineering ─────────────────────────────────────────────

class TestFeatureEngineering:
    """Teste la fonction _add_engineered_features."""

    def test_output_columns_added(self, sample_df):
        df_out = _add_engineered_features(sample_df)
        expected = [
            "indice_hydrique", "stress_thermique",
            "surface_log", "pluvio_temp_inter", "score_region",
        ]
        for col in expected:
            assert col in df_out.columns, f"Colonne manquante : {col}"

    def test_indice_hydrique_range(self, sample_df):
        df_out = _add_engineered_features(sample_df)
        assert df_out["indice_hydrique"].between(0, 1.6).all(), \
            "indice_hydrique hors plage attendue [0, 1.5]"

    def test_stress_thermique_nonnegative(self, sample_df):
        df_out = _add_engineered_features(sample_df)
        assert (df_out["stress_thermique"] >= 0).all(), \
            "stress_thermique doit être ≥ 0"

    def test_surface_log_positive(self, sample_df):
        df_out = _add_engineered_features(sample_df)
        assert (df_out["surface_log"] > 0).all(), "surface_log doit être > 0"

    def test_no_nan_introduced(self, sample_df):
        df_out = _add_engineered_features(sample_df)
        new_cols = ["indice_hydrique", "stress_thermique", "surface_log",
                    "pluvio_temp_inter", "score_region"]
        for col in new_cols:
            assert df_out[col].isna().sum() == 0, f"NaN dans {col}"

    def test_optimal_pluvio_keys(self):
        for culture in ["Maïs", "Sorgho", "Mil"]:
            assert culture in OPTIMAL_PLUVIO, f"{culture} absent de OPTIMAL_PLUVIO"


# ─── Tests : entraînement ─────────────────────────────────────────────────────

class TestModelTraining:
    """Teste l'entraînement du modèle."""

    def test_is_trained_after_fit(self, trained_model):
        assert trained_model.is_trained(), "is_trained() doit être True après fit"

    def test_metrics_present(self, trained_model):
        metrics = trained_model.get_metrics()
        for key in ["MAE", "RMSE", "R2", "MAPE_pct", "CV_R2_mean"]:
            assert key in metrics, f"Métrique manquante : {key}"

    def test_r2_reasonable(self, trained_model):
        r2 = trained_model.get_metrics()["R2"]
        assert r2 > 0.40, f"R² trop bas sur données synthétiques : {r2}"

    def test_mae_positive(self, trained_model):
        mae = trained_model.get_metrics()["MAE"]
        assert mae > 0, "MAE doit être > 0"

    def test_feature_importance_not_empty(self, trained_model):
        fi = trained_model.get_metrics().get("feature_importance", {})
        assert len(fi) > 0, "La feature importance est vide"

    def test_label_encoders_exist(self, trained_model):
        for col in CATEGORICAL_COLS:
            assert col in trained_model.label_encoders, f"Encodeur manquant pour {col}"


# ─── Tests : prédiction ───────────────────────────────────────────────────────

class TestModelPrediction:
    """Teste les prédictions du modèle."""

    VALID_INPUT = {
        "region":               "Kara",
        "culture":              "Maïs",
        "type_sol":             "Argileux",
        "surface_ha":           5.0,
        "pluviometrie_mm":      900,
        "temperature_moyenne_c": 27.0,
        "irrigation":           "Aucun",
        "fertilisation":        "Aucune",
    }

    def test_predict_returns_dict(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        assert isinstance(result, dict), "Le résultat doit être un dict"

    def test_predict_required_keys(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        for key in ["rendement_t_ha", "production_total_t", "niveau_risque",
                    "score_risque_pct", "ci_low", "ci_high"]:
            assert key in result, f"Clé manquante dans le résultat : {key}"

    def test_rendement_positive(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        assert result["rendement_t_ha"] > 0, "Rendement doit être > 0"

    def test_ci_ordered(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        assert result["ci_low"] <= result["rendement_t_ha"] <= result["ci_high"], \
            "L'intervalle de confiance est incohérent"

    def test_production_consistent(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        expected = round(result["rendement_t_ha"] * self.VALID_INPUT["surface_ha"], 2)
        assert abs(result["production_total_t"] - expected) < 0.5, \
            "Production incohérente avec rendement × surface"

    def test_risque_valid_values(self, trained_model):
        result = trained_model.predict(self.VALID_INPUT)
        assert result["niveau_risque"] in ["Faible", "Modéré", "Élevé"], \
            f"Niveau de risque invalide: {result['niveau_risque']}"

    def test_high_rain_low_risk(self, trained_model):
        """Avec une bonne pluviométrie, le risque doit être faible."""
        inp = {**self.VALID_INPUT, "pluviometrie_mm": 950}
        result = trained_model.predict(inp)
        assert result["niveau_risque"] in ["Faible", "Modéré"]

    def test_low_rain_high_risk(self, trained_model):
        """Avec une faible pluviométrie, le risque doit être modéré ou élevé."""
        inp = {**self.VALID_INPUT, "pluviometrie_mm": 250}
        result = trained_model.predict(inp)
        assert result["niveau_risque"] in ["Modéré", "Élevé"]

    def test_irrigation_increases_yield(self, trained_model):
        """L'irrigation goutte à goutte doit donner un rendement supérieur à l'absence d'irrigation."""
        r_none  = trained_model.predict({**self.VALID_INPUT, "irrigation": "Aucun"})
        r_drip  = trained_model.predict({**self.VALID_INPUT, "irrigation": "Goutte à goutte"})
        assert r_drip["rendement_t_ha"] > r_none["rendement_t_ha"], \
            "L'irrigation n'augmente pas le rendement"

    def test_fertilisation_increases_yield(self, trained_model):
        """La fertilisation chimique doit donner un rendement supérieur à l'absence."""
        r_none  = trained_model.predict({**self.VALID_INPUT, "fertilisation": "Aucune"})
        r_chem  = trained_model.predict({**self.VALID_INPUT, "fertilisation": "Chimique"})
        assert r_chem["rendement_t_ha"] > r_none["rendement_t_ha"]

    def test_predict_all_regions(self, trained_model):
        """Le modèle doit prédire pour toutes les régions sans erreur."""
        for region in ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]:
            inp = {**self.VALID_INPUT, "region": region}
            result = trained_model.predict(inp)
            assert result["rendement_t_ha"] > 0

    def test_predict_all_cultures(self, trained_model):
        """Le modèle doit prédire pour toutes les cultures."""
        for culture in ["Maïs", "Sorgho", "Mil"]:
            inp = {**self.VALID_INPUT, "culture": culture}
            result = trained_model.predict(inp)
            assert result["rendement_t_ha"] > 0


# ─── Tests : persistance ──────────────────────────────────────────────────────

class TestModelPersistence:
    """Teste la sauvegarde et le rechargement du modèle."""

    def test_save_and_load(self, trained_model, tmp_path):
        path = tmp_path / "test_model.pkl"
        trained_model.save(path)

        assert path.exists(), "Le fichier pkl n'a pas été créé"

        loaded = AgroPredictModel.load(path)
        assert loaded.is_trained(), "Le modèle chargé n'est pas en état entraîné"

    def test_loaded_model_same_prediction(self, trained_model, tmp_path):
        path = tmp_path / "test_model2.pkl"
        trained_model.save(path)
        loaded = AgroPredictModel.load(path)

        inp = {
            "region": "Maritime", "culture": "Maïs", "type_sol": "Argileux",
            "surface_ha": 5.0, "pluviometrie_mm": 800, "temperature_moyenne_c": 27.0,
        }
        r_original = trained_model.predict(inp)
        r_loaded   = loaded.predict(inp)

        assert abs(r_original["rendement_t_ha"] - r_loaded["rendement_t_ha"]) < 0.001, \
            "La prédiction après rechargement est différente"

    def test_not_trained_raises(self):
        """Un modèle non entraîné doit lever RuntimeError."""
        m = AgroPredictModel()
        with pytest.raises(RuntimeError):
            m.predict({"region": "Maritime", "culture": "Maïs"})
