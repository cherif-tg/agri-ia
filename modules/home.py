"""
modules/home.py
===============
Page d'accueil de l'application AgroPredict Togo.
"""

import streamlit as st

from modules.styles import kpi_card


def render() -> None:
    """Affiche la page d'accueil."""

    # Section héros
    st.markdown("""
    <div class="card" style="text-align:center; padding:2rem;">
        <h2 style="color:#1B5E20; margin:0 0 .5rem;">Bienvenue sur <strong>AgroPredict Togo</strong></h2>
        <p style="color:#616161; font-size:1rem; max-width:600px; margin:auto;">
            Plateforme d'intelligence artificielle dédiée à l'agriculture togolaise.
            Prévisions de rendement, analyse climatique, aide à la décision.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI rapides ───────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Régions couvertes", "5", "Maritime → Savanes"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Cultures analysées", "3", "Maïs · Sorgho · Mil"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Précision modèle", ">88%", "R² validation croisée"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Données météo", "Temps réel", "Open-Meteo API"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Features cards ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Fonctionnalités disponibles</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    features = [
        ("🌾", "Prévision de rendement",
         "Estimation précise du rendement (t/ha) et de la production totale à partir "
         "des données de votre exploitation. Modèle XGBoost + LightGBM optimisé."),
        ("📊", "Visualisations & Analyses",
         "Graphiques interactifs : tendances régionales, impact climatique, calendrier "
         "cultural, carte des rendements."),
        ("📂", "Analyse de fichiers (RAG)",
         "Importez vos propres fichiers CSV, Excel ou PDF. Le système détecte "
         "automatiquement les colonnes et génère des prévisions et visualisations."),
        ("🤖", "AgroBot – Assistant IA",
         "Chatbot alimenté par Groq (LLaMA 3.3-70B). Posez vos questions en français "
         "sur l'agronomie, les cultures, la météo et les prévisions."),
        ("📋", "Historique & Rapports",
         "Consultez toutes vos prévisions enregistrées, exportez-les en CSV, "
         "suivez l'évolution de vos rendements dans le temps."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card card-green" style="height:180px;">
                <div style="font-size:2rem;">{icon}</div>
                <strong style="color:#1B5E20;">{title}</strong>
                <p style="font-size:.85rem; color:#616161; margin-top:.4rem;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Guide rapide ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Démarrage rapide</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <ol style="margin:0; padding-left:1.2rem; line-height:2;">
            <li>Allez dans <strong>🌾 Prévision</strong> et renseignez les informations de votre exploitation.</li>
            <li>Le système récupère automatiquement la météo en temps réel de votre région.</li>
            <li>Obtenez votre prévision de rendement, le niveau de risque et les recommandations.</li>
            <li>Exportez vos résultats ou consultez les <strong>📊 Visualisations</strong>.</li>
            <li>Utilisez <strong>📂 Analyse de fichiers</strong> pour importer vos propres données.</li>
            <li>Posez vos questions à <strong>🤖 AgroBot</strong>.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # ── Zones géographiques ───────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:1.5rem;">Régions couvertes</div>',
                unsafe_allow_html=True)

    regions_info = {
        "Maritime":  {"ville": "Lomé",     "pluie": "900 mm/an",  "sol": "Sableux/Argileux"},
        "Plateaux":  {"ville": "Kpalimé",  "pluie": "1200 mm/an", "sol": "Argilo-limoneux"},
        "Centrale":  {"ville": "Sokodé",   "pluie": "1100 mm/an", "sol": "Argileux"},
        "Kara":      {"ville": "Kara",     "pluie": "1000 mm/an", "sol": "Argilo-sableux"},
        "Savanes":   {"ville": "Dapaong",  "pluie": "800 mm/an",  "sol": "Sableux"},
    }

    cols2 = st.columns(5)
    for i, (region, info) in enumerate(regions_info.items()):
        with cols2[i]:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">{region}</div>
                <div style="font-size:.85rem; color:#388E3C; font-weight:600;">{info['ville']}</div>
                <div class="kpi-sub">🌧 {info['pluie']}</div>
                <div class="kpi-sub">🪨 {info['sol']}</div>
            </div>""", unsafe_allow_html=True)
