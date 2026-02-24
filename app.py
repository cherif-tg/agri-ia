"""
app.py
======
AgroPredict Togo – Point d'entrée principal de l'application Streamlit.

Architecture :
    app.py              ← Ce fichier (entry point)
    config.py           ← Configuration centralisée
    core/
        ml_model.py     ← Modèle ML (XGBoost + LightGBM + Optuna)
        weather.py      ← API météo temps réel (Open-Meteo)
        data_processor.py ← Utilitaires de traitement de données
    modules/
        styles.py       ← CSS moderne
        home.py         ← Accueil
        prediction.py   ← Prévision de rendement
        visualizations.py ← Graphiques & analyses
        history.py      ← Historique des prévisions
        rag.py          ← RAG : upload CSV/Excel/PDF
        chatbot.py      ← AgroBot (Groq / LLaMA 3.3-70B)
        report.py       ← Rapports & performance modèle
    tests/              ← Tests pytest

Lancement :
    streamlit run app.py
"""

import logging
import streamlit as st

# ── Configuration de la page (DOIT être en premier) ──────────────────────────
st.set_page_config(
    page_title="AgroPredict Togo",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help":     "mailto:tengacherif@gmail.com",
        "Report a bug": "mailto:tengacherif@gmail.com",
        "About":        "AgroPredict Togo v2.0 – IA agricole pour le Togo",
    },
)

# ── Imports internes ──────────────────────────────────────────────────────────
from config import (
    APP_NAME, APP_VERSION, MODEL_PATH, DATA_CSV_PATH,
    GROQ_API_KEY,
)
from core.ml_model import get_or_train_model
from modules.styles import inject_css

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Initialisation de la session
# ─────────────────────────────────────────────────────────────────────────────

