"""
Visualizations for RAG data
Auto-generate charts
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

logger = logging.getLogger(__name__)


class RAGVisualizer:
    """Create automatic visualizations"""
    
    @staticmethod
    def plot_predictions_distribution(df: pd.DataFrame):
        """Distribution histogram"""
        
        if 'rendement_predit' not in df.columns:
            return None
        
        fig = px.histogram(
            df,
            x='rendement_predit',
            nbins=30,
            title='Distribution of Predicted Yields',
            labels={'rendement_predit': 'Yield (t/ha)'},
            color_discrete_sequence=['#4CAF50']
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def plot_production_by_culture(df: pd.DataFrame, culture_col: str):
        """Production by culture"""
        
        if culture_col not in df.columns or 'production_estimee' not in df.columns:
            return None
        
        df_agg = df.groupby(culture_col)['production_estimee'].sum().reset_index()
        
        fig = px.bar(
            df_agg,
            x=culture_col,
            y='production_estimee',
            title='Total Estimated Production by Culture',
            labels={'production_estimee': 'Production (t)'},
            color='production_estimee',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def plot_risk_breakdown(df: pd.DataFrame):
        """Risk distribution pie chart"""
        
        if 'risque' not in df.columns:
            return None
        
        risk_counts = df['risque'].value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title='Risk Distribution',
            color_discrete_map={
                'Faible': '#4CAF50',
                'Moyen': '#FFC107',
                'Élevé': '#F44336'
            }
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def plot_rendement_vs_pluviometrie(df: pd.DataFrame, rain_col: str):
        """Scatter plot yield vs rainfall"""
        
        if rain_col not in df.columns or 'rendement_predit' not in df.columns:
            return None
        
        fig = px.scatter(
            df,
            x=rain_col,
            y='rendement_predit',
            title='Rainfall - Yield Relationship',
            labels={
                rain_col: 'Pluviometry (mm)',
                'rendement_predit': 'Yield (t/ha)'
            },
            color='risque' if 'risque' in df.columns else None,
            color_discrete_map={
                'Faible': '#4CAF50',
                'Moyen': '#FFC107',
                'Élevé': '#F44336'
            }
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def plot_prediction_by_region(df: pd.DataFrame, region_col: str):
        """Average yield by region"""
        
        if region_col not in df.columns or 'rendement_predit' not in df.columns:
            return None
        
        df_agg = df.groupby(region_col)['rendement_predit'].mean().reset_index()
        
        fig = px.bar(
            df_agg,
            x=region_col,
            y='rendement_predit',
            title='Average Predicted Yield by Region',
            labels={'rendement_predit': 'Average Yield (t/ha)'},
            color='rendement_predit',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=400)
        return fig
    
    @staticmethod
    def generate_all_visualizations(df: pd.DataFrame, col_mapping: dict):
        """Generate all visualizations"""
        
        logger.info("Generating visualizations...")
        
        plots = {
            'distribution': RAGVisualizer.plot_predictions_distribution(df),
            'risk': RAGVisualizer.plot_risk_breakdown(df),
        }
        
        if col_mapping.get('culture') and col_mapping['culture'] in df.columns:
            plots['production_culture'] = RAGVisualizer.plot_production_by_culture(
                df, col_mapping['culture']
            )
        
        if col_mapping.get('pluviometrie') and col_mapping['pluviometrie'] in df.columns:
            plots['scatter'] = RAGVisualizer.plot_rendement_vs_pluviometrie(
                df, col_mapping['pluviometrie']
            )
        
        if col_mapping.get('region') and col_mapping['region'] in df.columns:
            plots['region'] = RAGVisualizer.plot_prediction_by_region(
                df, col_mapping['region']
            )
        
        logger.info(f"✓ {len([p for p in plots.values() if p])} visualizations created")
        
        return plots
