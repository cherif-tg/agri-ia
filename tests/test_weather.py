"""
tests/test_weather.py
=====================
Tests du module météo (core/weather.py).

Exécution :
    pytest tests/test_weather.py -v
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.weather import get_current_weather, get_historical_pluvio, REGIONS_COORDS, _fallback


class TestGetCurrentWeather:
    """Tests pour get_current_weather."""

    def test_invalid_region(self):
        result = get_current_weather("RegionInexistante")
        assert result["success"] is False
        assert "inconnu" in result["error"].lower()

    def test_valid_regions_structure(self):
        """Vérifie que toutes les régions ont bien des coordonnées."""
        for region in ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]:
            assert region in REGIONS_COORDS
            assert "lat" in REGIONS_COORDS[region]
            assert "lon" in REGIONS_COORDS[region]

    @patch("core.weather.requests.get")
    def test_success_response(self, mock_get):
        """Simule une réponse API réussie."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 28.5,
                "precipitation": 2.1,
                "relative_humidity_2m": 72,
                "wind_speed_10m": 12.4,
            },
            "daily": {
                "temperature_2m_max":  [30, 31, 29, 32, 30, 31, 29],
                "temperature_2m_min":  [22, 23, 22, 24, 22, 23, 21],
                "precipitation_sum":   [5, 0, 10, 2, 0, 3, 8],
                "temperature_2m_mean": [26, 27, 25.5, 28, 26, 27, 25],
            },
        }
        mock_get.return_value = mock_response

        result = get_current_weather("Maritime")

        assert result["success"] is True
        assert result["temperature_c"] == 28.5
        assert result["humidite_pct"] == 72
        assert result["precipitation_7j"] == pytest.approx(28.0, abs=1)

    @patch("core.weather.requests.get")
    def test_timeout_returns_fallback(self, mock_get):
        """En cas de timeout, la fonction retourne des valeurs par défaut."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout

        result = get_current_weather("Kara")

        assert result["success"] is False
        assert "temperature_c" in result or "temperature_moyenne_7j" in result or "temp_moyenne_7j" in result

    def test_fallback_structure(self):
        """_fallback doit toujours retourner les clés minimales."""
        fb = _fallback("Maritime", "test error")
        assert fb["success"] is False
        assert "temperature_c" in fb
        assert "precipitation_7j" in fb


class TestGetHistoricalPluvio:
    """Tests pour get_historical_pluvio."""

    def test_invalid_region(self):
        result = get_historical_pluvio("RegionBidon123")
        assert result["success"] is False

    @patch("core.weather.requests.get")
    def test_success_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "daily": {
                "precipitation_sum":   [5, 0, 10, 2, 0] * 18,
                "temperature_2m_mean": [27, 28, 26, 29, 27] * 18,
            }
        }
        mock_get.return_value = mock_response

        result = get_historical_pluvio("Kara", days=90)

        assert result["success"] is True
        assert result["pluvio_cumul_mm"] > 0
        assert result["temp_moyenne_c"] > 0
