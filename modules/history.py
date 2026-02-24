"""
modules/history.py
==================
Page d'historique des prévisions.
Tableau récapitulatif, statistiques, export CSV.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.styles import kpi_card


def render() -> None:
    """Affiche la page d'historique."""
    st.markdown('<div class="section-title"> Historique des Prévisions</div>', unsafe_allow_html=True)

    historique = st.session_state.get("historique", [])

    if not historique:
        st.markdown("""
        <div class="card" style="text-align:center; padding:3rem; color:#757575;">
            <div style="font-size:3rem;"></div>
            <h3>Aucune prévision enregistrée</h3>
            <p>Rendez-vous dans <strong>🌾 Prévision</strong> pour générer votre première prévision.</p>
        </div>""", unsafe_allow_html=True)
        return

    df = pd.DataFrame(historique)

    # ── KPI rapides ───────────────────────────────────────────────────────────
    kc1, kc2, kc3, kc4 = st.columns(4)
    with kc1:
        st.markdown(kpi_card("Prévisions", str(len(df)), "au total"), unsafe_allow_html=True)
    with kc2:
        st.markdown(kpi_card("Rendement moyen",
                             f"{df['rendement_t_ha'].mean():.2f} t/ha",
                             "toutes cultures"), unsafe_allow_html=True)
    with kc3:
        st.markdown(kpi_card("Production totale",
                             f"{df['production_t'].sum():.1f} t",
                             "cumulée"), unsafe_allow_html=True)
    with kc4:
        culture_freq = df["culture"].mode()[0] if not df.empty else "–"
        st.markdown(kpi_card("Culture principale", culture_freq, ""),
                     unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filtres ────────────────────────────────────────────────────────────────
    with st.expander(" Filtrer l'historique"):
        f1, f2, f3 = st.columns(3)
        with f1:
            cultures_dispo = df["culture"].unique().tolist()
            selected_cultures = st.multiselect("Culture", cultures_dispo, default=cultures_dispo)
        with f2:
            regions_dispo = df["region"].unique().tolist()
            selected_regions  = st.multiselect("Région",  regions_dispo, default=regions_dispo)
        with f3:
            risques_dispo = df["risque"].unique().tolist() if "risque" in df.columns else []
            selected_risques  = st.multiselect("Risque",  risques_dispo, default=risques_dispo)

    mask = (
        df["culture"].isin(selected_cultures) &
        df["region"].isin(selected_regions)
    )
    if "risque" in df.columns and selected_risques:
        mask = mask & df["risque"].isin(selected_risques)

    df_filtered = df[mask].copy()

    # ── Tableau ────────────────────────────────────────────────────────────────
    st.markdown(f"**{len(df_filtered)} prévision(s) affichée(s)**")

    display_cols = [c for c in [
        "date", "region", "culture", "surface_ha", "rendement_t_ha",
        "production_t", "risque", "irrigation", "fertilisation",
    ] if c in df_filtered.columns]

    styled = df_filtered[display_cols].rename(columns={
        "date": "Date", "region": "Région", "culture": "Culture",
        "surface_ha": "Surface (ha)", "rendement_t_ha": "Rendement (t/ha)",
        "production_t": "Production (t)", "risque": "Risque",
        "irrigation": "Irrigation", "fertilisation": "Fertilisation",
    })
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Évolution dans le temps ────────────────────────────────────────────────
    if len(df_filtered) > 1:
        st.markdown("#### Évolution des rendements")
        fig = px.line(
            df_filtered, x="date", y="rendement_t_ha", color="culture",
            markers=True,
            title="Rendements prévus dans le temps",
            color_discrete_map={"Maïs": "#4CAF50", "Sorgho": "#FF8F00", "Mil": "#42A5F5"},
            labels={"date": "Date", "rendement_t_ha": "Rendement (t/ha)", "culture": "Culture"},
        )
        fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=380)
        st.plotly_chart(fig, use_container_width=True)

    # ── Actions ────────────────────────────────────────────────────────────────
    a1, a2 = st.columns(2)
    with a1:
        csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Exporter l'historique (CSV)",
            data=csv_bytes,
            file_name="historique_previsions.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with a2:
        if st.button("🗑 Effacer l'historique", use_container_width=True):
            st.session_state.historique = []
            st.rerun()
