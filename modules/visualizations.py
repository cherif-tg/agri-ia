"""
modules/visualizations.py
==========================
Page de visualisations et analyses des données agricoles.
Onglets : Tendances régionales, Impact climatique, Calendrier cultural, Carte.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import CULTURES, REGIONS, DATA_CSV_PATH


@st.cache_data(show_spinner=False)
def _load_data() -> pd.DataFrame:
    """Charge le CSV de données historiques (mis en cache)."""
    try:
        return pd.read_csv(DATA_CSV_PATH)
    except FileNotFoundError:
        return _generate_sample_data()


def _generate_sample_data() -> pd.DataFrame:
    """Génère un jeu de données synthétique si le CSV est absent."""
    rng = np.random.default_rng(42)
    rows = []
    for _ in range(300):
        region   = rng.choice(REGIONS)
        culture  = rng.choice(CULTURES)
        type_sol = rng.choice(["Argileux", "Sableux", "Limoneux"])
        pluvio   = rng.integers(400, 1500)
        temp     = round(rng.uniform(22, 34), 1)
        surface  = round(rng.uniform(0.5, 10), 2)
        rendement = round(1.2 + pluvio / 600 - abs(temp - 27) * 0.05 + rng.normal(0, 0.3), 2)
        rows.append({"region": region, "culture": culture, "type_sol": type_sol,
                     "surface_ha": surface, "pluviometrie_mm": pluvio,
                     "temperature_moyenne_c": temp, "rendement_t_ha": max(rendement, 0.3)})
    return pd.DataFrame(rows)


def render() -> None:
    """Affiche la page de visualisations."""
    st.markdown('<div class="section-title"> Visualisations & Analyses</div>', unsafe_allow_html=True)
    st.markdown("Explorez les données historiques et les tendances agricoles du Togo.")
    st.markdown("<br>", unsafe_allow_html=True)

    df = _load_data()

    tab_regions, tab_climat, tab_calendrier, tab_map = st.tabs([
        "🗺 Tendances Régionales",
        "🌧 Impact Climatique",
        " Calendrier Cultural",
        " Carte des Rendements",
    ])

    # ── Onglet 1 : Tendances régionales ──────────────────────────────────────
    with tab_regions:
        _tab_tendances(df)

    # ── Onglet 2 : Impact climatique ─────────────────────────────────────────
    with tab_climat:
        _tab_climat(df)

    # ── Onglet 3 : Calendrier ─────────────────────────────────────────────────
    with tab_calendrier:
        _tab_calendrier()

    # ── Onglet 4 : Carte ──────────────────────────────────────────────────────
    with tab_map:
        _tab_carte(df)


# ─── Implémentation des onglets ───────────────────────────────────────────────

def _tab_tendances(df: pd.DataFrame) -> None:
    c1, c2 = st.columns([1, 3])
    with c1:
        selected_cultures = st.multiselect("Cultures", CULTURES, default=CULTURES)
        selected_regions  = st.multiselect("Régions",  REGIONS,  default=REGIONS)

    filtered = df[df["culture"].isin(selected_cultures) & df["region"].isin(selected_regions)]

    if filtered.empty:
        st.info("Aucune donnée pour ces filtres.")
        return

    with c2:
        agg = filtered.groupby(["region", "culture"])["rendement_t_ha"].mean().reset_index()
        fig = px.bar(
            agg, x="region", y="rendement_t_ha", color="culture",
            barmode="group",
            title="Rendement moyen par Région et Culture (t/ha)",
            color_discrete_map={"Maïs": "#4CAF50", "Sorgho": "#FF8F00", "Mil": "#42A5F5"},
            labels={"rendement_t_ha": "Rendement (t/ha)", "region": "Région", "culture": "Culture"},
        )
        fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
                           font=dict(family="Inter, Segoe UI"), height=420)
        st.plotly_chart(fig, use_container_width=True)

    # Distribution des rendements
    fig2 = px.box(
        filtered, x="culture", y="rendement_t_ha", color="culture",
        points="outliers",
        title="Distribution des rendements par culture",
        color_discrete_map={"Maïs": "#4CAF50", "Sorgho": "#FF8F00", "Mil": "#42A5F5"},
        labels={"rendement_t_ha": "Rendement (t/ha)", "culture": "Culture"},
    )
    fig2.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
                        height=380, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)


def _tab_climat(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    # Pluie vs Rendement (scatter + tendance)
    with col1:
        culture_sel = st.selectbox("Culture", CULTURES, key="climate_culture")
        df_c = df[df["culture"] == culture_sel]

        fig = px.scatter(
            df_c, x="pluviometrie_mm", y="rendement_t_ha",
            color="region",
            title=f"Pluviométrie vs Rendement — {culture_sel}",
            labels={"pluviometrie_mm": "Pluviométrie (mm)", "rendement_t_ha": "Rendement (t/ha)"},
            opacity=0.7,
        )
        fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Température vs Rendement
    with col2:
        fig2 = px.scatter(
            df_c, x="temperature_moyenne_c", y="rendement_t_ha",
            color="region",
            title=f"Température vs Rendement — {culture_sel}",
            labels={"temperature_moyenne_c": "Température moy. (°C)", "rendement_t_ha": "Rendement (t/ha)"},
            opacity=0.7,
        )
        fig2.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # Heatmap : Région × Culture
    pivot = df.groupby(["region", "culture"])["rendement_t_ha"].mean().unstack()
    fig3 = px.imshow(
        pivot, color_continuous_scale="Greens",
        title="Heatmap : Rendement moyen (t/ha) — Région × Culture",
        labels={"color": "Rendement (t/ha)"},
        text_auto=".2f",
    )
    fig3.update_layout(height=380)
    st.plotly_chart(fig3, use_container_width=True)


def _tab_calendrier() -> None:
    calendrier = [
        {"Culture": "Maïs",   "Saison": "1ère", "Semis": "Mars – Avril",  "Récolte": "Juin – Juillet",
         "Durée (j)": 95,  "Début": "2026-03-01", "Fin": "2026-06-04"},
        {"Culture": "Maïs",   "Saison": "2ème", "Semis": "Août – Sept",   "Récolte": "Nov – Déc",
         "Durée (j)": 95,  "Début": "2026-08-01", "Fin": "2026-11-03"},
        {"Culture": "Sorgho", "Saison": "1ère", "Semis": "Avril – Mai",   "Récolte": "Sept – Oct",
         "Durée (j)": 120, "Début": "2026-04-01", "Fin": "2026-07-29"},
        {"Culture": "Sorgho", "Saison": "2ème", "Semis": "Septembre",     "Récolte": "Janvier",
         "Durée (j)": 120, "Début": "2026-09-01", "Fin": "2026-12-30"},
        {"Culture": "Mil",    "Saison": "1ère", "Semis": "Mai – Juin",    "Récolte": "Sept – Oct",
         "Durée (j)": 105, "Début": "2026-05-01", "Fin": "2026-08-14"},
    ]

    df_cal = pd.DataFrame(calendrier)
    st.dataframe(df_cal[["Culture", "Saison", "Semis", "Récolte", "Durée (j)"]],
                  use_container_width=True, hide_index=True)

    # Gantt chart
    df_gantt = df_cal.copy()
    df_gantt["Début"] = pd.to_datetime(df_gantt["Début"])
    df_gantt["Fin"]   = pd.to_datetime(df_gantt["Fin"])

    fig = px.timeline(
        df_gantt, x_start="Début", x_end="Fin",
        y="Culture", color="Saison",
        title="Calendrier cultural 2026",
        color_discrete_sequence=["#4CAF50", "#FF8F00"],
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="alert-success">
        <strong>Note :</strong> Ces périodes sont indicatives. Dans les régions Savanes et Kara,
        la première saison peut démarrer plus tard (avril-mai) en raison d'un régime pluviométrique différent.
    </div>""", unsafe_allow_html=True)


