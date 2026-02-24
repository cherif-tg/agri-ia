"""
tests/test_data_processor.py
============================
Tests pour les utilitaires de traitement de données (core/data_processor.py).

Exécution :
    pytest tests/test_data_processor.py -v
"""

import sys
from pathlib import Path
from io import BytesIO

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_processor import (
    detect_columns,
    get_stats_summary,
    validate_and_clean,
    COLUMN_SYNONYMS,
    REQUIRED_COLUMNS,
)


@pytest.fixture
def sample_csv_df():
    """DataFrame avec des noms de colonnes standard."""
    return pd.DataFrame({
        "region":               ["Kara", "Maritime", "Plateaux"],
        "culture":              ["Maïs", "Sorgho", "Mil"],
        "type_sol":             ["Argileux", "Sableux", "Limoneux"],
        "surface_ha":           [5.0, 3.2, 8.1],
        "pluviometrie_mm":      [900.0, 750.0, 1100.0],
        "temperature_moyenne_c": [27.0, 28.5, 26.0],
        "rendement_t_ha":       [2.5, 1.8, 3.1],
    })


@pytest.fixture
def messy_df():
    """DataFrame avec des noms de colonnes non-standard."""
    return pd.DataFrame({
        "Zone":   ["Kara", "Maritime"],
        "Crop":   ["Maïs", "Sorgho"],
        "Sol":    ["Argileux", "Sableux"],
        "Area":   [5.0, 3.2],
        "Rain":   [900.0, 750.0],
        "Temp":   [27.0, 28.5],
        "Yield":  [2.5, 1.8],
    })


class TestDetectColumns:
    """Tests pour detect_columns."""

    def test_standard_columns_detected(self, sample_csv_df):
        mapping = detect_columns(sample_csv_df)
        assert mapping["region"] == "region"
        assert mapping["culture"] == "culture"
        assert mapping["surface_ha"] == "surface_ha"
        assert mapping["pluviometrie_mm"] == "pluviometrie_mm"
        assert mapping["temperature_moyenne_c"] == "temperature_moyenne_c"

    def test_synonyms_detected(self, messy_df):
        mapping = detect_columns(messy_df)
        assert mapping["region"] == "Zone"
        assert mapping["culture"] == "Crop"
        assert mapping["surface_ha"] == "Area"
        assert mapping["pluviometrie_mm"] == "Rain"

    def test_missing_column_returns_none(self):
        df = pd.DataFrame({"colonne_inconnue": [1, 2, 3]})
        mapping = detect_columns(df)
        for val in mapping.values():
            assert val is None or val == "colonne_inconnue"

    def test_synonyms_complete(self):
        """Chaque colonne standard doit avoir au moins un synonyme."""
        for col in REQUIRED_COLUMNS:
            assert col in COLUMN_SYNONYMS, f"Pas de synonymes pour {col}"
            assert len(COLUMN_SYNONYMS[col]) >= 1


class TestValidateAndClean:
    """Tests pour validate_and_clean."""

    def test_renaming_applied(self, sample_csv_df):
        mapping = {
            "region": "region", "culture": "culture", "type_sol": "type_sol",
            "surface_ha": "surface_ha", "pluviometrie_mm": "pluviometrie_mm",
            "temperature_moyenne_c": "temperature_moyenne_c",
        }
        df_clean, warnings = validate_and_clean(sample_csv_df, mapping)
        assert "region" in df_clean.columns
        assert "surface_ha" in df_clean.columns

    def test_nan_imputation(self):
        df = pd.DataFrame({
            "region": ["Kara", "Maritime"],
            "surface_ha": [5.0, None],
            "pluviometrie_mm": [900.0, 800.0],
            "temperature_moyenne_c": [27.0, 28.0],
        })
        mapping = {k: k for k in df.columns}
        df_clean, warnings = validate_and_clean(df, mapping)
        assert df_clean["surface_ha"].isna().sum() == 0
        assert len(warnings) > 0  # Warning sur l'imputation

    def test_duplicates_removed(self):
        df = pd.DataFrame({
            "region": ["Kara", "Kara"],
            "culture": ["Maïs", "Maïs"],
            "surface_ha": [5.0, 5.0],
        })
        mapping = {k: k for k in df.columns}
        df_clean, warnings = validate_and_clean(df, mapping)
        assert len(df_clean) == 1
        assert any("doublon" in w.lower() for w in warnings)

    def test_string_stripping(self, sample_csv_df):
        df = sample_csv_df.copy()
        df["region"] = "  kara  "
        mapping = {k: k for k in df.columns}
        df_clean, _ = validate_and_clean(df, mapping)
        assert df_clean["region"].iloc[0] == "Kara"


class TestGetStatsSummary:
    """Tests pour get_stats_summary."""

    def test_basic_stats(self, sample_csv_df):
        stats = get_stats_summary(sample_csv_df)
        assert stats["n_lignes"] == 3
        assert stats["n_colonnes"] == 7

    def test_rendement_stats(self, sample_csv_df):
        stats = get_stats_summary(sample_csv_df)
        assert "rendement_moyen" in stats
        assert stats["rendement_moyen"] == pytest.approx(
            sample_csv_df["rendement_t_ha"].mean(), abs=0.001
        )
        assert stats["rendement_max"] == pytest.approx(3.1, abs=0.001)
        assert stats["rendement_min"] == pytest.approx(1.8, abs=0.001)

    def test_culture_frequency(self, sample_csv_df):
        stats = get_stats_summary(sample_csv_df)
        assert "culture_freq" in stats
        assert "Maïs" in stats["culture_freq"]

    def test_surface_total(self, sample_csv_df):
        stats = get_stats_summary(sample_csv_df)
        assert stats["surface_totale_ha"] == pytest.approx(16.3, abs=0.1)

    def test_missing_values_count(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": [None, 2, None]})
        stats = get_stats_summary(df)
        assert stats["valeurs_manquantes"] == 3
