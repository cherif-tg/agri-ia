"""
Components module - Pages et composants UI
"""

from .home import show_home_page
from .prediction import show_prediction_form, show_prediction_results
from .visualizations import show_visualizations_page
from .history import show_history_page
from .report import show_report_page
from .about import show_about_page

__all__ = [
    "show_home_page",
    "show_prediction_form",
    "show_prediction_results",
    "show_visualizations_page",
    "show_history_page",
    "show_report_page",
    "show_about_page"
]
