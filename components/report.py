"""
Page de rapports - Génération de rapports d'activité et d'analyse
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import DatabaseManager
from utils.export import generate_historical_report


def show_report_page():
    """Affiche la page des rapports"""
    
    st.markdown("## Rapports d'Activité")
    
    db = DatabaseManager()
    df = db.get_all_predictions()
    
    if df.empty:
        st.info("ℹ️ Aucune donnée disponible pour générer un rapport.")
        return
    
    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Analyse Régionale", "Analyse par Culture"])
    
    with tab1:
        st.markdown("### Vue d'ensemble - Prévisions Globales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Prévisions Totales", len(df))
        
        with col2:
            st.metric("Rendement Moyen", f"{df['rendement_prevu'].mean():.2f} t/ha")
        
        with col3:
            st.metric("Production Totale", f"{df['production_totale'].sum():.2f} t")
        
        with col4:
            st.metric("Surface Total", f"{df['superficie'].sum():.2f} ha")
        
        # Graphique temporel
        if len(df) > 1:
            st.markdown("### Tendance Temporelle")
            
            fig = px.line(
                df.sort_values('created_at'),
                x='created_at',
                y='production_totale',
                title='Évolution de la Production Totale',
                labels={'created_at': 'Date', 'production_totale': 'Production (t)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Analyse par Région")
        
        # Statistiques régionales
        if 'region' in df.columns:
            regions_stats = df.groupby('region').agg({
                'rendement_prevu': 'mean',
                'production_totale': 'sum',
                'superficie': 'sum',
                'niveau_risque': 'mean'
            }).round(2)
            
            st.dataframe(regions_stats, use_container_width=True)
            
            # Graphiques régionaux
            col1, col2 = st.columns(2)
            
            with col1:
                fig_region_rendement = px.bar(
                    df.groupby('region')['rendement_prevu'].mean().reset_index(),
                    x='region',
                    y='rendement_prevu',
                    title='Rendement Moyen par Région',
                    labels={'rendement_prevu': 'Rendement (t/ha)', 'region': 'Région'}
                )
                st.plotly_chart(fig_region_rendement, use_container_width=True)
            
            with col2:
                fig_region_risque = px.bar(
                    df.groupby('region')['niveau_risque'].mean().reset_index(),
                    x='region',
                    y='niveau_risque',
                    title='Risque Moyen par Région',
                    labels={'niveau_risque': 'Risque (%)', 'region': 'Région'},
                    color='niveau_risque',
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig_region_risque, use_container_width=True)
    
    with tab3:
        st.markdown("### Analyse par Culture")
        
        # Statistiques par culture
        if 'culture' in df.columns:
            cultures_stats = df.groupby('culture').agg({
                'rendement_prevu': ['mean', 'min', 'max'],
                'production_totale': 'sum',
                'niveau_risque': 'mean'
            }).round(2)
            
            st.write(cultures_stats)
            
            # Graphiques par culture
            col1, col2 = st.columns(2)
            
            with col1:
                fig_culture_rendement = px.bar(
                    df.groupby('culture')['rendement_prevu'].mean().reset_index(),
                    x='culture',
                    y='rendement_prevu',
                    title='Rendement Moyen par Culture',
                    labels={'rendement_prevu': 'Rendement (t/ha)', 'culture': 'Culture'},
                    color='rendement_prevu',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_culture_rendement, use_container_width=True)
            
            with col2:
                fig_culture_box = px.box(
                    df,
                    x='culture',
                    y='rendement_prevu',
                    title='Distribution des Rendements',
                    labels={'rendement_prevu': 'Rendement (t/ha)', 'culture': 'Culture'}
                )
                st.plotly_chart(fig_culture_box, use_container_width=True)
    
    # Export du rapport complet
    st.markdown("### Télécharger le Rapport")
    
    report = generate_historical_report(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Rapport Texte Complet",
            data=report.encode('utf-8'),
            file_name="rapport_complet_activite.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # Export CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Données Brutes (CSV)",
            data=csv_data,
            file_name="donnees_brutes.csv",
            mime="text/csv",
            use_container_width=True
        )
