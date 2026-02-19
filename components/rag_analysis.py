"""
RAG Analysis page for Streamlit
Upload files and get batch predictions
"""

import streamlit as st
import pandas as pd
import logging
from pathlib import Path

from rag.loader import FileLoader
from rag.processor import DataProcessor
from rag.batch_predictor import BatchPredictor
from rag.visualizer import RAGVisualizer

logger = logging.getLogger(__name__)


def show_rag_analysis_page():
    """RAG analysis page"""
    
    st.markdown("## 📊 Batch Analysis - Upload Your Data")
    
    st.info("""
    Upload a CSV or PDF file with your agricultural data.
    The system will automatically:
    - 📍 Identify columns
    - 🧮 Generate predictions
    - 📈 Create charts
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose file (CSV/PDF/Excel)",
        type=['csv', 'pdf', 'xlsx'],
        help="Max 100 MB"
    )
    
    if uploaded_file:
        # Save temp file
        temp_path = Path(f"temp/{uploaded_file.name}")
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Load file
            with st.spinner("📂 Loading file..."):
                df = FileLoader.load_file(temp_path)
                info = FileLoader.get_file_info(df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", info['rows'])
            with col2:
                st.metric("Columns", info['columns'])
            with col3:
                st.metric("Size", info['memory_usage'])
            
            # Preview
            with st.expander("👀 Data preview"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Column identification
            st.markdown("### 🔍 Column Identification")
            col_mapping = DataProcessor.identify_columns(df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Auto-detected:**")
                for field, col in col_mapping.items():
                    status = "✓" if col else "❌"
                    st.caption(f"{status} {field}: {col}")
            
            with col2:
                st.write("**Correct if needed:**")
                for field in col_mapping:
                    options = [col_mapping[field]] if col_mapping[field] else []
                    options += [c for c in df.columns if c not in options]
                    col_mapping[field] = st.selectbox(
                        f"Select {field}",
                        options,
                        key=f"col_{field}"
                    )
            
            # Generate predictions
            if st.button("🚀 Generate Predictions", use_container_width=True):
                try:
                    with st.spinner("🧮 Making predictions..."):
                        predictor = BatchPredictor()
                        df_results = predictor.predict_batch(df, col_mapping)
                        summary = predictor.get_summary_stats(df_results)
                    
                    st.success("✓ Predictions complete!")
                    
                    # Show stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Average Yield", f"{summary['rendement_moyen']:.2f} t/ha")
                    with col2:
                        st.metric("Total Production", f"{summary['production_totale']:.2f} t")
                    with col3:
                        st.metric("Min Yield", f"{summary['rendement_min']:.2f} t/ha")
                    with col4:
                        st.metric("Max Yield", f"{summary['rendement_max']:.2f} t/ha")
                    
                    # Show visualizations
                    st.markdown("### 📊 Visualizations")
                    
                    plots = RAGVisualizer.generate_all_visualizations(df_results, col_mapping)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if plots['distribution']:
                            st.plotly_chart(plots['distribution'], use_container_width=True)
                    
                    with col2:
                        if plots['risk']:
                            st.plotly_chart(plots['risk'], use_container_width=True)
                    
                    if plots.get('production_culture'):
                        st.plotly_chart(plots['production_culture'], use_container_width=True)
                    
                    if plots.get('scatter'):
                        st.plotly_chart(plots['scatter'], use_container_width=True)
                    
                    if plots.get('region'):
                        st.plotly_chart(plots['region'], use_container_width=True)
                    
                    # Show results
                    st.markdown("### 💾 Result Data")
                    
                    with st.expander("View all predictions"):
                        st.dataframe(df_results, use_container_width=True)
                    
                    # Download
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name=f"predictions_batch_{uploaded_file.name.split('.')[0]}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Save in session
                    st.session_state.rag_results = df_results
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Prediction error: {e}", exc_info=True)
        
        except Exception as e:
            st.error(f"❌ File loading error: {str(e)}")
            logger.error(f"File error: {e}", exc_info=True)
        
        finally:
            # Clean temp file
            import os
            if temp_path.exists():
                os.remove(temp_path)
