"""
modules/report.py
=================
Page de rapports : synthèse des prévisions, métriques du modèle ML, export.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.styles import kpi_card


def render(model) -> None:
    """Affiche la page de rapports."""
    st.markdown('<div class="section-title"> Rapports & Synthèse</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_perf, tab_synthese, tab_modele = st.tabs([
        " Synthèse des prévisions",
        "🗓 Rapport mensuel",
        " Performance du modèle",
    ])

    with tab_perf:
        _tab_synthese()

    with tab_synthese:
        _tab_mensuel()

    with tab_modele:
        _tab_modele_perf(model)


# ── Onglets ───────────────────────────────────────────────────────────────────

def _tab_synthese() -> None:
    historique = st.session_state.get("historique", [])

    if not historique:
        st.info("Aucune prévision dans l'historique. Réalisez des prévisions pour générer un rapport.")
        return

    df = pd.DataFrame(historique)

    # KPI
    kc1, kc2, kc3, kc4 = st.columns(4)
    with kc1:
        st.markdown(kpi_card("Prévisions totales", str(len(df))), unsafe_allow_html=True)
    with kc2:
        st.markdown(kpi_card("Rendement moyen", f"{df['rendement_t_ha'].mean():.2f} t/ha"),
                     unsafe_allow_html=True)
    with kc3:
        st.markdown(kpi_card("Production totale", f"{df['production_t'].sum():.1f} t"),
                     unsafe_allow_html=True)
    with kc4:
        n_faible = (df["risque"] == "Faible").sum() if "risque" in df.columns else 0
        pct = round(n_faible / len(df) * 100) if len(df) else 0
        st.markdown(kpi_card("Risque faible", f"{pct}%", "des prévisions"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Répartition par culture
    if "culture" in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names="culture", title="Répartition par culture",
                          color_discrete_map={"Maïs": "#4CAF50", "Sorgho": "#FF8F00", "Mil": "#42A5F5"})
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df.groupby("region")["rendement_t_ha"].mean().reset_index(),
                           x="region", y="rendement_t_ha",
                           color="rendement_t_ha", color_continuous_scale="Greens",
                           title="Rendement moyen par région",
                           labels={"rendement_t_ha": "Rendement (t/ha)", "region": "Région"})
            fig2.update_layout(height=350, plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA")
            st.plotly_chart(fig2, use_container_width=True)

    # Répartition des risques
    if "risque" in df.columns:
        risk_counts = df["risque"].value_counts().reset_index()
        risk_counts.columns = ["Niveau de risque", "Nombre"]
        color_map = {"Faible": "#4CAF50", "Modéré": "#FFCA28", "Élevé": "#EF5350"}
        fig3 = px.bar(risk_counts, x="Niveau de risque", y="Nombre",
                       color="Niveau de risque", color_discrete_map=color_map,
                       title="Distribution des niveaux de risque")
        fig3.update_layout(height=350, showlegend=False,
                            plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA")
        st.plotly_chart(fig3, use_container_width=True)

    # Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Exporter la synthèse (CSV)",
        data=csv,
        file_name=f"rapport_synthese_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def _tab_mensuel() -> None:
    historique = st.session_state.get("historique", [])

    st.markdown("#### Rapport d'activité mensuel")

    if not historique:
        st.info("Aucune donnée disponible pour le moment.")
        return

    df = pd.DataFrame(historique)
    df["date"] = pd.to_datetime(df["date"])
    df["mois"] = df["date"].dt.to_period("M").astype(str)

    mois_dispo = df["mois"].unique().tolist()
    mois_select = st.selectbox("Sélectionner le mois", sorted(mois_dispo, reverse=True))

    df_mois = df[df["mois"] == mois_select]

    if df_mois.empty:
        st.info("Aucune prévision ce mois-ci.")
        return

    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(kpi_card("Prévisions", str(len(df_mois)), mois_select), unsafe_allow_html=True)
    with kc2:
        st.markdown(kpi_card("Rendement moyen", f"{df_mois['rendement_t_ha'].mean():.2f} t/ha"),
                     unsafe_allow_html=True)
    with kc3:
        st.markdown(kpi_card("Production", f"{df_mois['production_t'].sum():.1f} t"),
                     unsafe_allow_html=True)

    st.dataframe(df_mois.drop(columns=["mois"], errors="ignore"), use_container_width=True, hide_index=True)


def _tab_modele_perf(model) -> None:
    st.markdown("#### Performance du modèle ML")

    metrics = model.get_metrics() if model else {}

    if not metrics:
        st.info("Métriques indisponibles. Entraînez d'abord le modèle.")
        return

    # KPI métriques
    kc1, kc2, kc3, kc4 = st.columns(4)
    with kc1:
        st.markdown(kpi_card("R² (test)", f"{metrics.get('R2', '–')}", "Qualité globale"),
                     unsafe_allow_html=True)
    with kc2:
        st.markdown(kpi_card("MAE", f"{metrics.get('MAE', '–')} t/ha", "Erreur absolue moy."),
                     unsafe_allow_html=True)
    with kc3:
        st.markdown(kpi_card("RMSE", f"{metrics.get('RMSE', '–')} t/ha", "Racine err. quadratique"),
                     unsafe_allow_html=True)
    with kc4:
        st.markdown(kpi_card("MAPE", f"{metrics.get('MAPE_pct', '–')}%", "Erreur relative moy."),
                     unsafe_allow_html=True)

    # Validation croisée
    cv_mean = metrics.get("CV_R2_mean")
    cv_std  = metrics.get("CV_R2_std")
    if cv_mean is not None:
        st.markdown(f"""
        <div class="alert-success">
            <strong>Validation croisée (5-fold) : R² = {cv_mean:.3f} ± {cv_std:.3f}</strong><br>
            Un R² élevé avec un faible écart-type confirme la stabilité et la généralisation du modèle.
        </div>""", unsafe_allow_html=True)

    # Feature importance
    fi = metrics.get("feature_importance", {})
    if fi:
        st.markdown("#### Importance des variables")
        fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance"])
        fi_df = fi_df.sort_values("Importance", ascending=True).tail(12)

        fig = px.bar(fi_df, x="Importance", y="Feature", orientation="h",
                      color="Importance", color_continuous_scale="Greens",
                      title="Importance des features – XGBoost",
                      labels={"Importance": "Score d'importance", "Feature": "Variable"})
        fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
                           showlegend=False, height=420)
        st.plotly_chart(fig, use_container_width=True)

    # Taille des données
    n_train = metrics.get("n_train", "–")
    n_test  = metrics.get("n_test", "–")
    st.markdown(f"""
    <div class="card">
        <strong>Données d'entraînement :</strong> {n_train} échantillons<br>
        <strong>Données de test :</strong> {n_test} échantillons<br>
        <strong>Modèle :</strong> Ensemble XGBoost + LightGBM (Optuna optimization)
    </div>""", unsafe_allow_html=True)
