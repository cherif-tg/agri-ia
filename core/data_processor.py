"""
core/data_processor.py
======================
Utilitaires de traitement et d'analyse des données agricoles.
"""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Colonnes attendues par le modèle ML
REQUIRED_COLUMNS = {
    "region":                 "Région",
    "culture":                "Culture",
    "type_sol":               "Type de sol",
    "surface_ha":             "Surface (ha)",
    "pluviometrie_mm":        "Pluviométrie (mm)",
    "temperature_moyenne_c":  "Température moy. (°C)",
}

TARGET_COLUMN = "rendement_t_ha"

# Synonymes courants pour la détection automatique de colonnes
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "region":                ["region", "régions", "zone", "localite", "localité"],
    "culture":               ["culture", "crop", "type_culture", "produit"],
    "type_sol":              ["type_sol", "sol", "soil", "type_de_sol"],
    "surface_ha":            ["surface_ha", "surface", "ha", "superficie", "area"],
    "pluviometrie_mm":       ["pluviometrie_mm", "pluie", "rain", "precip", "precipitation",
                              "pluviometrie", "pluvio"],
    "temperature_moyenne_c": ["temperature_moyenne_c", "temp", "temperature", "temp_c",
                               "temperature_c", "temp_moy"],
    "rendement_t_ha":        ["rendement_t_ha", "rendement", "yield", "production",
                              "rendement_ha", "yield_t_ha"],
}


# ─── Détection intelligente des colonnes ─────────────────────────────────────

def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Détecte automatiquement le mapping entre les colonnes d'un DataFrame
    et les colonnes attendues par le modèle.

    Retourne un dict {nom_standard: nom_colonne_détecté | None}.
    """
    df_cols_lower = {c.lower().strip().replace(" ", "_"): c for c in df.columns}
    mapping: Dict[str, Optional[str]] = {}

    for std_col, synonyms in COLUMN_SYNONYMS.items():
        found = None
        for syn in synonyms:
            if syn in df_cols_lower:
                found = df_cols_lower[syn]
                break
        mapping[std_col] = found

    return mapping


# ─── Chargement de fichiers ───────────────────────────────────────────────────

def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Charge un fichier uploadé (CSV, Excel, PDF).

    Retourne (dataframe_ou_None, message_info).
    Pour les PDF, retourne (None, texte_extrait).
    """
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            # Essaye plusieurs encodages
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    return df, f"Fichier CSV chargé : {len(df)} lignes, {len(df.columns)} colonnes."
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
            return None, "Erreur : impossible de décoder le CSV."

        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl" if name.endswith(".xlsx") else "xlrd")
            return df, f"Fichier Excel chargé : {len(df)} lignes, {len(df.columns)} colonnes."

        elif name.endswith(".pdf"):
            text = _extract_pdf_text(uploaded_file)
            return None, text

        else:
            return None, "Format non supporté. Utilisez CSV, Excel (.xlsx/.xls) ou PDF."

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Erreur lors du chargement de {uploaded_file.name}: {exc}")
        return None, f"Erreur de chargement : {exc}"


def _extract_pdf_text(uploaded_file) -> str:
    """Extrait le texte d'un PDF avec pdfplumber."""
    try:
        import pdfplumber  # noqa: PLC0415
        with pdfplumber.open(uploaded_file) as pdf:
            pages_text = []
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- Page {i} ---\n{text}")
        return "\n\n".join(pages_text) if pages_text else "Aucun texte extractible."
    except ImportError:
        return "Module pdfplumber non installé. Installez-le avec : pip install pdfplumber"
    except Exception as exc:  # noqa: BLE001
        return f"Erreur d'extraction PDF : {exc}"


# ─── Validation et nettoyage ─────────────────────────────────────────────────

def validate_and_clean(df: pd.DataFrame, col_mapping: Dict[str, str]) -> Tuple[pd.DataFrame, List[str]]:
    """
    Valide et nettoie un DataFrame remappé.

    Retourne (df_nettoyé, liste_avertissements).
    """
    warnings: List[str] = []
    df_clean = df.copy()

    # Renommage
    rename_map = {v: k for k, v in col_mapping.items() if v and v in df_clean.columns}
    df_clean = df_clean.rename(columns=rename_map)

    # Séquence de nettoyage sur les colonnes numériques
    for num_col in ["surface_ha", "pluviometrie_mm", "temperature_moyenne_c", "rendement_t_ha"]:
        if num_col in df_clean.columns:
            before = df_clean[num_col].isna().sum()
            df_clean[num_col] = pd.to_numeric(df_clean[num_col], errors="coerce")
            df_clean[num_col] = df_clean[num_col].fillna(df_clean[num_col].median())
            after = df_clean[num_col].isna().sum()
            if before > 0:
                warnings.append(f"{num_col} : {before} valeur(s) manquante(s) imputée(s) par la médiane.")

    # Nettoyage des catégorielles
    for cat_col in ["region", "culture", "type_sol"]:
        if cat_col in df_clean.columns:
            df_clean[cat_col] = df_clean[cat_col].astype(str).str.strip().str.title()

    # Suppression des doublons
    n_before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    if len(df_clean) < n_before:
        warnings.append(f"{n_before - len(df_clean)} doublon(s) supprimé(s).")

    return df_clean, warnings


def get_stats_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule des statistiques descriptives pour un DataFrame agricole.
    """
    stats: Dict[str, Any] = {
        "n_lignes":  len(df),
        "n_colonnes": len(df.columns),
        "valeurs_manquantes": int(df.isna().sum().sum()),
    }

    if "rendement_t_ha" in df.columns:
        stats["rendement_moyen"]  = round(df["rendement_t_ha"].mean(), 3)
        stats["rendement_max"]    = round(df["rendement_t_ha"].max(), 3)
        stats["rendement_min"]    = round(df["rendement_t_ha"].min(), 3)
        stats["rendement_std"]    = round(df["rendement_t_ha"].std(), 3)

    if "culture" in df.columns:
        stats["cultures"]         = df["culture"].unique().tolist()
        stats["culture_freq"]     = df["culture"].value_counts().to_dict()

    if "region" in df.columns:
        stats["regions"]          = df["region"].unique().tolist()

    if "surface_ha" in df.columns:
        stats["surface_totale_ha"] = round(df["surface_ha"].sum(), 1)

    return stats
