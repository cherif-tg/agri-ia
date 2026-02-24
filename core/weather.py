"""
core/weather.py
===============
Module météorologique : récupère les données en temps réel via Open-Meteo (gratuit).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Coordonnées des régions du Togo
REGIONS_COORDS: Dict[str, Dict[str, float]] = {
    "Maritime": {"lat": 6.1256,  "lon": 1.2256},
    "Plateaux": {"lat": 6.9000,  "lon": 0.8500},
    "Centrale": {"lat": 8.9711,  "lon": 1.1056},
    "Kara":     {"lat": 9.5511,  "lon": 1.1856},
    "Savanes":  {"lat": 10.5700, "lon": 0.2200},
}

_OPEN_METEO_URL  = "https://api.open-meteo.com/v1/forecast"
_ARCHIVE_URL     = "https://archive-api.open-meteo.com/v1/archive"
_TIMEOUT         = 12


def get_current_weather(region: str) -> Dict:
    """
    Récupère la météo actuelle (7 jours de prévision) pour une région du Togo.

    Retourne un dictionnaire avec :
    - success           : bool
    - temperature_c     : température actuelle (°C)
    - temp_max / min    : max/min sur 7 jours (°C)
    - temp_moyenne_7j   : moyenne sur 7 jours (°C)
    - precipitation_7j  : cumul sur 7 jours (mm)
    - humidite_pct      : humidité relative (%)
    - vent_kmh          : vitesse du vent (km/h)
    - source            : "Open-Meteo"
    """
    if region not in REGIONS_COORDS:
        return {"success": False, "error": f"Région inconnue: {region}"}

    coords = REGIONS_COORDS[region]
    params = {
        "latitude":  coords["lat"],
        "longitude": coords["lon"],
        "current":   ["temperature_2m", "precipitation", "relative_humidity_2m", "wind_speed_10m"],
        "daily":     ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                      "temperature_2m_mean"],
        "timezone":  "Africa/Lome",
        "forecast_days": 7,
    }

    try:
        resp = requests.get(_OPEN_METEO_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily   = data.get("daily", {})

        precip_list = daily.get("precipitation_sum", []) or []
        temp_mean   = daily.get("temperature_2m_mean", []) or []
        temp_max    = daily.get("temperature_2m_max", []) or []
        temp_min    = daily.get("temperature_2m_min", []) or []

        temp_moy_7j    = round(sum(t for t in temp_mean if t) / max(len(temp_mean), 1), 1)
        precip_cumul   = round(sum(p for p in precip_list if p is not None), 1)

        return {
            "success":           True,
            "region":            region,
            "temperature_c":     current.get("temperature_2m", 27.0),
            "temp_max":          max(temp_max) if temp_max else 32.0,
            "temp_min":          min(temp_min) if temp_min else 22.0,
            "temp_moyenne_7j":   temp_moy_7j,
            "precipitation_7j":  precip_cumul,
            "humidite_pct":      current.get("relative_humidity_2m", 60),
            "vent_kmh":          current.get("wind_speed_10m", 0),
            "source":            "Open-Meteo",
            "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except requests.exceptions.Timeout:
        return _fallback(region, "Timeout de connexion")
    except requests.exceptions.RequestException as exc:
        return _fallback(region, str(exc))


def get_historical_pluvio(region: str, days: int = 90) -> Dict:
    """
    Récupère le cumul de précipitations historiques (90 derniers jours par défaut).

    Utile pour estimer la saison pluvieuse en cours.
    """
    if region not in REGIONS_COORDS:
        return {"success": False, "pluvio_cumul_mm": 800}

    coords    = REGIONS_COORDS[region]
    date_end  = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    params = {
        "latitude":   coords["lat"],
        "longitude":  coords["lon"],
        "start_date": date_start,
        "end_date":   date_end,
        "daily":      ["precipitation_sum", "temperature_2m_mean"],
        "timezone":   "Africa/Lome",
    }

    try:
        resp = requests.get(_ARCHIVE_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily", {})

        precip_list = daily.get("precipitation_sum") or []
        temp_list   = daily.get("temperature_2m_mean") or []

        pluvio  = round(sum(p for p in precip_list if p is not None), 1)
        temp_moy = round(sum(t for t in temp_list if t is not None) / max(len(temp_list), 1), 1)

        return {
            "success":          True,
            "days":             days,
            "pluvio_cumul_mm":  pluvio,
            "temp_moyenne_c":   temp_moy,
            "source":           "Open-Meteo Archive",
        }

    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Erreur archive météo pour {region}: {exc}")
        return {"success": False, "pluvio_cumul_mm": 800, "temp_moyenne_c": 27.0}


# ── Données de fallback ────────────────────────────────────────────────────────

_DEFAULTS = {
    "Maritime": {"temperature_c": 28.0, "precipitation_7j": 60.0, "humidite_pct": 75},
    "Plateaux": {"temperature_c": 27.0, "precipitation_7j": 90.0, "humidite_pct": 72},
    "Centrale": {"temperature_c": 29.0, "precipitation_7j": 70.0, "humidite_pct": 55},
    "Kara":     {"temperature_c": 27.5, "precipitation_7j": 65.0, "humidite_pct": 58},
    "Savanes":  {"temperature_c": 31.0, "precipitation_7j": 40.0, "humidite_pct": 45},
}

def _fallback(region: str, error: str) -> Dict:
    """Retourne des valeurs par défaut en cas d'erreur API."""
    defaults = _DEFAULTS.get(region, {"temperature_c": 27, "precipitation_7j": 60, "humidite_pct": 60})
    logger.warning(f"Météo fallback pour {region}: {error}")
    return {
        "success":          False,
        "error":            error,
        "region":           region,
        "temperature_c":    defaults["temperature_c"],
        "temp_moy_7j":      defaults["temperature_c"],
        "temp_moyenne_7j":  defaults["temperature_c"],
        "precipitation_7j": defaults["precipitation_7j"],
        "humidite_pct":     defaults["humidite_pct"],
        "vent_kmh":         0,
        "source":           "Valeurs par défaut (hors ligne)",
        "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
