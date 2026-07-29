"""Adoption analytics helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

ADOPTION_LABELS = {
    "production_coverage": "Production coverage",
    "message_volume_adoption": "Message-volume adoption",
    "customer_selection_adoption": "Customer-selection adoption",
    "campaign_choice_adoption": "Campaign-choice adoption",
    "followup_adoption": "Follow-up adoption",
    "suppression_adoption": "Suppression adoption",
    "priority_adoption": "Priority adoption",
}


def pchart_limits(series: pd.Series, n: pd.Series) -> pd.DataFrame:
    y = series.astype(float).to_numpy()
    weights = n.clip(lower=1).astype(float).to_numpy()
    pbar = float(np.average(y, weights=weights))
    sigma = np.sqrt(pbar * (1 - pbar) / weights)
    return pd.DataFrame(
        {
            "value": y,
            "center": pbar,
            "ucl": pbar + 3 * sigma,
            "lcl": np.maximum(0, pbar - 3 * sigma),
            "outlier": y < np.maximum(0, pbar - 3 * sigma),
        },
        index=series.index,
    )


def pareto_gap(
    decisions: pd.DataFrame,
    dimension: str,
    recommended_campaign: str | None = "Performance Collection",
) -> pd.DataFrame:
    """Contribution to campaign-choice adoption gap for a selected slice."""
    df = decisions.copy()
    if recommended_campaign:
        df = df[df["recommended_campaign"] == recommended_campaign]
    contact = df[df["recommended_campaign"] != "Suppression"]
    if contact.empty:
        contact = df
    contact = contact.copy()
    contact["exact_match"] = contact["actual_campaign"] == contact["recommended_campaign"]
    grouped = (
        contact.groupby(dimension, dropna=False)
        .agg(customers=("customer_id", "count"), exact=("exact_match", "sum"))
        .reset_index()
    )
    grouped["misses"] = grouped["customers"] - grouped["exact"]
    grouped = grouped.sort_values("misses", ascending=False)
    total = grouped["misses"].sum() or 1
    grouped["contribution"] = grouped["misses"] / total
    grouped["cumulative"] = grouped["contribution"].cumsum()
    return grouped


def decision_class_summary(decisions: pd.DataFrame) -> pd.DataFrame:
    g = (
        decisions.groupby("execution_class")
        .agg(
            customers=("decision_id", "count"),
            messages=("actual_campaign", lambda s: int((s != "Suppression").sum())),
            conversion_rate=("converted", "mean"),
            incremental_conversion_rate=("incremental_conversion_prob", "mean"),
            gross_revenue=("gross_revenue", "sum"),
            campaign_cost=("campaign_cost", "sum"),
            net_incremental_revenue=("net_incremental_revenue", "sum"),
            missed_value=("missed_value", "sum"),
            wasted_spend=("wasted_spend", "sum"),
        )
        .reset_index()
    )
    g["revenue_per_message"] = g["gross_revenue"] / g["messages"].clip(lower=1)
    return g
