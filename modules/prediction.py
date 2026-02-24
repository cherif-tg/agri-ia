"""
modules/prediction.py
=====================
Page de prévision du rendement agricole.
Formulaire intelligent avec météo temps réel et résultats détaillés.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CULTURES, REGIONS, TYPES_SOL
from core.weather import get_current_weather, get_historical_pluvio
from modules.styles import kpi_card, risk_badge


def render(model) -> None:
    """
    Affiche la page de prévision.

    Paramètres
    ----------
    model : instance AgroPredictModel déjà chargée/entraînée
    """
    st.markdown('<div class="section-title">🌾 Nouvelle Prévision Agricole</div>', unsafe_allow_html=True)
    st.markdown("Renseignez les informations de votre exploitation pour obtenir une prévision personnalisée.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Formulaire ────────────────────────────────────────────────────────────
    with st.form("form_prevision", clear_on_submit=False):
        col_form1, col_form2, col_form3 = st.columns([1.2, 1.2, 1.4])

        # Colonne 1 : Exploitation
        with col_form1:
            st.markdown("#### 🏡 Exploitation")
            region  = st.selectbox("Région", REGIONS, help="Région agricole concernée")
            culture = st.selectbox("Culture", CULTURES, help="Type de culture à analyser")
            type_sol = st.selectbox("Type de sol", TYPES_SOL)
            surface  = st.number_input("Surface cultivée (ha)", min_value=0.1, max_value=2000.0,
                                        value=5.0, step=0.5)

        # Colonne 2 : Pratiques agricoles
        with col_form2:
            st.markdown("#### 🌿 Pratiques")
            irrigation   = st.selectbox("Irrigation",
                                         ["Aucun", "Traditionnel", "Goutte à goutte", "Aspersion"])
            fertilisation = st.selectbox("Fertilisation",
                                          ["Aucune", "Organique", "Chimique", "Mixte"])
            date_semis    = st.date_input("Date de semis", value=date.today())
            use_realtime  = st.checkbox("Météo temps réel ✓", value=True,
                                         help="Récupère automatiquement la météo de votre région")

        # Colonne 3 : Données climatiques
        with col_form3:
            st.markdown("#### 🌦️ Données climatiques")

            if use_realtime:
                with st.spinner(f"Récupération météo {region}..."):
                    weather = get_current_weather(region)
                    hist    = get_historical_pluvio(region, days=90)

                if weather["success"]:
                    st.success("Météo récupérée ✓")
                    st.caption(f"Source: {weather['source']} — {weather['timestamp']}")
                    default_temp   = weather["temp_moyenne_7j"]
                    default_pluvio = int(hist.get("pluvio_cumul_mm", weather["precipitation_7j"] * 13))
                else:
                    st.warning("Connexion indisponible – valeurs par défaut")
                    default_temp   = 27.0
                    default_pluvio = 800
            else:
                default_temp   = 27.0
                default_pluvio = 800

            temperature_moy = st.number_input("Température moyenne (°C)", min_value=15.0,
                                               max_value=45.0, value=float(default_temp), step=0.5)
            pluviometrie    = st.number_input("Pluviométrie cumulée (mm)", min_value=0,
                                               max_value=3000, value=int(default_pluvio), step=50)

            if use_realtime and weather.get("success"):
                st.info(
                    f"🌡 Actuel: **{weather['temperature_c']}°C** | "
                    f"💧 Humidité: **{weather['humidite_pct']}%** | "
                    f"💨 Vent: **{weather['vent_kmh']} km/h**"
                )

        submitted = st.form_submit_button("🔍 Générer la Prévision", use_container_width=True,
                                           type="primary")

    # ── Résultats ─────────────────────────────────────────────────────────────
    if submitted:
        if not model.is_trained():
            st.error("Le modèle n'est pas chargé. Vérifiez la configuration.")
            return

        with st.spinner("Analyse en cours..."):
            result = model.predict({
                "region":               region,
                "culture":              culture,
                "type_sol":             type_sol,
                "surface_ha":           surface,
                "pluviometrie_mm":      pluviometrie,
                "temperature_moyenne_c": temperature_moy,
                "irrigation":           irrigation,
                "fertilisation":        fertilisation,
            })

        _display_results(result, region, culture, type_sol, surface,
                          pluviometrie, temperature_moy, irrigation,
                          fertilisation, date_semis)

        # Sauvegarde historique
        _save_to_history(result, region, culture, type_sol, surface,
                          pluviometrie, temperature_moy, irrigation,
                          fertilisation, date_semis)


def _display_results(
    result, region, culture, type_sol, surface,
    pluviometrie, temperature_moy, irrigation,
    fertilisation, date_semis
) -> None:
    """Affiche les résultats de la prévision."""
    st.markdown("---")
    st.markdown('<div class="section-title">📈 Résultats de la Prévision</div>', unsafe_allow_html=True)

    rendement    = result["rendement_t_ha"]
    production   = result["production_total_t"]
    niveau_risque = result["niveau_risque"]
    score_risque  = result["score_risque_pct"]
    ci_low, ci_high = result["ci_low"], result["ci_high"]

    # Date de récolte estimée
    jours_maturation = {"Maïs": 95, "Sorgho": 120, "Mil": 105}.get(culture, 100)
    date_recolte = pd.Timestamp(date_semis) + pd.Timedelta(days=jours_maturation)

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Rendement estimé",
                             f"{rendement:.2f} t/ha",
                             f"IC [{ci_low} – {ci_high}]"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Production totale",
                             f"{production:.1f} t",
                             f"sur {surface} ha"), unsafe_allow_html=True)
    with c3:
        badge = risk_badge(niveau_risque)
        st.markdown(kpi_card("Niveau de risque",
                             f"{score_risque}%",
                             badge), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Récolte optimale",
                             date_recolte.strftime("%d %b %Y"),
                             f"Dans ~{jours_maturation} jours"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphiques ─────────────────────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig = go.Figure()
        scenarios = ["Pesimiste (-8%)", "Prévision", "Optimiste (+8%)"]
        vals      = [ci_low, rendement, ci_high]
        colors    = ["#EF5350", "#4CAF50", "#42A5F5"]

        fig.add_trace(go.Bar(
            x=scenarios, y=vals,
            marker_color=colors,
            text=[f"{v:.2f} t/ha" for v in vals],
            textposition="outside",
            width=0.45,
        ))
        fig.update_layout(
            title="Scénarios de rendement (t/ha)",
            yaxis_title="Rendement (t/ha)",
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#FAFAFA",
            font=dict(family="Inter, Segoe UI"),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_risque,
            title={"text": "Indice de risque (%)"},
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#EF5350" if score_risque > 60 else "#FFCA28" if score_risque > 35 else "#4CAF50"},
                "steps": [
                    {"range": [0, 35],  "color": "#E8F5E9"},
                    {"range": [35, 65], "color": "#FFF8E1"},
                    {"range": [65, 100],"color": "#FFEBEE"},
                ],
                "threshold": {
                    "line": {"color": "#B71C1C", "width": 3},
                    "thickness": 0.75,
                    "value": 70,
                },
            },
        ))
        fig2.update_layout(height=380, paper_bgcolor="#FAFAFA")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Recommandations ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">💡 Recommandations</div>', unsafe_allow_html=True)

    recos = _build_recommendations(rendement, pluviometrie, temperature_moy,
                                    irrigation, fertilisation, culture, niveau_risque)
    for reco in recos:
        alert_cls = "alert-danger" if reco["type"] == "danger" else \
                    "alert-warning" if reco["type"] == "warning" else "alert-success"
        st.markdown(
            f'<div class="{alert_cls}" style="margin-bottom:.75rem;">'
            f'<strong>{reco["titre"]}</strong><br>{reco["texte"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("#### Actions")
    cb1, cb2 = st.columns(2)

    export_row = {
        "region": region, "culture": culture, "type_sol": type_sol,
        "surface_ha": surface, "pluviometrie_mm": pluviometrie,
        "temperature_c": temperature_moy, "irrigation": irrigation,
        "fertilisation": fertilisation, "rendement_t_ha": rendement,
        "production_t": production, "risque": niveau_risque,
        "date_semis": str(date_semis),
        "date_recolte_estimee": date_recolte.strftime("%Y-%m-%d"),
    }
    csv_bytes = pd.DataFrame([export_row]).to_csv(index=False).encode("utf-8")

    with cb1:
        st.download_button(
            "⬇ Exporter en CSV",
            data=csv_bytes,
            file_name=f"prevision_{culture}_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with cb2:
        if st.button("➕ Nouvelle prévision", use_container_width=True):
            st.rerun()


def _build_recommendations(rendement, pluviometrie, temperature, irrigation,
                             fertilisation, culture, niveau_risque):
    """Génère un ensemble de recommandations contextuelles."""
    recos = []

    if pluviometrie < 500:
        recos.append({
            "type": "danger",
            "titre": "Déficit hydrique critique",
            "texte": f"La pluviométrie ({pluviometrie} mm) est insuffisante pour {culture}. "
                     "Envisagez l'irrigation d'urgence et des variétés résistantes à la sécheresse."
        })
    elif pluviometrie < 700:
        recos.append({
            "type": "warning",
            "titre": "Pluviométrie modérée",
            "texte": f"Pensez à optimiser la rétention d'eau du sol (paillis, labour minimal)."
        })

    if temperature > 33:
        recos.append({
            "type": "warning",
            "titre": "Stress thermique",
            "texte": f"Température élevée ({temperature}°C). Anticipez des semis matinaux "
                     "et protégez les jeunes pousses."
        })

    if fertilisation == "Aucune":
        recos.append({
            "type": "warning",
            "titre": "Fertilisation recommandée",
            "texte": "L'absence de fertilisation peut réduire le rendement de 18 à 25 %. "
                     "La fertilisation organique est accessible et durable."
        })

    if irrigation == "Aucun" and pluviometrie < 700:
        recos.append({
            "type": "warning",
            "titre": "Envisagez l'irrigation",
            "texte": "Avec une faible pluviométrie et sans irrigation, votre récolte est vulnérable."
        })

    if niveau_risque == "Faible":
        recos.append({
            "type": "success",
            "titre": "Conditions favorables",
            "texte": f"Les conditions sont bonnes pour {culture}. "
                     "Maintenez vos pratiques et préparez le stockage de la récolte."
        })

    return recos if recos else [{"type": "success",
                                  "titre": "Prévision stable",
                                  "texte": "Aucun risque majeur détecté. Suivez le calendrier cultural."}]


def _save_to_history(result, region, culture, type_sol, surface,
                      pluviometrie, temperature_moy, irrigation,
                      fertilisation, date_semis) -> None:
    """Sauvegarde la prévision dans la session Streamlit."""
    from datetime import datetime
    if "historique" not in st.session_state:
        st.session_state.historique = []

    record = {
        "date":             datetime.now().strftime("%Y-%m-%d %H:%M"),
        "region":           region,
        "culture":          culture,
        "type_sol":         type_sol,
        "surface_ha":       surface,
        "pluviometrie_mm":  pluviometrie,
        "temperature_c":    temperature_moy,
        "irrigation":       irrigation,
        "fertilisation":    fertilisation,
        "rendement_t_ha":   result["rendement_t_ha"],
        "production_t":     result["production_total_t"],
        "risque":           result["niveau_risque"],
        "score_risque_pct": result["score_risque_pct"],
    }
    st.session_state.historique.append(record)
