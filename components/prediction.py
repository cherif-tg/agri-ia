"""
Page de prévision - Formulaire et résultats de prévision
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from typing import Optional

from config import (
    REGIONS,
    CULTURES,
    TYPES_SOL,
    SYSTEMES_IRRIGATION,
    TYPES_FERTILISATION
)
from utils.weather import get_real_time_weather
from utils.validators import validate_all_inputs
from utils.export import export_prediction_to_csv, generate_simple_report
from models.predictor import generate_prediction
from utils.database import DatabaseManager


def show_prediction_form():
    """Affiche le formulaire de prévision"""
    
    st.markdown("## Nouvelle Prévision Agricole")
    
    with st.form("formulaire_prevision"):
        st.markdown("### Informations sur votre exploitation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            region = st.selectbox(
                "Région agricole",
                REGIONS,
                help="Sélectionnez votre région"
            )
            
            culture = st.selectbox(
                "Type de culture",
                CULTURES,
                help="Culture à analyser"
            )
            
            superficie = st.number_input(
                "Superficie cultivée (ha)",
                min_value=0.1,
                max_value=1000.0,
                value=5.0,
                step=0.5,
                help="Surface de votre exploitation"
            )
        
        with col2:
            date_semis = st.date_input(
                "Date de semis",
                value=date.today(),
                help="Date de plantation"
            )
            
            type_sol = st.selectbox(
                "Type de sol",
                TYPES_SOL,
                help="Nature du sol de votre parcelle"
            )
            
            use_real_weather = st.checkbox(
                "Utiliser les données météo en temps réel",
                value=True,
                help="Récupère automatiquement la météo actuelle"
            )
        
        with col3:
            if use_real_weather:
                with st.spinner(f"...Récupération météo pour {region}..."):
                    weather_data = get_real_time_weather(region)
                
                if weather_data["success"]:
                    st.success("Données météo récupérées ✓")
                    
                    temperature_moy = st.number_input(
                        "Température moyenne (°C) - Temps réel",
                        min_value=15.0,
                        max_value=45.0,
                        value=float(weather_data.get("temperature_moyenne", 27)),
                        step=0.5,
                        help=f"Température actuelle: {weather_data.get('temperature_actuelle')}°C"
                    )
                    
                    pluviometrie = st.number_input(
                        "Pluviométrie cumulée (mm) - Temps réel",
                        min_value=0,
                        max_value=3000,
                        value=int(weather_data.get("precipitation_cumul", 800)),
                        step=50,
                        help="Cumul sur 7 jours depuis l'API"
                    )
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.caption(f"Humidité: {weather_data.get('humidite')}%")
                    with col_info2:
                        st.caption(f"Vent: {weather_data.get('vitesse_vent')} km/h")
                else:
                    st.warning("⚠️ Erreur de connexion, valeurs par défaut")
                    temperature_moy = st.number_input(
                        "Température moyenne (°C)",
                        min_value=15.0,
                        max_value=45.0,
                        value=27.0,
                        step=0.5
                    )
                    pluviometrie = st.number_input(
                        "Pluviométrie cumulée (mm)",
                        min_value=0,
                        max_value=3000,
                        value=800,
                        step=50
                    )
            else:
                temperature_moy = st.number_input(
                    "Température moyenne (°C)",
                    min_value=15.0,
                    max_value=45.0,
                    value=27.0,
                    step=0.5,
                    help="Température moyenne de la saison"
                )
                pluviometrie = st.number_input(
                    "Pluviométrie cumulée (mm)",
                    min_value=0,
                    max_value=3000,
                    value=800,
                    step=50,
                    help="Précipitations totales depuis le semis"
                )
            
            irrigation = st.selectbox(
                "Système d'irrigation",
                SYSTEMES_IRRIGATION,
                help="Type d'irrigation utilisé"
            )
            
            fertilisation = st.selectbox(
                "Type de fertilisation",
                TYPES_FERTILISATION,
                help="Mode de fertilisation"
            )
        
        submitted = st.form_submit_button("Générer la Prévision", use_container_width=True)
    
    if submitted:
        # Validation
        is_valid, error_msg = validate_all_inputs(
            region, culture, superficie, temperature_moy, pluviometrie,
            type_sol, irrigation, fertilisation
        )
        
        if not is_valid:
            st.error(f"Erreur de validation: {error_msg}")
            return
        
        # Génération de prévision
        try:
            with st.spinner("...Analyse en cours..."):
                prediction = generate_prediction(
                    region=region,
                    culture=culture,
                    superficie=superficie,
                    date_semis=date_semis,
                    type_sol=type_sol,
                    temperature_moy=temperature_moy,
                    pluviometrie=pluviometrie,
                    irrigation=irrigation,
                    fertilisation=fertilisation
                )
            
            st.session_state.last_prediction = prediction
            show_prediction_results(prediction)
            
            # Sauvegarde en BD
            db = DatabaseManager()
            db.save_prediction(prediction)
            
        except FileNotFoundError as e:
            st.error(f"❌ {str(e)}")
            st.info("Veuillez placer le fichier modèle à: `models/modele_rendement_agricole.pkl`")
        except Exception as e:
            st.error(f"Erreur lors de la prévision: {str(e)}")


def show_prediction_results(prediction: dict):
    """Affiche les résultats d'une prévision"""
    
    st.success("Prévision générée avec succès ! ✓")
    
    st.markdown("### Résultats de la Prévision")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Rendement Estimé",
            value=f"{prediction['rendement']:.2f} t/ha",
            delta=f"+{((prediction['rendement']/prediction['rendement_base'])-1)*100:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Production Totale",
            value=f"{prediction['production']:.2f} t",
            delta=f"{prediction.get('superficie', 1)} ha"
        )
    
    with col3:
        risque_emoji = {
            "Faible": "🟢",
            "Moyen": "🟡",
            "Élevé": "🔴"
        }
        emoji = risque_emoji.get(prediction['risque'], "❓")
        st.metric(
            label="Niveau de Risque",
            value=f"{prediction['risque']} ({prediction['niveau_risque']}%)",
            delta=emoji
        )
    
    with col4:
        st.metric(
            label="Récolte Optimale",
            value=prediction['date_recolte'],
            delta="Date estimée"
        )
    
    # Graphiques analytiques
    st.markdown("### Analyse Détaillée")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Graphique comparatif rendement
        fig1 = go.Figure()
        categories = ['Rendement\nPrévu', 'Rendement\nBase', 'Rendement\nOptimal']
        valeurs = [
            prediction['rendement'],
            prediction['rendement_base'],
            prediction['rendement_base'] * 1.3
        ]
        couleurs = ['#4CAF50', '#FF9800', '#2196F3']
        
        fig1.add_trace(go.Bar(
            x=categories,
            y=valeurs,
            marker_color=couleurs,
            text=[f'{v:.2f} t/ha' for v in valeurs],
            textposition='outside'
        ))
        
        fig1.update_layout(
            title="Comparaison des Rendements",
            yaxis_title="Rendement (t/ha)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_g2:
        # Jauge de risque
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=prediction['niveau_risque'],
            title={'text': "Indice de Risque (%)"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred" if prediction['niveau_risque'] > 60 else "orange" if prediction['niveau_risque'] > 30 else "green"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 60], 'color': "lightyellow"},
                    {'range': [60, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Recommandations
    st.markdown("### Recommandations")
    
    if prediction['niveau_risque'] > 60:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.warning(f"""
        **Attention - Risque {prediction['risque']}**
        
        - ⚠️ Surveillez étroitement l'évolution climatique
        - 💧 Envisagez un système d'irrigation complémentaire
        - 🛡️ Planifiez des mesures préventives
        - 👨‍🌾 Consultez un agronome si possible
        """)
    else:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success(f"""
        **Conditions Favorables - Risque {prediction['risque']}**
        
        - ✓ Les conditions sont bonnes pour votre culture
        - 📋 Maintenez vos pratiques actuelles
        - 📅 Suivez le calendrier de récolte recommandé
        - 🏭 Préparez le stockage pour la récolte
        """)
    
    # Boutons d'action
    st.markdown("### Actions")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    
    with col_b1:
        # Export CSV
        csv = export_prediction_to_csv(prediction)
        st.download_button(
            label="📥 Exporter CSV",
            data=csv,
            file_name=f"prevision_{prediction['culture']}_{prediction['date'].split()[0]}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_b2:
        # Rapport texte
        report = generate_simple_report(prediction)
        st.download_button(
            label="📄 Rapport Texte",
            data=report.encode('utf-8'),
            file_name=f"rapport_{prediction['culture']}_{prediction['date'].split()[0]}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_b3:
        if st.button("🔄 Nouvelle Prévision", use_container_width=True):
            st.rerun()
    
    with col_b4:
        st.caption("")  # Spacer
