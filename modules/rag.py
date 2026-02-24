"""
modules/rag.py
==============
Module RAG (Retrieval-Augmented Generation) :
Upload de fichiers CSV / Excel / PDF → Analyse, prévisions et visualisations.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from config import GROQ_API_KEY, GROQ_MODEL, CULTURES, REGIONS
from core.data_processor import (
    detect_columns,
    get_stats_summary,
    load_file,
    validate_and_clean,
    REQUIRED_COLUMNS,
)


def render(model) -> None:
    """Affiche la page d'analyse de fichiers (RAG)."""
    st.markdown('<div class="section-title">📂 Analyse de Fichiers (RAG)</div>', unsafe_allow_html=True)
    st.markdown(
        "Importez vos propres données agricoles (CSV, Excel, PDF). "
        "Le système détecte automatiquement les colonnes, génère des prévisions et produit des visualisations."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Upload ────────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Glissez-déposez votre fichier ici",
        type=["csv", "xlsx", "xls", "pdf"],
        accept_multiple_files=False,
        help="Formats acceptés : CSV, Excel (.xlsx / .xls), PDF",
    )

    if uploaded is None:
        _show_help()
        return

    # Chargement
    with st.spinner(f"Chargement de « {uploaded.name} »…"):
        df, msg = load_file(uploaded)

    st.markdown(f'<div class="alert-success">{msg}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cas PDF : analyse textuelle ───────────────────────────────────────────
    if df is None:
        _handle_pdf(msg)
        return

    # ── Cas CSV / Excel ───────────────────────────────────────────────────────
    _handle_tabular(df, model, uploaded.name)


# ─── PDF ────────────────────────────────────────────────────────────────────────

def _handle_pdf(text: str) -> None:
    """Analyse un PDF via Groq et affiche une synthèse."""
    st.subheader("📄 Contenu extrait du PDF")

    with st.expander("Voir le texte brut extrait", expanded=False):
        st.text(text[:4000] + ("…" if len(text) > 4000 else ""))

    if not text or "Erreur" in text[:50]:
        st.warning("Impossible d'extraire le texte de ce PDF.")
        return

    if not GROQ_API_KEY:
        st.warning("Clé GROQ_API_KEY non configurée. Ajoutez-la dans votre fichier `.env` pour l'analyse IA.")
        return

    if st.button("🤖 Analyser ce document avec l'IA", use_container_width=True):
        with st.spinner("Analyse IA en cours…"):
            analysis = _groq_analyze_pdf(text)
        if analysis:
            st.markdown("#### Synthèse IA")
            st.markdown(
                f'<div class="card card-green" style="white-space:pre-wrap;">{analysis}</div>',
                unsafe_allow_html=True,
            )


def _groq_analyze_pdf(text: str) -> Optional[str]:
    """Appelle Groq pour analyser le contenu d'un document PDF."""
    try:
        from groq import Groq  # noqa: PLC0415
        client = Groq(api_key=GROQ_API_KEY)
        excerpt = text[:6000]
        prompt  = (
            "Tu es un expert en agronomie africaine. Voici le contenu d'un document agricole :\n\n"
            f"{excerpt}\n\n"
            "Fais une synthèse structurée (max 400 mots) en identifiant :\n"
            "1. Le sujet principal du document\n"
            "2. Les données quantitatives clés (rendements, surfaces, productions…)\n"
            "3. Les régions / cultures mentionnées\n"
            "4. Les recommandations ou conclusions importantes\n"
            "Réponds en français, de façon claire et organisée."
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur Groq : {exc}")
        return None


# ─── Tabulaire (CSV / Excel) ──────────────────────────────────────────────────

def _handle_tabular(df: pd.DataFrame, model, filename: str) -> None:
    """Traite un fichier CSV ou Excel."""

    # 1. Aperçu
    with st.expander("👁 Aperçu du fichier", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"{len(df)} lignes × {len(df.columns)} colonnes")

    st.markdown("---")

    # 2. Détection automatique des colonnes
    st.markdown("#### 🔍 Détection des colonnes")
    col_mapping = detect_columns(df)

    st.info(
        "Le système a tenté de détecter automatiquement les colonnes correspondant au modèle. "
        "Corrigez si nécessaire."
    )

    # Interface pour corriger le mapping
    available_cols = ["(aucune)"] + df.columns.tolist()
    corrected_mapping: dict = {}

    with st.form("col_mapping_form"):
        cols_ui = st.columns(3)
        for i, (std_col, display_name) in enumerate(REQUIRED_COLUMNS.items()):
            detected = col_mapping.get(std_col)
            default_idx = (available_cols.index(detected)
                           if detected and detected in available_cols else 0)
            with cols_ui[i % 3]:
                selected = st.selectbox(
                    f"{display_name}",
                    options=available_cols,
                    index=default_idx,
                    key=f"map_{std_col}",
                )
                corrected_mapping[std_col] = selected if selected != "(aucune)" else None

        submit_map = st.form_submit_button("✅ Valider et analyser", use_container_width=True, type="primary")

    if not submit_map:
        return

    # 3. Nettoyage
    final_mapping = {k: v for k, v in corrected_mapping.items() if v}
    df_clean, warnings_list = validate_and_clean(df, final_mapping)

    if warnings_list:
        for w in warnings_list:
            st.warning(w)

    # 4. Statistiques descriptives
    st.markdown("#### 📊 Statistiques descriptives")
    stats = get_stats_summary(df_clean)
    _display_stats(stats)

    # 5. Visualisations auto
    st.markdown("#### 📈 Visualisations automatiques")
    _auto_visualize(df_clean)

    # 6. Prévisions batch (si modèle chargé et colonnes OK)
    required_for_pred = ["region", "culture", "type_sol",
                          "surface_ha", "pluviometrie_mm", "temperature_moyenne_c"]
    has_all = all(c in df_clean.columns for c in required_for_pred)

    if has_all and model.is_trained():
        st.markdown("#### 🌾 Prévisions de rendement sur vos données")
        _batch_predict(df_clean, model)
    elif not has_all:
        st.info("Pour obtenir des prévisions, mappez toutes les colonnes requises (région, culture, sol, surface, pluie, température).")


def _display_stats(stats: dict) -> None:
    """Affiche les statistiques descriptives en cartes."""
    from modules.styles import kpi_card

    cols = st.columns(4)
    with cols[0]:
        st.markdown(kpi_card("Lignes", str(stats.get("n_lignes", "–"))), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(kpi_card("Colonnes", str(stats.get("n_colonnes", "–"))), unsafe_allow_html=True)
    with cols[2]:
        val = f"{stats['rendement_moyen']:.2f} t/ha" if "rendement_moyen" in stats else "–"
        st.markdown(kpi_card("Rendement moyen", val), unsafe_allow_html=True)
    with cols[3]:
        val = f"{stats['surface_totale_ha']:.1f} ha" if "surface_totale_ha" in stats else "–"
        st.markdown(kpi_card("Surface totale", val), unsafe_allow_html=True)


def _auto_visualize(df: pd.DataFrame) -> None:
    """Génère automatiquement 2 ou 3 graphiques pertinents."""
    tab_names = []
    if "rendement_t_ha" in df.columns and "region" in df.columns:
        tab_names.append("Rendement par région")
    if "pluviometrie_mm" in df.columns and "rendement_t_ha" in df.columns:
        tab_names.append("Pluie vs Rendement")
    if "culture" in df.columns and "rendement_t_ha" in df.columns:
        tab_names.append("Distribution par culture")

    if not tab_names:
        st.info("Pas assez de colonnes reconnues pour générer des graphiques automatiques.")
        return

    tabs = st.tabs(tab_names)
    idx = 0

    if "Rendement par région" in tab_names:
        with tabs[idx]:
            agg = df.groupby("region")["rendement_t_ha"].mean().reset_index()
            fig = px.bar(agg, x="region", y="rendement_t_ha",
                          color="rendement_t_ha", color_continuous_scale="Greens",
                          title="Rendement moyen par région",
                          labels={"rendement_t_ha": "Rendement (t/ha)", "region": "Région"})
            fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=380)
            st.plotly_chart(fig, use_container_width=True)
            idx += 1

    if "Pluie vs Rendement" in tab_names:
        with tabs[idx]:
            kwargs = {"color": "culture"} if "culture" in df.columns else {}
            fig = px.scatter(df, x="pluviometrie_mm", y="rendement_t_ha", **kwargs,
                              title="Pluviométrie vs Rendement",
                              labels={"pluviometrie_mm": "Pluviométrie (mm)",
                                      "rendement_t_ha": "Rendement (t/ha)"})
            fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=380)
            st.plotly_chart(fig, use_container_width=True)
            idx += 1

    if "Distribution par culture" in tab_names:
        with tabs[idx]:
            fig = px.box(df, x="culture", y="rendement_t_ha", color="culture",
                          title="Distribution des rendements par culture",
                          labels={"rendement_t_ha": "Rendement (t/ha)", "culture": "Culture"})
            fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


def _batch_predict(df: pd.DataFrame, model) -> None:
    """Génère des prévisions ML pour chaque ligne du fichier."""
    results = []
    errors  = 0

    progress = st.progress(0, text="Prévisions en cours…")
    n = len(df)

    for i, row in df.iterrows():
        try:
            pred = model.predict({
                "region":               row.get("region", "Maritime"),
                "culture":              row.get("culture", "Maïs"),
                "type_sol":             row.get("type_sol", "Argileux"),
                "surface_ha":           row.get("surface_ha", 1.0),
                "pluviometrie_mm":      row.get("pluviometrie_mm", 800),
                "temperature_moyenne_c": row.get("temperature_moyenne_c", 27),
            })
            results.append({**dict(row), "rendement_predit_t_ha": pred["rendement_t_ha"],
                             "production_predite_t": pred["production_total_t"],
                             "risque_predit": pred["niveau_risque"]})
        except Exception:  # noqa: BLE001
            errors += 1
        progress.progress((i + 1) / n)

    progress.empty()

    df_results = pd.DataFrame(results)
    st.success(f"✓ {len(df_results)} prévisions générées ({errors} erreur(s)).")
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    # Export
    csv_bytes = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Télécharger les prévisions (CSV)",
        data=csv_bytes,
        file_name="previsions_batch.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Résumé graphique
    if "rendement_predit_t_ha" in df_results.columns and "region" in df_results.columns:
        agg = df_results.groupby("region")["rendement_predit_t_ha"].mean().reset_index()
        fig = px.bar(agg, x="region", y="rendement_predit_t_ha",
                      color="rendement_predit_t_ha", color_continuous_scale="Greens",
                      title="Rendements prédits par région",
                      labels={"rendement_predit_t_ha": "Rendement prédit (t/ha)", "region": "Région"})
        fig.update_layout(plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA", height=380)
        st.plotly_chart(fig, use_container_width=True)


def _show_help() -> None:
    """Affiche la documentation d'aide sur les formats acceptés."""
    st.markdown("""
    <div class="card card-green">
        <h4>📌 Formats acceptés et colonnes attendues</h4>
        <p>Pour obtenir des <strong>prévisions automatiques</strong>, votre fichier doit contenir les colonnes suivantes
        (les noms peuvent varier, le système les détectera automatiquement) :</p>
        <table style="width:100%; border-collapse:collapse; font-size:.9rem;">
            <tr style="background:#E8F5E9;">
                <th style="padding:.5rem; text-align:left;">Colonne</th>
                <th style="padding:.5rem; text-align:left;">Description</th>
                <th style="padding:.5rem; text-align:left;">Exemple</th>
            </tr>
            <tr><td style="padding:.4rem;"><code>region</code></td>
                <td>Région du Togo</td><td>Maritime, Kara…</td></tr>
            <tr style="background:#F9FBE7;"><td style="padding:.4rem;"><code>culture</code></td>
                <td>Type de culture</td><td>Maïs, Sorgho, Mil</td></tr>
            <tr><td style="padding:.4rem;"><code>type_sol</code></td>
                <td>Nature du sol</td><td>Argileux, Sableux…</td></tr>
            <tr style="background:#F9FBE7;"><td style="padding:.4rem;"><code>surface_ha</code></td>
                <td>Surface cultivée (ha)</td><td>5.0</td></tr>
            <tr><td style="padding:.4rem;"><code>pluviometrie_mm</code></td>
                <td>Pluviométrie cumulée (mm)</td><td>850</td></tr>
            <tr style="background:#F9FBE7;"><td style="padding:.4rem;"><code>temperature_moyenne_c</code></td>
                <td>Température moyenne (°C)</td><td>27.5</td></tr>
        </table>
        <p style="margin-top:.75rem; color:#616161; font-size:.85rem;">
            Les fichiers <strong>PDF</strong> font l'objet d'une analyse textuelle par l'IA.
        </p>
    </div>
    """, unsafe_allow_html=True)
