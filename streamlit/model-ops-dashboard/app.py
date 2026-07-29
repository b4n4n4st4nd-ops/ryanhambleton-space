"""Transparensea — Model Transparency, Adoption & Impact.

A.Typical demonstration for the Lab.
"""

from __future__ import annotations

import streamlit as st

from components.ui import (
    apply_filters,
    get_data,
    inject_styles,
    render_filter_bar,
    render_masthead,
    render_navigation,
)
from views.pages import (
    render_adoption,
    render_conversion_revenue,
    render_exceptions,
    render_improvement_history,
    render_input_transparency,
    render_insights_actions,
    render_model_details,
    render_overview,
    render_recommendations,
)

st.set_page_config(
    page_title="Transparensea · A.Typical",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()

PAGES = {
    "Overview": render_overview,
    "Inputs": render_input_transparency,
    "Recommendations": render_recommendations,
    "Adoption": render_adoption,
    "Impact": render_conversion_revenue,
    "Exceptions": render_exceptions,
    "Insights & Actions": render_insights_actions,
    "Improvement": render_improvement_history,
    "Model Details": render_model_details,
}

try:
    data = get_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

render_masthead(data)
page = render_navigation()
filters = render_filter_bar(data)
filtered = apply_filters(data, filters)
PAGES[page](filtered)