def _tab_carte(df: pd.DataFrame) -> None:
    from config import REGIONS_COORDINATES

    agg = df.groupby("region")["rendement_t_ha"].mean().reset_index()
    agg["lat"] = agg["region"].map(lambda r: REGIONS_COORDINATES.get(r, {}).get("lat", 8.0))
    agg["lon"] = agg["region"].map(lambda r: REGIONS_COORDINATES.get(r, {}).get("lon", 1.0))

    fig = px.scatter_mapbox(
        agg, lat="lat", lon="lon",
        size="rendement_t_ha",
        color="rendement_t_ha",
        hover_name="region",
        hover_data={"rendement_t_ha": ":.2f"},
        color_continuous_scale="Greens",
        size_max=40,
        zoom=5.5,
        center={"lat": 8.5, "lon": 1.0},
        mapbox_style="carto-positron",
        title="Rendement moyen par région (t/ha)",
    )
    fig.update_layout(height=520, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    # Tableau récapitulatif
    st.dataframe(
        agg[["region", "rendement_t_ha"]].rename(
            columns={"region": "Région", "rendement_t_ha": "Rendement moyen (t/ha)"}
        ).sort_values("Rendement moyen (t/ha)", ascending=False).style.format({"Rendement moyen (t/ha)": "{:.2f}"}),
        use_container_width=True, hide_index=True,
    )