def _init_session() -> None:
    """Initialise les variables de session Streamlit."""
    defaults = {
        "historique":     [],
        "chat_messages":  [],
        "current_page":   " Accueil",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# Chargement du modèle (mis en cache)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Chargement du modèle IA…")
def _load_model():
    """Charge ou entraîne le modèle ML et le met en cache."""
    return get_or_train_model(MODEL_PATH, DATA_CSV_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────────────────────

def _render_sidebar() -> str:
    """Affiche la barre latérale et retourne la page sélectionnée."""
    with st.sidebar:
        # Logo / titre
        st.markdown(f"""
        <div style="text-align:center; padding:1rem 0 .5rem;">
            <div style="font-size:3rem;">🌾</div>
            <h2 style="color:#fff; margin:0; font-size:1.3rem; font-weight:700;">
                {APP_NAME}
            </h2>
            <p style="color:rgba(255,255,255,.6); font-size:.8rem; margin:.2rem 0 0;">
                v{APP_VERSION} – IA agricole
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,.2);'>", unsafe_allow_html=True)

        # Navigation
        pages = [
            " Accueil",
            " Prévision",
            " Visualisations",
            " Analyse de fichiers",
            " AgroBot",
            " Historique",
            " Rapports",
            "ℹ À propos",
        ]

        page = st.radio(
            "Navigation",
            pages,
            label_visibility="collapsed",
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,.2);'>", unsafe_allow_html=True)

        # Statut API
        groq_status = "✅ Configurée" if GROQ_API_KEY else "❌ Non configurée"
        st.markdown(f"""
        <div style="font-size:.78rem; color:rgba(255,255,255,.7); line-height:1.8;">
            <div><strong style="color:#fff;"> API Groq :</strong> {groq_status}</div>
            <div><strong style="color:#fff;">🌦 Météo :</strong> Open-Meteo (gratuit)</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,.2);'>", unsafe_allow_html=True)
        st.caption("© 2026 AgroPredict Togo")

    return page


# ─────────────────────────────────────────────────────────────────────────────
# Header global
# ─────────────────────────────────────────────────────────────────────────────

_PAGE_SUBTITLES = {
    " Accueil":            "Tableau de bord principal",
    " Prévision":          "Prévision personnalisée de rendement",
    " Visualisations":     "Analyse des données et tendances",
    " Analyse de fichiers": "Import et analyse de vos données (RAG)",
    " AgroBot":            "Assistant IA agricole – LLaMA 3.3-70B",
    " Historique":         "Historique de vos prévisions",
    " Rapports":           "Rapports et performance du modèle",
    "ℹ À propos":           "Technologies et informations",
}

def _render_header(page: str) -> None:
    """Affiche le header de la page courante."""
    subtitle = _PAGE_SUBTITLES.get(page, "")
    st.markdown(f"""
    <div class="agro-header">
        <h1>🌾 {APP_NAME}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page À propos
# ─────────────────────────────────────────────────────────────────────────────

def _page_about() -> None:
    tab1, tab2, tab3 = st.tabs(["Présentation", "Technologies", "Contact"])

    with tab1:
        st.markdown("""
        <div class="card">
            <h3 style="color:#1B5E20;">AgroPredict Togo v2.0</h3>
            <p>
                Plateforme d'intelligence artificielle dédiée à l'agriculture togolaise.
                Conçue pour aider les agriculteurs, les techniciens de terrain et les décideurs
                à obtenir des <strong>prévisions fiables de rendement</strong> et à prendre de meilleures
                décisions agricoles.
            </p>
            <ul>
                <li>Couverture : 5 régions du Togo (Maritime, Plateaux, Centrale, Kara, Savanes)</li>
                <li>Cultures : Maïs, Sorgho, Mil</li>
                <li>Précision : R² &gt; 0.88 sur données de validation croisée</li>
                <li>Météo : données temps réel Open-Meteo (gratuit, sans clé)</li>
                <li>Chatbot : LLaMA 3.3-70B via API Groq</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        cols = st.columns(3)
        techs = [
            (" Machine Learning", "XGBoost + LightGBM\nOptimisation Optuna\nValidation croisée 5-fold"),
            (" Visualisation", "Plotly Express & Graph Objects\nCarte interaktive\nCharts interactifs"),
            (" Framework", "Streamlit 1.32+\nPython 3.10+\nArchitecture modulaire"),
            ("🌦 Météo", "Open-Meteo API (gratuit)\nDonnées temps réel + historiques\nFallback automatique"),
            (" Chatbot", "Groq API\nLLaMA 3.3-70B Versatile\nHistorique de conversation"),
            (" RAG", "CSV / Excel / PDF\nDétection auto des colonnes\nPrévisions batch"),
        ]
        for i, (title, desc) in enumerate(techs):
            with cols[i % 3]:
                desc_html = desc.replace("\n", "<br>")
                st.markdown(f"""
                <div class="card card-green">
                    <strong style="color:#1B5E20;">{title}</strong>
                    <p style="font-size:.85rem; color:#616161; margin-top:.5rem;">{desc_html}</p>
                </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="card">
            <h4>Contact & Support</h4>
            <ul>
                <li> Email : <a href="mailto:tengacherif@gmail.com">tengacherif@gmail.com</a></li>
                <li> Tél : +228 71518061</li>
            </ul>
        </div>""", unsafe_allow_html=True)

        with st.form("feedback_form"):
            st.markdown("**Envoyer un feedback**")
            nom     = st.text_input("Nom (optionnel)")
            message = st.text_area("Message", height=120)
            if st.form_submit_button("Envoyer", type="primary"):
                if message.strip():
                    st.success("Merci pour votre retour !")
                else:
                    st.warning("Veuillez saisir un message.")


# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée principal
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Fonction principale – charge le modèle et route vers la bonne page."""
    # CSS global
    inject_css()

    # Session
    _init_session()

    # Modèle ML
    model = _load_model()

    # Sidebar + navigation
    page = _render_sidebar()

    # Header
    _render_header(page)

    # Routing
    if page == " Accueil":
        from modules.home import render
        render()

    elif page == " Prévision":
        from modules.prediction import render
        render(model)

    elif page == " Visualisations":
        from modules.visualizations import render
        render()

    elif page == " Analyse de fichiers":
        from modules.rag import render
        render(model)

    elif page == " AgroBot":
        from modules.chatbot import render
        render()

    elif page == " Historique":
        from modules.history import render
        render()

    elif page == " Rapports":
        from modules.report import render
        render(model)

    elif page == "ℹ À propos":
        _page_about()


if __name__ == "__main__":
    main()
