"""
modules/styles.py
==================
Feuille de style CSS globale pour l'application AgroPredict.
Design épuré, moderne, adapté à une application agri-data professionnelle.
"""

GLOBAL_CSS = """
<style>
/* ── Reset & variables ────────────────────────────────────────────────────── */
:root {
    --green-50:  #F1F8E9;
    --green-100: #DCEDC8;
    --green-200: #C5E1A5;
    --green-500: #4CAF50;
    --green-700: #388E3C;
    --green-900: #1B5E20;
    --amber-400: #FFCA28;
    --amber-700: #F57F17;
    --red-400:   #EF5350;
    --red-700:   #C62828;
    --gray-50:   #FAFAFA;
    --gray-100:  #F5F5F5;
    --gray-200:  #EEEEEE;
    --gray-700:  #616161;
    --gray-900:  #212121;
    --radius:    12px;
    --shadow:    0 2px 12px rgba(0,0,0,.08);
    --shadow-md: 0 4px 24px rgba(0,0,0,.14);
}

/* ── Layout & Police ──────────────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    background: var(--gray-50) !important;
    color: var(--gray-900) !important;
}

/* ── Header principal ─────────────────────────────────────────────────────── */
.agro-header {
    background: linear-gradient(135deg, var(--green-900) 0%, var(--green-700) 60%, var(--green-500) 100%);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: var(--shadow-md);
}
.agro-header h1 {
    color: #fff;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.agro-header p {
    color: rgba(255,255,255,.85);
    font-size: 1rem;
    margin: .4rem 0 0;
}

/* ── Cards ────────────────────────────────────────────────────────────────── */
.card {
    background: #fff;
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
    border: 1px solid var(--gray-200);
}
.card-green {
    border-left: 4px solid var(--green-500);
}
.card-amber {
    border-left: 4px solid var(--amber-400);
}
.card-red {
    border-left: 4px solid var(--red-400);
}

/* ── KPI metrics ──────────────────────────────────────────────────────────── */
.kpi-box {
    background: #fff;
    border-radius: var(--radius);
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-200);
    transition: box-shadow .2s;
}
.kpi-box:hover { box-shadow: var(--shadow-md); }
.kpi-label {
    font-size: .78rem;
    color: var(--gray-700);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: .3rem;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--green-900);
    line-height: 1;
}
.kpi-sub {
    font-size: .8rem;
    color: var(--gray-700);
    margin-top: .3rem;
}

/* ── Badges de risque ─────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: .25rem .75rem;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .3px;
}
.badge-low    { background: #E8F5E9; color: var(--green-700); }
.badge-medium { background: #FFF8E1; color: var(--amber-700); }
.badge-high   { background: #FFEBEE; color: var(--red-700); }

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--green-900) !important;
    color: #fff !important;
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: .6rem .8rem;
    border-radius: 8px;
    transition: background .15s;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.12);
}

/* ── Section title ────────────────────────────────────────────────────────── */
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--green-900);
    margin-bottom: .25rem;
    padding-bottom: .4rem;
    border-bottom: 2px solid var(--green-100);
}

/* ── Alert boxes ──────────────────────────────────────────────────────────── */
.alert-success {
    background: #E8F5E9;
    border-left: 4px solid var(--green-500);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: var(--green-900);
}
.alert-warning {
    background: #FFF8E1;
    border-left: 4px solid var(--amber-400);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: #5D4037;
}
.alert-danger {
    background: #FFEBEE;
    border-left: 4px solid var(--red-400);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: var(--red-700);
}

/* ── Chatbot bubbles ──────────────────────────────────────────────────────── */
.chat-user {
    background: var(--green-100);
    border-radius: 18px 18px 4px 18px;
    padding: .75rem 1rem;
    margin: .5rem 0;
    max-width: 80%;
    margin-left: auto;
    color: var(--gray-900);
    font-size: .93rem;
}
.chat-bot {
    background: #fff;
    border: 1px solid var(--gray-200);
    border-radius: 18px 18px 18px 4px;
    padding: .75rem 1rem;
    margin: .5rem 0;
    max-width: 85%;
    color: var(--gray-900);
    font-size: .93rem;
    box-shadow: var(--shadow);
}
.chat-name-user { font-size: .72rem; color: var(--gray-700); text-align: right; margin-bottom: .15rem; }
.chat-name-bot  { font-size: .72rem; color: var(--gray-700); margin-bottom: .15rem; }

/* ── Progress bar ─────────────────────────────────────────────────────────── */
.progress-bar-wrap { background: var(--gray-200); border-radius: 999px; height: 10px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 999px; transition: width .4s ease; }
.pb-green  { background: var(--green-500); }
.pb-amber  { background: var(--amber-400); }
.pb-red    { background: var(--red-400); }

/* ── Streamlit overrides ───────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: opacity .15s !important;
}
.stButton > button:hover { opacity: .88; }

/* Hide default streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""


def inject_css() -> None:
    """Injecte le CSS global dans l'application Streamlit."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "") -> str:
    """Génère le HTML d'une carte KPI."""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>"""


def risk_badge(niveau: str) -> str:
    """Retourne un badge HTML coloré selon le niveau de risque."""
    cls = {"Faible": "badge-low", "Modéré": "badge-medium", "Élevé": "badge-high"}.get(niveau, "badge-low")
    return f'<span class="badge {cls}">{niveau}</span>'
