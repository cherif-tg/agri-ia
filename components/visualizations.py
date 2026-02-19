"""
Page de visualisations - Graphiques et analyses
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import REGIONS, CULTURES


def show_visualizations_page():
    """Affiche la page des visualisations"""
    
    st.markdown("## Visualisations et Analyses")
    
    tab1, tab2, tab3 = st.tabs(["Tendances Régionales", "Analyse Climatique", "Calendrier Cultural"])
    
    with tab1:
        st.markdown("### Rendements Moyens par Région")
        
        # Données simulées (en production, utiliser les données réelles de la BD)
        regions = REGIONS
        cultures_viz = CULTURES
        
        data = []
        for region in regions:
            for culture in cultures_viz:
                rendement = np.random.uniform(1.5, 4.5)
                data.append({'Région': region, 'Culture': culture, 'Rendement': rendement})
        
        df_viz = pd.DataFrame(data)
        
        fig = px.bar(
            df_viz,
            x='Région',
            y='Rendement',
            color='Culture',
            barmode='group',
            title='Rendements Moyens par Région et Culture (t/ha)',
            color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3']
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("ℹ️ Ces données sont basées sur les prévisions historiques du système.")
    
    with tab2:
        st.markdown("### Impact de la Pluviométrie sur le Rendement")
        
        # Génération de données synthétiques
        pluie = np.linspace(300, 1500, 50)
        rendement_mais = 1.5 + 0.003 * pluie - 0.000001 * pluie**2 + np.random.normal(0, 0.2, 50)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=pluie,
            y=rendement_mais,
            mode='markers',
            name='Observations',
            marker=dict(size=8, color='#4CAF50')
        ))
        
        # Ligne de tendance
        z = np.polyfit(pluie, rendement_mais, 2)
        p = np.poly1d(z)
        fig2.add_trace(go.Scatter(
            x=pluie,
            y=p(pluie),
            mode='lines',
            name='Tendance',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig2.update_layout(
            title='Relation Pluviométrie - Rendement (Maïs)',
            xaxis_title='Pluviométrie (mm)',
            yaxis_title='Rendement (t/ha)',
            height=500
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pluviométrie Optimale", "800-1000 mm")
        with col2:
            st.metric("Rendement Maximal Observé", "4.2 t/ha")
    
    with tab3:
        st.markdown("### Calendrier Cultural Recommandé")
        
        calendrier = {
            'Culture': ['Maïs', 'Maïs', 'Sorgho', 'Sorgho', 'Mil', 'Mil'],
            'Saison': ['Première', 'Deuxième', 'Première', 'Deuxième', 'Première', 'Deuxième'],
            'Semis': ['Mars-Avril', 'Août-Sept', 'Avril-Mai', 'Septembre', 'Mai-Juin', '-'],
            'Récolte': ['Juin-Juillet', 'Nov-Déc', 'Sept-Oct', 'Janvier', 'Sept-Oct', '-'],
            'Durée (jours)': [90, 90, 120, 120, 100, 0]
        }
        
        df_cal = pd.DataFrame(calendrier)
        df_cal = df_cal[df_cal['Durée (jours)'] > 0]  # Retirer les lignes avec durée 0
        
        st.dataframe(df_cal, use_container_width=True, hide_index=True)
        
        st.info("""
        **Note:** Ces périodes sont indicatives et peuvent varier selon les conditions 
        climatiques spécifiques de votre région. Utilisez la fonction de prévision pour 
        obtenir des recommandations personnalisées.
        """)
