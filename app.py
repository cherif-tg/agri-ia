"""
Application Principale - Système de Prévision Agricole IA
Point d'entrée Streamlit
"""

import streamlit as st
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# Configuration du logging
def setup_logging():
    """Configure le système de logging"""
    from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE
    
    # Créer le logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    
    # Handler fichier
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    return logger


# Initialiser le logging
logger = setup_logging()
logger.info("Application démarrée")

# Imports
from config import (
    PAGE_CONFIG,
    CUSTOM_CSS,
    REGIONS_COORDINATES,
    APP_VERSION
)
from utils.weather import get_real_time_weather
from components import (
    show_home_page,
    show_prediction_form,
    show_visualizations_page,
    show_history_page,
    show_report_page,
    show_about_page
)
from components.rag_analysis import show_rag_analysis_page
from components.chatbot_ui import show_chatbot_page


def init_session_state():
    """Initialise l'état de session Streamlit"""
    if 'last_prediction' not in st.session_state:
        st.session_state.last_prediction = None
    if 'weather_cache' not in st.session_state:
        st.session_state.weather_cache = {}


def main():
    """Fonction principale de l'application"""
    
    # Configuration de page
    st.set_page_config(**PAGE_CONFIG)
    
    # CSS personnalisé
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialisation session
    init_session_state()
    
    # Titre principal
    st.markdown('<div class="main-header">🌾 Système de Prévision Agricole - Togo</div>', 
                unsafe_allow_html=True)
    st.markdown("### Intelligence Artificielle pour l'agriculture durable")
    
    # Sidebar - Navigation
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Togo.svg/200px-Flag_of_Togo.svg.png",
            width=100
        )
        
        st.title("Navigation")
        page = st.radio(
            "Sélectionnez une section",
            ["Accueil", "Prévision", "📊 Analyse Batch (RAG)", "💬 Assistant IA", "Visualisations", "Historique", "Rapport", "À propos"]
        )
        
        st.markdown("---")
        
        st.info("""
        **Cultures supportées:**
        - Maïs
        - Sorgho
        - Mil
        
        **Régions couvertes:**
        - Maritime
        - Plateaux
        - Centrale
        - Kara
        - Savanes
        """)
        
        st.markdown("---")
        st.caption(f"Version {APP_VERSION} - 2026")
    
    # Router des pages
    try:
        if page == "Accueil":
            show_home_page()
        
        elif page == "Prévision":
            show_prediction_form()
        
        elif page == "📊 Analyse Batch (RAG)":
            show_rag_analysis_page()
        
        elif page == "💬 Assistant IA":
            show_chatbot_page()
        
        elif page == "Visualisations":
            show_visualizations_page()
        
        elif page == "Historique":
            show_history_page()
        
        elif page == "Rapport":
            show_report_page()
        
        elif page == "À propos":
            show_about_page()
    
    except Exception as e:
        logger.error(f"Erreur page: {str(e)}", exc_info=True)
        st.error(f"Une erreur est survenue: {str(e)}")
        st.info("Consultez les logs pour plus de détails.")
    
    # Footer
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.caption("🌾 Système de Prévision Agricole")
    
    with col_f2:
        st.caption("🇹🇬 Fait pour le Togo")
    
    with col_f3:
        st.caption("⚡ L'IA au service de l'agriculture")


if __name__ == "__main__":
    main()
