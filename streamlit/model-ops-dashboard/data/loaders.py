"""Cached loaders for Transparensea generated artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from data.schema import DISCLOSURE, FINANCIAL_ASSUMPTIONS, PRODUCT_NAME, PRODUCT_TAGLINE, BRAND

GENERATED = Path(__file__).resolve().parent / "generated"


@st.cache_data(show_spinner=False)
def _read_csv(name: str) -> pd.DataFrame:
    path = GENERATED / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run: python scripts/build_demo_data.py"
        )
    return pd.read_csv(path)


def load_all() -> dict[str, pd.DataFrame]:
    names = [
        "model_versions",
        "model_runs",
        "customers",
        "decisions",
        "monthly_kpis",
        "feature_influence",
        "feature_dictionary",
        "business_exceptions",
        "statistical_outliers",
        "generated_insights",
        "human_insight_reviews",
        "suggested_actions",
        "action_measurements",
        "validation_report",
    ]
    return {name: _read_csv(name) for name in names}


def product_meta() -> dict[str, str]:
    return {
        "product": PRODUCT_NAME,
        "tagline": PRODUCT_TAGLINE,
        "brand": BRAND,
        "disclosure": DISCLOSURE,
        "formula": FINANCIAL_ASSUMPTIONS["formula"],
    }
