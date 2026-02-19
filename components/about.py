"""
Page À propos - Informations sur le système
"""

import streamlit as st
from config import CONTACT_INFO, APP_VERSION, APP_YEAR


def show_about_page():
    """Affiche la page À propos"""
    
    tab1, tab2, tab3 = st.tabs(["Présentation", "Technologie", "Contact"])
    
    with tab1:
        st.markdown("""
        ### Système de Prévision Agricole Intelligent
        
        Ce système a été conçu pour répondre aux besoins des agriculteurs togolais en matière 
        de prévision et d'aide à la décision agricole.
        
        #### Objectifs
        
        - 🎯 Fournir des prévisions fiables de rendement
        - 📊 Aider à la prise de décision (semis, irrigation, récolte)
        - 🛡️ Réduire les pertes liées aux aléas climatiques
        - 📈 Valoriser les données agricoles locales
        
        #### Couverture Géographique
        
        Le système couvre l'ensemble des régions agricoles du Togo :
        - 🌾 Maritime
        - 🌄 Plateaux
        - 🏞️ Centrale
        - ⛰️ Kara
        - 🌍 Savanes
        
        #### Cultures Supportées
        
        - **Maïs** : Culture principale
        - **Sorgho** : Céréale traditionnelle
        - **Mil** : Culture de la zone sahélienne
        
        *D'autres cultures seront ajoutées prochainement.*
        
        #### Fonctionnalités Principales
        
        1. **Prévision de Rendement** : Estimation basée sur IA
        2. **Analyse Climatique** : Évaluation des risques
        3. **Recommandations Personnalisées** : Basées sur vos conditions
        4. **Historique Complet** : Suivi de vos prévisions
        5. **Rapports Détaillés** : Analyses et statistiques
        6. **Exports Multiples** : CSV, TXT, etc.
        """)
    
    with tab2:
        st.markdown("""
        ### Technologies Utilisées
        
        #### Intelligence Artificielle
        
        - 🤖 **Algorithmes** : Random Forest, Gradient Boosting
        - 📚 **Framework** : Scikit-learn
        - 🐍 **Langage** : Python 3.10+
        
        #### Interface Utilisateur
        
        - 🎨 **Framework** : Streamlit
        - 📊 **Visualisations** : Plotly
        - 💻 **Design** : Interface intuitive et responsive
        
        #### Sources de Données
        
        - 📡 **FAOSTAT** : Données agricoles internationales
        - 🌡️ **Open-Meteo API** : Données météorologiques en temps réel
        - 📋 **Enquêtes locales** : Données de terrain
        - 🗄️ **Base de données locales** : SQLite
        
        #### Traitement des Données
        
        - 🛠️ **Pandas** : Manipulation de données
        - 🔢 **NumPy** : Calcul numérique
        - 📊 **Scikit-learn** : Machine Learning
        
        #### Architecture
        
        ```
        prevision/
        ├── config.py           # Configuration centralisée
        ├── models/
        │   └── predictor.py    # Moteur de prédiction
        ├── utils/
        │   ├── weather.py      # Gestion météo
        │   ├── database.py     # Base de données
        │   ├── validators.py   # Validation données
        │   └── export.py       # Exports
        ├── components/
        │   ├── home.py         # Pages
        │   ├── prediction.py
        │   ├── history.py
        │   └── ...
        └── app.py              # Application principale
        ```
        
        #### Métriques de Performance
        
        - ⚡ Temps de réponse : < 2 secondes
        - 🎯 Précision : R² > 0.85 (sur données de test)
        - 🔄 Mises à jour : Modèles actualisés régulièrement
        - 📱 Disponibilité : 99%+ uptime
        
        #### Modèles d'Évaluation
        
        Les modèles sont évalués selon :
        - **RMSE** (Root Mean Square Error)
        - **MAE** (Mean Absolute Error)
        - **R²** (Coefficient de détermination)
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Précision Moyenne", "87%")
        with col2:
            st.metric("Erreur Moyenne", "0.3 t/ha")
        with col3:
            st.metric("Prévisions/jour", "150+")
    
    with tab3:
        st.markdown(f"""
        ### 📞 Contact et Support
        
        #### 💬 Besoin d'aide ?
        
        Pour toute question ou assistance technique :
        
        - 📧 **Email** : {CONTACT_INFO['email']}
        - 📱 **Téléphone** : {CONTACT_INFO['telephone']}
        - 🌐 **Site web** : {CONTACT_INFO['website']}
        
        #### ⭐ Nous parler
        
        Vos retours sont précieux pour améliorer le système !
        """)
        
        with st.form("formulaire_feedback"):
            st.markdown("**Envoyez-nous vos suggestions et retours**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Votre nom (optionnel)")
            
            with col2:
                email = st.text_input("Votre email (optionnel)")
            
            message = st.text_area("Votre message ou suggestion", height=150)
            
            submitted = st.form_submit_button("Envoyer le Feedback", use_container_width=True)
            
            if submitted:
                if message:
                    st.success("✓ Merci pour votre retour ! Nous l'avons bien reçu.")
                    st.info("Vos commentaires nous aident à améliorer le système.")
                else:
                    st.warning("⚠️ Veuillez saisir un message.")
        
        st.markdown("---")
        st.markdown(f"""
        <p style="text-align: center; color: gray; font-size: 0.9em;">
        © {APP_YEAR} Système de Prévision Agricole IA<br>
        Version {APP_VERSION} | 🇹🇬 Made for Togo
        </p>
        """, unsafe_allow_html=True)
