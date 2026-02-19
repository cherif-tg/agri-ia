"""
Page d'historique - Gestion et affichage des prévisions passées
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import DatabaseManager
from utils.export import export_predictions_to_csv, generate_historical_report


def show_history_page():
    """Affiche la page d'historique"""
    
    st.markdown("## Historique des Prévisions")
    
    db = DatabaseManager()
    df_historique = db.get_all_predictions()
    
    if df_historique.empty:
        st.info("ℹ️ Aucune prévision enregistrée pour le moment. Commencez par créer une nouvelle prévision !")
        return
    
    st.success(f"✓ {len(df_historique)} prévision(s) enregistrée(s)")
    
    # Statistiques
    stats = db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prévisions", stats.get('total_predictions', 0))
    
    with col2:
        st.metric("Rendement Moyen", f"{stats.get('average_yield', 0):.2f} t/ha")
    
    with col3:
        st.metric("Prod. Totale", f"{stats.get('total_production', 0):.2f} t")
    
    with col4:
        st.metric("Risque Moyen", f"{stats.get('average_risk', 0):.1f}%")
    
    # Affichage tableau
    st.markdown("### Détail des Prévisions")
    
    # Colonnes à afficher
    colonnes_affichage = [
        'date_creation', 'region', 'culture', 'superficie',
        'rendement_prevu', 'production_totale', 'risque_niveau', 'date_recolte'
    ]
    
    df_display = df_historique[[col for col in colonnes_affichage if col in df_historique.columns]].copy()
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Graphiques d'évolution
    if len(df_historique) > 1:
        st.markdown("### Évolution des Rendements")
        
        fig = px.line(
            df_historique.sort_values('created_at'),
            x='date_creation',
            y='rendement_prevu',
            color='culture',
            markers=True,
            title='Évolution des Rendements Prévus'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Graphiques par culture
    if 'culture' in df_historique.columns:
        st.markdown("### Distribution par Culture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_culture = px.pie(
                df_historique,
                names='culture',
                title='Nombre de prévisions par culture',
                color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3']
            )
            st.plotly_chart(fig_culture, use_container_width=True)
        
        with col2:
            fig_rendement_culture = px.box(
                df_historique,
                x='culture',
                y='rendement_prevu',
                title='Distribution des rendements par culture'
            )
            st.plotly_chart(fig_rendement_culture, use_container_width=True)
    
    # Actions d'export
    st.markdown("### Actions")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        csv_all = export_predictions_to_csv(df_historique)
        st.download_button(
            label="📥 Historique Complet (CSV)",
            data=csv_all,
            file_name=f"historique_complet.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_a2:
        report = generate_historical_report(df_historique)
        st.download_button(
            label="📄 Rapport d'Activité",
            data=report.encode('utf-8'),
            file_name="rapport_activite.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_a3:
        if st.button("🗑️ Effacer l'Historique", use_container_width=True):
            if st.confirm("Êtes-vous sûr ? Cette action est irréversible."):
                db.delete_all_predictions()
                st.success("Historique supprimé")
                st.rerun()
