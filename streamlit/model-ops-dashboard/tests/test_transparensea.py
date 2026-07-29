"""Tests for Transparensea demo data contract and analytics."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "data" / "generated"


@pytest.fixture(scope="module")
def artifacts() -> dict[str, pd.DataFrame]:
    required = [
        "model_runs",
        "model_versions",
        "decisions",
        "monthly_kpis",
        "generated_insights",
        "suggested_actions",
        "action_measurements",
        "validation_report",
    ]
    missing = [name for name in required if not (GEN / f"{name}.csv").exists()]
    if missing:
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build_demo_data.py")])
    return {name: pd.read_csv(GEN / f"{name}.csv") for name in [
        "model_runs",
        "model_versions",
        "decisions",
        "monthly_kpis",
        "customers",
        "feature_influence",
        "statistical_outliers",
        "generated_insights",
        "suggested_actions",
        "action_measurements",
        "validation_report",
        "business_exceptions",
        "human_insight_reviews",
    ]}


def test_run_count(artifacts):
    assert len(artifacts["model_runs"]) == 24


def test_model_versions(artifacts):
    versions = set(artifacts["model_versions"]["model_version"])
    assert {"v1.0", "v1.1"} <= versions
    runs = artifacts["model_runs"]
    assert (runs.loc[runs["run_month"] < "2026-02", "model_version"] == "v1.0").all()
    assert (runs.loc[runs["run_month"] >= "2026-02", "model_version"] == "v1.1").all()


def test_decision_ids_unique(artifacts):
    assert artifacts["decisions"]["decision_id"].is_unique


def test_execution_classes_exhaustive(artifacts):
    allowed = {
        "Adopted",
        "Modified",
        "Ignored",
        "Outside recommendation",
        "Suppression adopted",
        "Suppression rejected",
    }
    classes = set(artifacts["decisions"]["execution_class"].unique())
    assert classes <= allowed
    assert len(classes) >= 5


def test_no_negative_messages(artifacts):
    assert (artifacts["monthly_kpis"]["messages_sent"] >= 0).all()
    assert (artifacts["monthly_kpis"]["recommended_messages"] >= 0).all()


def test_conversion_bounds(artifacts):
    assert artifacts["decisions"]["converted"].isin([0, 1]).all()


def test_nir_reconciliation(artifacts):
    by_run = artifacts["decisions"].groupby("run_id")["net_incremental_revenue"].sum()
    monthly = artifacts["monthly_kpis"].set_index("run_id")["net_incremental_revenue"]
    aligned = by_run.align(monthly, join="inner")
    assert (aligned[0] - aligned[1]).abs().max() < 1e-6


def test_suppression_behavior(artifacts):
    d = artifacts["decisions"]
    supp_adopt = d[d["execution_class"] == "Suppression adopted"]
    assert (supp_adopt["actual_campaign"] == "Suppression").all()
    supp_rej = d[d["execution_class"] == "Suppression rejected"]
    assert (supp_rej["actual_campaign"] != "Suppression").all()


def test_insight_uses_calculated_values(artifacts):
    text = artifacts["generated_insights"].iloc[0]["automated_text"]
    assert "%" in text
    assert "$" in text


def test_action_measurement_refs(artifacts):
    action_ids = set(artifacts["suggested_actions"]["action_id"])
    measured = set(artifacts["action_measurements"]["action_id"])
    assert measured <= action_ids
    assert {"Successful", "Inconclusive"} <= set(
        artifacts["action_measurements"]["result_classification"]
    )


def test_validation_all_passed(artifacts):
    assert artifacts["validation_report"]["passed"].all()


def test_modules_import():
    sys.path.insert(0, str(ROOT))
    from views import pages  # noqa: F401
    from analytics import adoption, financials  # noqa: F401
    from charts.product_charts import rates_trend  # noqa: F401
    from data import loaders, schema  # noqa: F401
    monthly = pd.read_csv(GEN / "monthly_kpis.csv")
    assert rates_trend(monthly) is not None
