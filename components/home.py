"""
Page d'accueil - Présentation générale du système
"""

import streamlit as st
from config import REGIONS


def show_home_page():
    """Affiche la page d'accueil"""
    
    st.markdown("## Bienvenue sur le système de prévision agricole")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        Ce système utilise l'**intelligence artificielle** pour vous aider à prendre de meilleures 
        décisions agricoles concernant vos cultures de maïs et céréales locales.
        """)
        
        st.markdown("### Que pouvez-vous faire ?")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("""
            **Prévisions de rendement**
            - Estimation de la production (t/ha)
            - Basée sur vos données réelles
            
            **Analyse climatique**
            - Évaluation des risques
            - Recommandations adaptées
            """)
        
        with col_b:
            st.markdown("""
            **Calendrier optimal**
            - Meilleure période de récolte
            - Adaptation aux conditions locales
            
            **Historique**
            - Conservation des prévisions
            - Exportation des données
            """)
        
        with col_c:
            st.markdown("""
            **Générer des rapports**
            - Rapport des prévisions du mois 
            - Contrôler l'évolution des récoltes
            
            **Statistiques**
            - Analyses tendances
            - Comparaisons régionales
            """)
    
    with col2:
        st.markdown("### Régions couvertes")
        for region in REGIONS:
            st.success(f"✓ {region}")
        
        st.markdown("### Besoin d'aide ?")
        st.info("Consultez la section **À propos** pour plus d'informations.")
