"""
modules/chatbot.py
==================
AgroBot – Chatbot alimenté par l'API Groq avec le modèle LLaMA 3.3-70B.
Conservation de l'historique de conversation dans la session Streamlit.
"""

from __future__ import annotations

from typing import List, Dict

import streamlit as st

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE, SYSTEM_PROMPT_CHATBOT


def render() -> None:
    """Affiche la page du chatbot AgroBot."""
    st.markdown('<div class="section-title">🤖 AgroBot – Assistant Agricole IA</div>', unsafe_allow_html=True)
    st.markdown(
        "Posez vos questions en français sur l'agronomie, les cultures togolaises, "
        "les conditions climatiques, la gestion des sols, ou l'interprétation de vos prévisions."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Vérification de la clé API
    if not GROQ_API_KEY:
        st.markdown("""
        <div class="alert-warning">
            <strong>🔑 Clé API Groq manquante</strong><br>
            Pour utiliser AgroBot, configurez votre clé API :<br>
            1. Créez un compte gratuit sur <a href="https://console.groq.com" target="_blank">console.groq.com</a><br>
            2. Copiez le fichier <code>.env.example</code> en <code>.env</code><br>
            3. Ajoutez votre clé : <code>GROQ_API_KEY=gsk_...</code><br>
            4. Relancez l'application.
        </div>""", unsafe_allow_html=True)

        # Mode démo sans clé
        st.markdown("---")
        st.info("Mode démonstration : les réponses ci-dessous sont des exemples statiques.")
        _show_demo_examples()
        return

    # Initialisation de l'historique
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Bouton reset
    col_title, col_reset = st.columns([5, 1])
    with col_reset:
        if st.button("🗑 Effacer", help="Effacer la conversation"):
            st.session_state.chat_messages = []
            st.rerun()

    # ── Affichage de la conversation ──────────────────────────────────────────
    _render_conversation(st.session_state.chat_messages)

    # ── Input utilisateur ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Suggestions rapides
    _render_quick_suggestions()

    user_input = st.chat_input("Posez votre question à AgroBot…")

    if user_input:
        _process_message(user_input)


def _render_conversation(messages: List[Dict]) -> None:
    """Affiche toutes les bulles de conversation."""
    if not messages:
        st.markdown("""
        <div class="card" style="text-align:center; padding:2rem; color:#757575;">
            <div style="font-size:2.5rem;">🌾</div>
            <h4>Bonjour ! Je suis AgroBot.</h4>
            <p>Je suis là pour vous aider avec vos questions agricoles.<br>
            Demandez-moi par exemple :<br>
            « Quels sont les besoins en eau du maïs ? »<br>
            « Comment améliorer la fertilité des sols argileux ? »</p>
        </div>""", unsafe_allow_html=True)
        return

    for msg in messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-name-user">Vous</div>'
                f'<div style="display:flex; justify-content:flex-end;">'
                f'<div class="chat-user">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            # Préserver les retours à la ligne du markdown dans la bulle
            content_html = msg["content"].replace("\n", "<br>")
            st.markdown(
                f'<div class="chat-name-bot">🌾 AgroBot</div>'
                f'<div class="chat-bot">{content_html}</div>',
                unsafe_allow_html=True,
            )


def _render_quick_suggestions() -> None:
    """Affiche des boutons de suggestions rapides."""
    suggestions = [
        "Quels sont les besoins en eau du maïs ?",
        "Comment préparer le sol pour le sorgho ?",
        "Quel engrais utiliser pour le mil dans la région Savanes ?",
        "Comment lutter contre les ravageurs du maïs ?",
    ]
    st.markdown("**Suggestions rapides :**")
    cols = st.columns(4)
    for i, sug in enumerate(suggestions):
        with cols[i]:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                _process_message(sug)


def _process_message(user_input: str) -> None:
    """Ajoute le message utilisateur, appelle l'API et affiche la réponse."""
    # Ajout message utilisateur
    st.session_state.chat_messages.append({"role": "user", "content": user_input})

    # Appel API Groq
    with st.spinner("AgroBot réfléchit…"):
        response = _call_groq(st.session_state.chat_messages)

    if response:
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    else:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "Désolé, une erreur s'est produite. Vérifiez votre connexion et la clé API.",
        })

    st.rerun()


def _call_groq(messages: List[Dict]) -> str | None:
    """Appelle l'API Groq et retourne la réponse textuelle."""
    try:
        from groq import Groq  # noqa: PLC0415
        client = Groq(api_key=GROQ_API_KEY)

        # Construction des messages avec le system prompt
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT_CHATBOT}]
        # Garde seulement les 20 derniers messages pour ne pas dépasser le contexte
        full_messages.extend(messages[-20:])

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=full_messages,
            max_tokens=GROQ_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
        )
        return response.choices[0].message.content

    except ImportError:
        st.error("Package `groq` non installé. Exécutez : `pip install groq`")
        return None
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur API Groq : {exc}")
        return None


def _show_demo_examples() -> None:
    """Affiche des exemples de conversations sans API."""
    examples = [
        {
            "q": "Quels sont les besoins en eau du maïs au Togo ?",
            "a": (
                "Le maïs a besoin de **800 à 1 000 mm** de pluie répartis sur son cycle de 90 à 100 jours. "
                "Au Togo, les meilleures conditions sont dans les régions Plateaux et Maritime. "
                "En saison sèche, une irrigation d'appoint de **25 à 30 mm/semaine** peut compenser un déficit pluviométrique."
            ),
        },
        {
            "q": "Comment améliorer la fertilité des sols sableux ?",
            "a": (
                "Pour les sols sableux du nord Togo (Savanes, Kara) :\n"
                "- Incorporez du **compost ou fumier** (5 à 10 t/ha) pour améliorer la rétention d'eau\n"
                "- Pratiquez l'**agroforesterie** avec des légumineuses (Acacia, Mucuna)\n"
                "- Utilisez le **paillage** pour réduire l'évaporation\n"
                "- Appliquez un engrais NPK 15-15-15 à la dose de 150 kg/ha"
            ),
        },
    ]

    for ex in examples:
        st.markdown(
            f'<div class="chat-name-user">Exemple de question</div>'
            f'<div style="display:flex; justify-content:flex-end;">'
            f'<div class="chat-user">{ex["q"]}</div></div>',
            unsafe_allow_html=True,
        )
        answer_html = ex["a"].replace("\n", "<br>")
        st.markdown(
            f'<div class="chat-name-bot">🌾 AgroBot (démo)</div>'
            f'<div class="chat-bot">{answer_html}</div>',
            unsafe_allow_html=True,
        )
