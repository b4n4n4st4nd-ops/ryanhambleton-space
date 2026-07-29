"""
Build reproducible Transparensea demo artifacts for A.Typical.

Data source decision: Option B — deterministic synthetic data inspired by
Hillstrom-style uplift marketing workflows. No runtime network dependency.

Usage (from streamlit/model-ops-dashboard):
  python scripts/build_demo_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.schema import (  # noqa: E402
    BRAND,
    CAMPAIGNS,
    CHANNELS,
    DISCLOSURE,
    EXECUTION_CLASSES,
    FEATURE_DEFINITIONS,
    FINANCIAL_ASSUMPTIONS,
    LOYALTY_TIERS,
    MARKET_TYPES,
    PRIMARY_TREATMENTS,
    PRODUCT_NAME,
    REGIONS,
    SEGMENTS,
)

SEED = 42
N_CUSTOMERS = 2400
RUN_MONTHS = pd.period_range("2024-08", "2026-07", freq="M")
OUT_DIR = ROOT / "data" / "generated"
RAW_DIR = ROOT / "data" / "raw"


def _rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


def _month_index(period: pd.Period) -> int:
    return int((period - RUN_MONTHS[0]).n)


def _phase(month_idx: int) -> str:
    if month_idx < 6:
        return "initial"
    if month_idx < 12:
        return "recurring"
    if month_idx < 16:
        return "intervention"
    return "improved"


def _model_version(month_idx: int) -> str:
    return "v1.1" if month_idx >= 18 else "v1.0"


def build_customers(rng: np.random.Generator) -> pd.DataFrame:
    n = N_CUSTOMERS
    regions = rng.choice(REGIONS, size=n, p=[0.12, 0.18, 0.10, 0.12, 0.18, 0.16, 0.14])
    market = rng.choice(MARKET_TYPES, size=n, p=[0.42, 0.38, 0.20])
    channel = rng.choice(CHANNELS, size=n, p=[0.28, 0.22, 0.30, 0.20])
    loyalty = rng.choice(LOYALTY_TIERS, size=n, p=[0.35, 0.35, 0.22, 0.08])
    customer_type = rng.choice(["New", "Returning"], size=n, p=[0.22, 0.78])
    states = {
        "Pacific Northwest": ["WA", "OR", "ID"],
        "California": ["CA"],
        "Mountain West": ["CO", "UT", "MT"],
        "Southwest": ["AZ", "NM", "NV"],
        "Midwest": ["IL", "MN", "OH", "MI"],
        "Northeast": ["NY", "MA", "PA", "NJ"],
        "Southeast": ["GA", "FL", "NC", "TN"],
    }
    state = [rng.choice(states[r]) for r in regions]

    tenure = rng.integers(1, 96, size=n)
    recency = rng.integers(1, 240, size=n)
    spend = np.round(rng.lognormal(mean=5.2, sigma=0.7, size=n), 2)
    frequency = rng.integers(0, 18, size=n)
    digital = np.clip(rng.beta(2.2, 2.0, size=n), 0, 1)
    email = np.clip(rng.beta(2.0, 2.4, size=n), 0, 1)
    prior_resp = np.clip(rng.beta(1.8, 3.0, size=n), 0, 1)
    cat_aff = np.clip(rng.beta(2.5, 2.0, size=n), 0, 1)
    perf_aff = np.clip(rng.beta(2.0, 2.5, size=n), 0, 1)
    life_aff = np.clip(rng.beta(2.3, 2.2, size=n), 0, 1)
    days_visit = rng.integers(0, 90, size=n)
    followup = rng.random(n) < 0.18

    segment = []
    for i in range(n):
        if customer_type[i] == "New":
            segment.append("New Customer")
        elif spend[i] > np.percentile(spend, 80):
            segment.append("High-Value")
        elif recency[i] > 120 and email[i] < 0.35:
            segment.append("At-Risk")
        elif perf_aff[i] > 0.65:
            segment.append("Performance Affinity")
        elif life_aff[i] > 0.65:
            segment.append("Lifestyle Affinity")
        else:
            segment.append("Returning Buyer")

    return pd.DataFrame(
        {
            "customer_id": [f"AT-{100000 + i}" for i in range(n)],
            "tenure_months": tenure,
            "recency_days": recency,
            "historical_spend": spend,
            "purchase_frequency": frequency,
            "digital_engagement": np.round(digital, 3),
            "email_engagement": np.round(email, 3),
            "prior_campaign_response": np.round(prior_resp, 3),
            "category_affinity": np.round(cat_aff, 3),
            "performance_affinity": np.round(perf_aff, 3),
            "lifestyle_affinity": np.round(life_aff, 3),
            "days_since_visit": days_visit,
            "followup_eligible": followup,
            "primary_channel": channel,
            "loyalty_tier": loyalty,
            "customer_type": customer_type,
            "region": regions,
            "state": state,
            "market_type": market,
            "segment": segment,
        }
    )


def _true_conversion_prob(
    df: pd.DataFrame, treatment: str, version: str, rng: np.random.Generator
) -> np.ndarray:
    """Ground-truth propensity used to train and to simulate outcomes."""
    base = (
        0.035
        + 0.04 * df["email_engagement"].to_numpy()
        + 0.03 * df["digital_engagement"].to_numpy()
        + 0.025 * df["prior_campaign_response"].to_numpy()
        - 0.00012 * df["recency_days"].to_numpy()
        + 0.00004 * np.minimum(df["historical_spend"].to_numpy(), 2000)
        / 10
    )
    if treatment == "New Season Edit":
        lift = (
            0.045 * df["lifestyle_affinity"].to_numpy()
            + 0.03 * df["category_affinity"].to_numpy()
            - 0.02 * df["performance_affinity"].to_numpy()
        )
        if version == "v1.1":
            lift = lift - 0.015 * (df["performance_affinity"].to_numpy() > 0.6)
    elif treatment == "Performance Collection":
        lift = (
            0.055 * df["performance_affinity"].to_numpy()
            + 0.02 * df["digital_engagement"].to_numpy()
            + 0.015 * (df["primary_channel"].eq("Paid Social").to_numpy())
        )
        if version == "v1.1":
            lift = lift + 0.02 * df["performance_affinity"].to_numpy()
    else:
        lift = -0.01 + 0.01 * (df["email_engagement"].to_numpy() < 0.25)

    noise = rng.normal(0, 0.01, size=len(df))
    return np.clip(base + lift + noise, 0.005, 0.45)


def fit_t_learner(
    customers: pd.DataFrame, rng: np.random.Generator
) -> tuple[dict[str, Pipeline], dict[str, Pipeline], pd.DataFrame]:
    """Fit v1.0 and v1.1 T-learners on synthetic labeled outcomes."""
    train = customers.sample(n=min(1800, len(customers)), random_state=SEED).copy()
    treatments = list(PRIMARY_TREATMENTS)
    assigned = rng.choice(treatments, size=len(train), p=[0.38, 0.32, 0.30])
    train["treatment"] = assigned
    probs = np.zeros(len(train))
    for treatment in PRIMARY_TREATMENTS:
        mask = assigned == treatment
        if mask.any():
            probs[mask] = _true_conversion_prob(train.loc[mask], treatment, "v1.0", rng)
    train["converted"] = (rng.random(len(train)) < probs).astype(int)

    numeric = [
        "tenure_months",
        "recency_days",
        "historical_spend",
        "purchase_frequency",
        "digital_engagement",
        "email_engagement",
        "prior_campaign_response",
        "category_affinity",
        "performance_affinity",
        "lifestyle_affinity",
        "days_since_visit",
    ]
    categorical = ["primary_channel", "loyalty_tier", "customer_type", "region", "market_type"]
    features = numeric + categorical

    def _make_pipeline() -> Pipeline:
        pre = ColumnTransformer(
            [
                ("num", StandardScaler(), numeric),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    categorical,
                ),
            ]
        )
        return Pipeline(
            [
                ("pre", pre),
                (
                    "clf",
                    LogisticRegression(max_iter=800, C=0.8, solver="lbfgs"),
                ),
            ]
        )

    models_v10: dict[str, Pipeline] = {}
    models_v11: dict[str, Pipeline] = {}
    importance_rows: list[dict] = []

    for treatment in treatments:
        mask = train["treatment"] == treatment
        X = train.loc[mask, features]
        y = train.loc[mask, "converted"]
        pipe = _make_pipeline()
        pipe.fit(X, y)
        models_v10[treatment] = pipe

        # v1.1: reweight / slightly shift labels near performance boundary
        y11 = y.copy()
        boundary = (
            (train.loc[mask, "performance_affinity"] > 0.55)
            & (train.loc[mask, "lifestyle_affinity"] > 0.45)
            & (treatment == "New Season Edit")
        )
        y11.loc[boundary] = 0
        boost = (
            (train.loc[mask, "performance_affinity"] > 0.6)
            & (treatment == "Performance Collection")
        )
        flip_idx = train.loc[mask].index[boost][: max(1, int(boost.sum() * 0.15))]
        y11.loc[flip_idx] = 1
        pipe11 = _make_pipeline()
        pipe11.fit(X, y11)
        models_v11[treatment] = pipe11

        # Permutation importance on v1.0 (lightweight)
        result = permutation_importance(
            pipe, X, y, n_repeats=2, random_state=SEED, scoring="accuracy", n_jobs=1
        )
        # Approximate feature names after one-hot is hard; report on raw numeric + cats
        for i, col in enumerate(features):
            importance_rows.append(
                {
                    "model_version": "v1.0",
                    "treatment": treatment,
                    "feature": col,
                    "method": "Permutation importance",
                    "importance": float(result.importances_mean[i]),
                    "direction_note": "Higher absolute importance indicates stronger effect on predicted conversion under this treatment.",
                }
            )

        # Standardized coefficient proxy from logistic on numeric-only for transparency
        num_pipe = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=600, C=0.8)),
            ]
        )
        num_pipe.fit(train.loc[mask, numeric], y)
        coefs = num_pipe.named_steps["clf"].coef_[0]
        for col, coef in zip(numeric, coefs):
            importance_rows.append(
                {
                    "model_version": "v1.0",
                    "treatment": treatment,
                    "feature": col,
                    "method": "Standardized coefficient",
                    "importance": float(coef),
                    "direction_note": (
                        "Positive coefficient increases conversion probability under this treatment; "
                        "negative decreases it. Not causal proof."
                    ),
                }
            )

        # Mirror v1.1 coefficients with small shift
        num_pipe11 = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=600, C=0.8)),
            ]
        )
        num_pipe11.fit(train.loc[mask, numeric], y11)
        coefs11 = num_pipe11.named_steps["clf"].coef_[0]
        for col, coef in zip(numeric, coefs11):
            importance_rows.append(
                {
                    "model_version": "v1.1",
                    "treatment": treatment,
                    "feature": col,
                    "method": "Standardized coefficient",
                    "importance": float(coef),
                    "direction_note": (
                        "Positive coefficient increases conversion probability under this treatment; "
                        "negative decreases it. Not causal proof."
                    ),
                }
            )
            importance_rows.append(
                {
                    "model_version": "v1.1",
                    "treatment": treatment,
                    "feature": col,
                    "method": "Permutation importance",
                    "importance": float(abs(coef) * 0.08 + rng.normal(0, 0.002)),
                    "direction_note": "Higher absolute importance indicates stronger effect on predicted conversion under this treatment.",
                }
            )

    return models_v10, models_v11, pd.DataFrame(importance_rows)


def score_customers(
    customers: pd.DataFrame,
    models: dict[str, Pipeline],
    version: str,
) -> pd.DataFrame:
    features = [
        "tenure_months",
        "recency_days",
        "historical_spend",
        "purchase_frequency",
        "digital_engagement",
        "email_engagement",
        "prior_campaign_response",
        "category_affinity",
        "performance_affinity",
        "lifestyle_affinity",
        "days_since_visit",
        "primary_channel",
        "loyalty_tier",
        "customer_type",
        "region",
        "market_type",
    ]
    frame = customers.reset_index(drop=True)
    X = frame[features]
    p_ns = models["New Season Edit"].predict_proba(X)[:, 1]
    p_pc = models["Performance Collection"].predict_proba(X)[:, 1]
    p_sup = models["Suppression"].predict_proba(X)[:, 1]
    aov = FINANCIAL_ASSUMPTIONS["average_order_value"]
    margin = FINANCIAL_ASSUMPTIONS["gross_margin"]
    msg_cost = FINANCIAL_ASSUMPTIONS["message_cost"]
    camp_costs = FINANCIAL_ASSUMPTIONS["campaign_cost_per_message"]

    uplift_ns = p_ns - p_sup
    uplift_pc = p_pc - p_sup
    net_ns = uplift_ns * aov * margin - msg_cost - camp_costs["New Season Edit"]
    net_pc = uplift_pc * aov * margin - msg_cost - camp_costs["Performance Collection"]

    prefer_pc = net_pc >= net_ns
    best_net = np.where(prefer_pc, net_pc, net_ns)
    best_uplift = np.where(prefer_pc, uplift_pc, uplift_ns)
    best_p = np.where(prefer_pc, p_pc, p_ns)
    best_name = np.where(prefer_pc, "Performance Collection", "New Season Edit")

    suppress = best_net <= 0
    recommended = np.where(suppress, "Suppression", best_name)
    predicted = np.where(suppress, p_sup, best_p)
    uplift = np.where(suppress, 0.0, best_uplift)
    net = np.where(suppress, 0.0, best_net)
    priority = np.where(
        suppress,
        0.05 + 0.2 * (1 - predicted),
        np.clip(0.35 + uplift * 8 + net / 20, 0.05, 0.99),
    )
    followup = (
        frame["followup_eligible"].to_numpy()
        & (recommended != "Suppression")
        & (priority > 0.45)
    )

    return pd.DataFrame(
        {
            "customer_id": frame["customer_id"],
            "model_version": version,
            "p_new_season": p_ns,
            "p_performance": p_pc,
            "p_suppression": p_sup,
            "recommended_campaign": recommended,
            "predicted_conversion": predicted,
            "estimated_uplift": uplift,
            "estimated_net_value": net,
            "priority_score": priority,
            "recommend_followup": followup,
        }
    )


def simulate_execution(
    scored: pd.DataFrame,
    customers: pd.DataFrame,
    month_idx: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    phase = _phase(month_idx)
    merged = scored.merge(customers, on="customer_id", how="left")
    n = len(merged)

    if phase == "initial":
        choice_rate, follow_rate, suppress_rate = 0.56, 0.38, 0.70
    elif phase == "recurring":
        choice_rate, follow_rate, suppress_rate = 0.58, 0.40, 0.68
    elif phase == "intervention":
        choice_rate, follow_rate, suppress_rate = 0.66, 0.52, 0.74
    else:
        choice_rate, follow_rate, suppress_rate = 0.78, 0.71, 0.86

    rec = merged["recommended_campaign"].to_numpy(dtype=object)
    force_mod = (
        (phase in ("recurring", "intervention"))
        & (rec == "Performance Collection")
        & merged["region"].isin(["Midwest", "Southwest"]).to_numpy()
        & merged["segment"].isin(["High-Value", "Lifestyle Affinity"]).to_numpy()
        & (merged["market_type"].to_numpy() == "Suburban")
        & (rng.random(n) < (0.72 if phase == "recurring" else 0.35))
    )

    actual = rec.copy()
    classes = np.empty(n, dtype=object)
    u1 = rng.random(n)
    u2 = rng.random(n)

    is_supp = rec == "Suppression"
    supp_adopt = is_supp & (u1 < suppress_rate)
    supp_reject = is_supp & ~supp_adopt
    actual[supp_adopt] = "Suppression"
    classes[supp_adopt] = "Suppression adopted"
    n_rej = int(supp_reject.sum())
    if n_rej:
        reject_opts = np.array(["New Season Edit", "Re-Engagement", "Member Access"])
        actual[supp_reject] = reject_opts[rng.choice(3, size=n_rej, p=[0.55, 0.25, 0.20])]
        classes[supp_reject] = "Suppression rejected"

    is_contact = ~is_supp
    actual[force_mod] = "New Season Edit"
    classes[force_mod] = "Modified"

    remaining = is_contact & ~force_mod
    adopt = remaining & (u1 < choice_rate)
    actual[adopt] = rec[adopt]
    classes[adopt] = "Adopted"

    rem = remaining & ~adopt
    modify_mask = rem & (u2 < 0.45)
    ignore_mask = rem & ~modify_mask
    n_mod = int(modify_mask.sum())
    if n_mod:
        mod_opts = np.array(
            ["New Season Edit", "Member Access", "Re-Engagement", "Performance Collection"]
        )
        actual[modify_mask] = mod_opts[rng.integers(0, len(mod_opts), size=n_mod)]
    classes[modify_mask] = "Modified"
    actual[ignore_mask] = "Suppression"
    classes[ignore_mask] = "Ignored"

    followups = np.zeros(n, dtype=bool)
    fu_idx = merged["recommend_followup"].to_numpy()
    n_fu = int(fu_idx.sum())
    if n_fu:
        followups[fu_idx] = rng.random(n_fu) < follow_rate

    merged["actual_campaign"] = actual
    merged["execution_class"] = classes
    merged["followup_completed"] = followups
    return merged

def _vector_true_p(df: pd.DataFrame, treatment: np.ndarray, version: str) -> np.ndarray:
    base = (
        0.035
        + 0.04 * df["email_engagement"].to_numpy()
        + 0.03 * df["digital_engagement"].to_numpy()
        + 0.025 * df["prior_campaign_response"].to_numpy()
        - 0.00012 * df["recency_days"].to_numpy()
        + 0.00004 * np.minimum(df["historical_spend"].to_numpy(), 2000) / 10
    )
    ns = treatment == "New Season Edit"
    pc = treatment == "Performance Collection"
    sup = treatment == "Suppression"
    other = ~(ns | pc | sup)

    lift = np.zeros(len(df))
    lift[ns] = (
        0.045 * df.loc[ns, "lifestyle_affinity"].to_numpy()
        + 0.03 * df.loc[ns, "category_affinity"].to_numpy()
        - 0.02 * df.loc[ns, "performance_affinity"].to_numpy()
    )
    if version == "v1.1" and ns.any():
        lift[ns] = lift[ns] - 0.015 * (df.loc[ns, "performance_affinity"].to_numpy() > 0.6)

    lift[pc] = (
        0.055 * df.loc[pc, "performance_affinity"].to_numpy()
        + 0.02 * df.loc[pc, "digital_engagement"].to_numpy()
        + 0.015 * df.loc[pc, "primary_channel"].eq("Paid Social").to_numpy()
    )
    if version == "v1.1" and pc.any():
        lift[pc] = lift[pc] + 0.02 * df.loc[pc, "performance_affinity"].to_numpy()

    lift[sup] = -0.01 + 0.01 * (df.loc[sup, "email_engagement"].to_numpy() < 0.25)
    # Fallback treatments behave like mild New Season
    lift[other] = 0.02 * df.loc[other, "category_affinity"].to_numpy()
    return np.clip(base + lift, 0.005, 0.45)


def simulate_outcomes(
    executed: pd.DataFrame,
    month_idx: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    version = _model_version(month_idx)
    aov = FINANCIAL_ASSUMPTIONS["average_order_value"]
    margin = FINANCIAL_ASSUMPTIONS["gross_margin"]
    msg_cost = FINANCIAL_ASSUMPTIONS["message_cost"]
    fu_cost = FINANCIAL_ASSUMPTIONS["followup_cost"]
    camp_costs = FINANCIAL_ASSUMPTIONS["campaign_cost_per_message"]

    actual = executed["actual_campaign"].to_numpy()
    # Map unknown to New Season Edit for propensity
    mapped = np.where(
        np.isin(actual, list(PRIMARY_TREATMENTS)),
        actual,
        "New Season Edit",
    )
    p = _vector_true_p(executed, mapped, version)
    cls = executed["execution_class"].to_numpy()
    p = np.where(cls == "Adopted", p * 1.08, p)
    p = np.where(cls == "Modified", p * 0.82, p)
    p = np.where(
        cls == "Ignored",
        _vector_true_p(executed, np.full(len(executed), "Suppression"), version),
        p,
    )
    p = np.where(cls == "Suppression rejected", p * 0.75, p)
    p = np.where(
        cls == "Suppression adopted",
        _vector_true_p(executed, np.full(len(executed), "Suppression"), version),
        p,
    )
    p = np.where(executed["followup_completed"].to_numpy(), np.minimum(0.55, p + 0.03), p)
    if month_idx >= 16:
        p = np.where(cls == "Adopted", np.minimum(0.55, p * 1.06), p)

    converted = (rng.random(len(executed)) < p).astype(int)
    revenue = np.where(converted == 1, np.round(aov * (0.85 + 0.3 * rng.random(len(executed))), 2), 0.0)
    message_sent = actual != "Suppression"
    cost = np.zeros(len(executed))
    for name, cval in camp_costs.items():
        cost = np.where(actual == name, msg_cost + cval, cost)
    cost = np.where(message_sent, cost, 0.0)
    cost = np.where(executed["followup_completed"].to_numpy(), cost + fu_cost, cost)
    cost = np.round(cost, 2)

    base_p = executed["p_suppression"].fillna(0.05).to_numpy()
    incr = np.where(message_sent, np.maximum(0.0, p - base_p), 0.0)
    net_incr = np.round(incr * aov * margin - cost, 2)

    out = executed.copy()
    out["converted"] = converted
    out["gross_revenue"] = revenue
    out["campaign_cost"] = cost
    out["incremental_conversion_prob"] = np.round(incr, 4)
    out["net_incremental_revenue"] = net_incr
    out["missed_value"] = np.where(
        out["execution_class"].isin(["Ignored", "Modified"]),
        np.maximum(0, out["estimated_net_value"] - out["net_incremental_revenue"]),
        0.0,
    )
    out["wasted_spend"] = np.where(
        (out["execution_class"].isin(["Suppression rejected", "Outside recommendation"]))
        | ((out["converted"] == 0) & (out["actual_campaign"] != "Suppression")),
        out["campaign_cost"] * 0.65,
        0.0,
    )
    return out

def classify_outside_pool(
    customers: pd.DataFrame,
    scored_ids: set[str],
    month_idx: int,
    run_id: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Business contacts a few customers the model did not prioritize this run."""
    phase = _phase(month_idx)
    rate = 0.04 if phase in ("initial", "recurring") else 0.02
    pool = customers[~customers["customer_id"].isin(scored_ids)]
    n = max(5, int(len(customers) * rate * 0.15))
    sample = pool.sample(n=min(n, len(pool)), random_state=SEED + month_idx)
    rows = []
    aov = FINANCIAL_ASSUMPTIONS["average_order_value"]
    margin = FINANCIAL_ASSUMPTIONS["gross_margin"]
    for _, cust in sample.iterrows():
        actual = rng.choice(["New Season Edit", "Member Access", "Re-Engagement"], p=[0.5, 0.25, 0.25])
        p = 0.04 + 0.03 * cust["email_engagement"]
        did = int(rng.random() < p)
        cost = 0.14 + FINANCIAL_ASSUMPTIONS["campaign_cost_per_message"][actual]
        rev = float(aov * (0.9 + 0.2 * rng.random())) if did else 0.0
        rows.append(
            {
                "decision_id": f"{run_id}-{cust['customer_id']}-OUT",
                "run_id": run_id,
                "run_month": str(RUN_MONTHS[month_idx]),
                "run_date": RUN_MONTHS[month_idx].to_timestamp().strftime("%Y-%m-%d"),
                "model_version": _model_version(month_idx),
                "customer_id": cust["customer_id"],
                "region": cust["region"],
                "state": cust["state"],
                "market_type": cust["market_type"],
                "segment": cust["segment"],
                "primary_channel": cust["primary_channel"],
                "loyalty_tier": cust["loyalty_tier"],
                "recommended_campaign": "Suppression",
                "priority_score": 0.02,
                "predicted_conversion": p,
                "estimated_uplift": 0.0,
                "estimated_net_value": 0.0,
                "recommend_followup": False,
                "actual_campaign": actual,
                "execution_class": "Outside recommendation",
                "followup_completed": False,
                "converted": did,
                "gross_revenue": round(rev, 2),
                "campaign_cost": round(cost, 2),
                "incremental_conversion_prob": 0.0,
                "net_incremental_revenue": round(did * aov * margin * 0.2 - cost, 2),
                "missed_value": 0.0,
                "wasted_spend": round(cost * (0.8 if not did else 0.2), 2),
                "tenure_months": cust["tenure_months"],
                "recency_days": cust["recency_days"],
                "historical_spend": cust["historical_spend"],
                "purchase_frequency": cust["purchase_frequency"],
                "digital_engagement": cust["digital_engagement"],
                "email_engagement": cust["email_engagement"],
                "prior_campaign_response": cust["prior_campaign_response"],
                "category_affinity": cust["category_affinity"],
                "performance_affinity": cust["performance_affinity"],
                "lifestyle_affinity": cust["lifestyle_affinity"],
                "days_since_visit": cust["days_since_visit"],
                "followup_eligible": cust["followup_eligible"],
                "customer_type": cust["customer_type"],
                "p_new_season": np.nan,
                "p_performance": np.nan,
                "p_suppression": np.nan,
            }
        )
    return pd.DataFrame(rows)


def compute_monthly_kpis(decisions: pd.DataFrame, model_runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for run_id, g in decisions.groupby("run_id"):
        meta = model_runs.loc[model_runs["run_id"] == run_id].iloc[0]
        eligible = meta["eligible_customers"]
        scored = meta["records_scored"]
        rec_msgs = int((g["recommended_campaign"] != "Suppression").sum())
        sent = int((g["actual_campaign"] != "Suppression").sum())
        rec_customers = g[g["recommended_campaign"] != "Suppression"]
        adopted_choice = g[g["execution_class"] == "Adopted"]
        campaign_choice = (
            len(adopted_choice) / max(1, len(rec_customers))
            if len(rec_customers)
            else np.nan
        )
        # More precise campaign-choice: among recommended contact, exact campaign match
        contact_rec = g[g["recommended_campaign"] != "Suppression"]
        exact = contact_rec[contact_rec["actual_campaign"] == contact_rec["recommended_campaign"]]
        campaign_choice_adoption = len(exact) / max(1, len(contact_rec))

        fu_rec = g[g["recommend_followup"] == True]  # noqa: E712
        fu_adopt = fu_rec["followup_completed"].mean() if len(fu_rec) else np.nan

        supp_rec = g[g["recommended_campaign"] == "Suppression"]
        supp_adopt = (
            (supp_rec["execution_class"] == "Suppression adopted").mean()
            if len(supp_rec)
            else np.nan
        )

        customer_selection = (
            ((contact_rec["actual_campaign"] != "Suppression")).mean()
            if len(contact_rec)
            else np.nan
        )
        message_volume = sent / max(1, rec_msgs)
        # Priority adoption: share of top-quartile priority recommendations that were adopted
        top = contact_rec[contact_rec["priority_score"] >= contact_rec["priority_score"].quantile(0.75)]
        priority_adoption = (
            (top["execution_class"] == "Adopted").mean() if len(top) else np.nan
        )

        rows.append(
            {
                "run_id": run_id,
                "run_month": meta["run_month"],
                "run_date": meta["run_date"],
                "model_version": meta["model_version"],
                "phase": meta["phase"],
                "customers_scored": scored,
                "production_coverage": scored / eligible,
                "recommendations_generated": len(g),
                "recommended_messages": rec_msgs,
                "messages_sent": sent,
                "message_volume_adoption": message_volume,
                "customer_selection_adoption": customer_selection,
                "campaign_choice_adoption": campaign_choice_adoption,
                "followup_adoption": fu_adopt,
                "suppression_adoption": supp_adopt,
                "priority_adoption": priority_adoption,
                "conversion_rate": g["converted"].mean(),
                "incremental_conversion_rate": g["incremental_conversion_prob"].mean(),
                "gross_revenue": g["gross_revenue"].sum(),
                "campaign_cost": g["campaign_cost"].sum(),
                "net_incremental_revenue": g["net_incremental_revenue"].sum(),
                "missed_value": g["missed_value"].sum(),
                "wasted_spend": g["wasted_spend"].sum(),
                "aov": g.loc[g["converted"] == 1, "gross_revenue"].mean()
                if g["converted"].sum()
                else FINANCIAL_ASSUMPTIONS["average_order_value"],
                "revenue_per_message": g["gross_revenue"].sum() / max(1, sent),
                "cost_per_conversion": g["campaign_cost"].sum() / max(1, int(g["converted"].sum())),
                "net_revenue_adopted": g.loc[
                    g["execution_class"] == "Adopted", "net_incremental_revenue"
                ].sum(),
                "net_revenue_modified": g.loc[
                    g["execution_class"] == "Modified", "net_incremental_revenue"
                ].sum(),
                "net_revenue_ignored": g.loc[
                    g["execution_class"] == "Ignored", "net_incremental_revenue"
                ].sum(),
                "net_revenue_outside": g.loc[
                    g["execution_class"] == "Outside recommendation",
                    "net_incremental_revenue",
                ].sum(),
            }
        )
    return pd.DataFrame(rows).sort_values("run_date").reset_index(drop=True)


def build_outliers_and_insights(monthly: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """p-chart style outliers on campaign_choice_adoption + narrative artifacts."""
    y = monthly["campaign_choice_adoption"].to_numpy()
    n = monthly["recommended_messages"].clip(lower=1).to_numpy()
    pbar = np.average(y, weights=n)
    sigma = np.sqrt(pbar * (1 - pbar) / n)
    ucl = pbar + 3 * sigma
    lcl = np.maximum(0, pbar - 3 * sigma)
    monthly = monthly.copy()
    monthly["pchart_center"] = pbar
    monthly["pchart_ucl"] = ucl
    monthly["pchart_lcl"] = lcl
    monthly["is_adoption_outlier"] = y < lcl

    outliers = []
    for _, row in monthly[monthly["is_adoption_outlier"]].iterrows():
        outliers.append(
            {
                "outlier_id": f"OUT-{row['run_month']}-CCA",
                "timestamp": row["run_date"],
                "run_id": row["run_id"],
                "scope": "Campaign-choice adoption",
                "campaign_or_segment": "Performance Collection · Midwest/Southwest Suburban",
                "metric": "campaign_choice_adoption",
                "expected_range": f"{lcl[monthly.index.get_loc(row.name)]:.1%} – {ucl[monthly.index.get_loc(row.name)]:.1%}",
                "actual_value": float(row["campaign_choice_adoption"]),
                "severity": "High",
                "evidence": (
                    f"Monthly campaign-choice adoption {row['campaign_choice_adoption']:.1%} fell below "
                    f"p-chart lower control limit using n={int(row['recommended_messages'])}."
                ),
                "source": "Automated statistical detection",
                "status": "Open",
                "related_insight_id": "INS-001",
                "related_action_id": "ACT-BIZ-001",
            }
        )

    # Ensure at least the recurring-pattern months are flagged if p-chart is quiet
    if len(outliers) < 2:
        recurring = monthly[monthly["phase"] == "recurring"].nsmallest(2, "campaign_choice_adoption")
        for _, row in recurring.iterrows():
            oid = f"OUT-{row['run_month']}-CCA"
            if oid not in {o["outlier_id"] for o in outliers}:
                outliers.append(
                    {
                        "outlier_id": oid,
                        "timestamp": row["run_date"],
                        "run_id": row["run_id"],
                        "scope": "Campaign-choice adoption",
                        "campaign_or_segment": "Performance Collection · Midwest/Southwest Suburban",
                        "metric": "campaign_choice_adoption",
                        "expected_range": f"{pbar - 0.05:.1%} – {pbar + 0.05:.1%}",
                        "actual_value": float(row["campaign_choice_adoption"]),
                        "severity": "High",
                        "evidence": (
                            f"Recurring adoption gap: campaign-choice adoption {row['campaign_choice_adoption']:.1%} "
                            f"versus weighted baseline {pbar:.1%}."
                        ),
                        "source": "Automated statistical detection",
                        "status": "Open",
                        "related_insight_id": "INS-001",
                        "related_action_id": "ACT-BIZ-001",
                    }
                )

    outliers_df = pd.DataFrame(outliers)

    # Business exceptions
    exceptions = pd.DataFrame(
        [
            {
                "exception_id": "BEX-001",
                "timestamp": "2025-03-12",
                "run_id": monthly.loc[monthly["run_month"] == "2025-03", "run_id"].iloc[0]
                if (monthly["run_month"] == "2025-03").any()
                else monthly.iloc[7]["run_id"],
                "scope": "Southeast · Performance Collection",
                "campaign_or_segment": "Performance Collection",
                "metric": "conversion_rate",
                "expected_range": "Baseline seasonal range",
                "actual_value": "Creative delayed 9 days",
                "severity": "Medium",
                "evidence": "Regional creative QA blocked send window for Performance Collection in Southeast.",
                "source": "Marketing operations log",
                "status": "Resolved",
                "related_insight_id": "INS-002",
                "related_action_id": "",
            },
            {
                "exception_id": "BEX-002",
                "timestamp": "2025-11-04",
                "run_id": monthly.loc[monthly["run_month"] == "2025-11", "run_id"].iloc[0]
                if (monthly["run_month"] == "2025-11").any()
                else monthly.iloc[15]["run_id"],
                "scope": "National · New Season Edit",
                "campaign_or_segment": "New Season Edit",
                "metric": "messages_sent",
                "expected_range": "Planned volume",
                "actual_value": "Inventory constrained in 2 sizes",
                "severity": "Medium",
                "evidence": "Merchandising held back assortment depth for two hero SKUs during Holiday build.",
                "source": "Merchandising",
                "status": "Resolved",
                "related_insight_id": "",
                "related_action_id": "ACT-DATA-001",
            },
            {
                "exception_id": "BEX-003",
                "timestamp": "2026-01-18",
                "run_id": monthly.loc[monthly["run_month"] == "2026-01", "run_id"].iloc[0]
                if (monthly["run_month"] == "2026-01").any()
                else monthly.iloc[17]["run_id"],
                "scope": "California · site conversion",
                "campaign_or_segment": "All campaigns",
                "metric": "conversion_rate",
                "expected_range": "Prior 3-month CA baseline",
                "actual_value": "2h checkout outage",
                "severity": "High",
                "evidence": "Checkout service degradation reduced same-day conversion for targeted sends.",
                "source": "Engineering incident",
                "status": "Resolved",
                "related_insight_id": "",
                "related_action_id": "",
            },
        ]
    )

    # Primary computed insight from recurring gap
    pre = monthly[monthly["phase"].isin(["initial", "recurring"])]
    post = monthly[monthly["phase"] == "improved"]
    pre_adopt = pre["campaign_choice_adoption"].mean()
    post_adopt = post["campaign_choice_adoption"].mean()
    pre_nir = pre["net_incremental_revenue"].mean()
    post_nir = post["net_incremental_revenue"].mean()
    delta_adopt = post_adopt - pre_adopt
    delta_nir = post_nir - pre_nir

    insight_text = (
        f"Campaign-choice adoption averaged {pre_adopt:.1%} during months 1–12, with a recurring substitution "
        f"pattern: Midwest and Southwest suburban High-Value and Lifestyle Affinity customers recommended for "
        f"Performance Collection frequently received New Season Edit instead. Modified executions converted "
        f"worse than adopted recommendations. After the default-plan business action and v1.1 boundary tuning, "
        f"campaign-choice adoption rose to {post_adopt:.1%} (+{delta_adopt:.1%} pts) and mean monthly net "
        f"incremental revenue changed by ${delta_nir:,.0f}."
    )

    insights = pd.DataFrame(
        [
            {
                "insight_id": "INS-001",
                "generated_at": "2025-11-28",
                "status": "Confirmed",
                "title": "Recurring Performance Collection substitutions depress adoption and value",
                "automated_text": insight_text,
                "method": "p-chart outlier detection + dimensional contribution + adopted vs modified outcome contrast",
                "evidence_strength": "High",
                "baseline": f"Months 1–12 mean campaign-choice adoption {pre_adopt:.1%}",
                "magnitude": f"Adoption +{delta_adopt:.1%} pts; monthly NIR Δ ${delta_nir:,.0f}",
                "contributing_dimensions": "Campaign=Performance Collection; Region=Midwest/Southwest; Market=Suburban; Segment=High-Value/Lifestyle Affinity",
                "financial_significance": f"Estimated monthly net incremental revenue lift ${delta_nir:,.0f} after interventions",
                "related_outlier_ids": ",".join(outliers_df["outlier_id"].head(3)),
                "why_action_follows": "Substitutions are process-driven and concentrated; making the recommendation the default plan plus boundary model review addresses both execution and scoring.",
            },
            {
                "insight_id": "INS-002",
                "generated_at": "2025-03-20",
                "status": "Confirmed",
                "title": "Southeast Performance Collection conversion dip coincides with creative delay",
                "automated_text": (
                    "Southeast Performance Collection conversion fell outside the recent regional baseline in March 2025. "
                    "A recorded business exception shows creative was delayed nine days, reducing valid send window coverage. "
                    "This is labeled a business exception rather than a model defect."
                ),
                "method": "Regional conversion z-score vs prior 3 months + exception join",
                "evidence_strength": "Medium",
                "baseline": "Prior 3-month Southeast Performance Collection conversion",
                "magnitude": "Temporary regional conversion shortfall tied to delayed creative",
                "contributing_dimensions": "Region=Southeast; Campaign=Performance Collection",
                "financial_significance": "Short-window missed send opportunity; not treated as durable model drift",
                "related_outlier_ids": "",
                "why_action_follows": "Operational exception handling; no permanent model change required.",
            },
            {
                "insight_id": "INS-003",
                "generated_at": "2026-02-10",
                "status": "Under review",
                "title": "Follow-up completion improved but revenue attribution remains mixed",
                "automated_text": (
                    f"Follow-up adoption improved in the post-intervention window, yet incremental revenue attribution "
                    f"for follow-up-only completions remains mixed versus campaign-choice gains. "
                    f"Current measurement classifies the dedicated follow-up coaching action as inconclusive."
                ),
                "method": "Before/after follow-up adoption vs NIR contribution variance",
                "evidence_strength": "Low–Medium",
                "baseline": "Months 7–12 follow-up adoption",
                "magnitude": "Follow-up adoption up; NIR contribution inconclusive",
                "contributing_dimensions": "Follow-up completion; Customer segment=At-Risk",
                "financial_significance": "Insufficient separation from concurrent campaign-choice improvements",
                "related_outlier_ids": "",
                "why_action_follows": "Keep measuring; avoid over-claiming causal credit.",
            },
        ]
    )

    reviews = pd.DataFrame(
        [
            {
                "review_id": "REV-001",
                "insight_id": "INS-001",
                "reviewer": "Maya Chen (ML Product)",
                "reviewed_at": "2025-12-02",
                "status": "Confirmed",
                "human_edited_text": (
                    insight_text
                    + " Marketing leadership agreed the default-plan control is the primary lever; model boundary work is secondary."
                ),
                "edit_reason": "Clarified owner accountability and sequencing of business vs model actions.",
            },
            {
                "review_id": "REV-002",
                "insight_id": "INS-002",
                "reviewer": "Jordan Blake (Marketing Ops)",
                "reviewed_at": "2025-03-22",
                "status": "Confirmed",
                "human_edited_text": insights.loc[1, "automated_text"],
                "edit_reason": "No edit — confirmed as operational exception.",
            },
            {
                "review_id": "REV-003",
                "insight_id": "INS-003",
                "reviewer": "Maya Chen (ML Product)",
                "reviewed_at": "2026-02-14",
                "status": "Under review",
                "human_edited_text": insights.loc[2, "automated_text"],
                "edit_reason": "Awaiting one more measurement month before classification.",
            },
        ]
    )

    actions = pd.DataFrame(
        [
            {
                "action_id": "ACT-BIZ-001",
                "related_insight_id": "INS-001",
                "category": "Business action",
                "original_suggestion": (
                    "Make the recommended campaign and prioritized customer list the default marketing plan. "
                    "Require an explicit documented reason for campaign substitutions."
                ),
                "human_reviewed_text": (
                    "Default the weekly plan to Transparensea recommendations. Substitutions require a documented reason "
                    "in the campaign worksheet before send."
                ),
                "owner": "Jordan Blake (Marketing Ops)",
                "status": "Successful",
                "created_at": "2025-12-03",
                "implemented_at": "2025-12-15",
                "expected_effect": "Campaign-choice adoption → 75%+",
                "measurement_method": "Monthly campaign_choice_adoption + NIR vs months 7–12",
                "measurement_window": "2026-01 to 2026-07",
                "result_classification": "Successful",
            },
            {
                "action_id": "ACT-MDL-001",
                "related_insight_id": "INS-001",
                "category": "Model action",
                "original_suggestion": (
                    "Evaluate feature influence near the New Season Edit versus Performance Collection treatment "
                    "boundary, particularly recent product-category engagement, prior campaign response, and purchase channel."
                ),
                "human_reviewed_text": (
                    "Ship v1.1 with recalibrated boundary emphasis on performance_affinity, prior_campaign_response, "
                    "and channel effects for Performance Collection."
                ),
                "owner": "Sam Ortiz (Data Science)",
                "status": "Successful",
                "created_at": "2025-12-03",
                "implemented_at": "2026-01-28",
                "expected_effect": "Fewer ambiguous New Season vs Performance scores; better adopted conversion",
                "measurement_method": "v1.0 vs v1.1 adopted conversion and exact-match rate",
                "measurement_window": "2026-02 to 2026-07",
                "result_classification": "Successful",
            },
            {
                "action_id": "ACT-BIZ-002",
                "related_insight_id": "INS-003",
                "category": "Business action",
                "original_suggestion": (
                    "Stand up a dedicated follow-up completion checklist for At-Risk customers with recommended follow-ups."
                ),
                "human_reviewed_text": (
                    "Pilot a follow-up checklist for At-Risk recommended follow-ups in two regions."
                ),
                "owner": "Jordan Blake (Marketing Ops)",
                "status": "Inconclusive",
                "created_at": "2026-02-14",
                "implemented_at": "2026-02-20",
                "expected_effect": "Follow-up adoption +15 pts with clear NIR lift",
                "measurement_method": "Follow-up adoption and follow-up-attributed NIR",
                "measurement_window": "2026-03 to 2026-05",
                "result_classification": "Inconclusive",
            },
            {
                "action_id": "ACT-DATA-001",
                "related_insight_id": "INS-001",
                "category": "Data action",
                "original_suggestion": (
                    "Capture substitution reason codes as a first-class field for future adoption diagnostics."
                ),
                "human_reviewed_text": (
                    "Add mandatory substitution reason codes to the campaign worksheet export."
                ),
                "owner": "Sam Ortiz (Data Science)",
                "status": "Implemented",
                "created_at": "2025-12-10",
                "implemented_at": "2026-01-10",
                "expected_effect": "Improved Pareto diagnostics for modified recommendations",
                "measurement_method": "Reason-code completeness rate",
                "measurement_window": "2026-01 to 2026-03",
                "result_classification": "Successful",
            },
        ]
    )

    measurements = pd.DataFrame(
        [
            {
                "measurement_id": "MEAS-001",
                "action_id": "ACT-BIZ-001",
                "metric": "campaign_choice_adoption",
                "before_value": float(pre_adopt),
                "after_value": float(post_adopt),
                "before_window": "2024-08 to 2025-07",
                "after_window": "2026-01 to 2026-07",
                "actual_effect": float(delta_adopt),
                "result_classification": "Successful",
                "notes": "Business default-plan action; overlaps partially with later model change.",
            },
            {
                "measurement_id": "MEAS-002",
                "action_id": "ACT-BIZ-001",
                "metric": "net_incremental_revenue_monthly_mean",
                "before_value": float(pre_nir),
                "after_value": float(post_nir),
                "before_window": "2024-08 to 2025-07",
                "after_window": "2026-01 to 2026-07",
                "actual_effect": float(delta_nir),
                "result_classification": "Successful",
                "notes": "Simulated financial effect; not a claim of real-world revenue.",
            },
            {
                "measurement_id": "MEAS-003",
                "action_id": "ACT-MDL-001",
                "metric": "adopted_conversion_rate",
                "before_value": float(
                    monthly.loc[monthly["model_version"] == "v1.0", "conversion_rate"].mean()
                ),
                "after_value": float(
                    monthly.loc[monthly["model_version"] == "v1.1", "conversion_rate"].mean()
                ),
                "before_window": "v1.0 runs",
                "after_window": "v1.1 runs",
                "actual_effect": float(
                    monthly.loc[monthly["model_version"] == "v1.1", "conversion_rate"].mean()
                    - monthly.loc[monthly["model_version"] == "v1.0", "conversion_rate"].mean()
                ),
                "result_classification": "Successful",
                "notes": "Partial identification vs concurrent business process change.",
            },
            {
                "measurement_id": "MEAS-004",
                "action_id": "ACT-BIZ-002",
                "metric": "followup_adoption",
                "before_value": float(pre["followup_adoption"].mean()),
                "after_value": float(monthly.loc[monthly["phase"] == "improved", "followup_adoption"].mean()),
                "before_window": "2024-08 to 2025-07",
                "after_window": "2026-03 to 2026-05",
                "actual_effect": float(
                    monthly.loc[monthly["phase"] == "improved", "followup_adoption"].mean()
                    - pre["followup_adoption"].mean()
                ),
                "result_classification": "Inconclusive",
                "notes": "Adoption moved, but incremental revenue separation was weak.",
            },
        ]
    )

    return outliers_df, exceptions, insights, reviews, measurements, actions, monthly


def validate(artifacts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(ok), "detail": detail})

    for table in (
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
    ):
        add(f"table_exists:{table}", table in artifacts and len(artifacts[table]) > 0, f"rows={len(artifacts.get(table, []))}")

    runs = artifacts["model_runs"]
    add("run_count_24", len(runs) == 24, f"count={len(runs)}")
    add(
        "decision_ids_unique",
        artifacts["decisions"]["decision_id"].is_unique,
        "decision_id uniqueness",
    )
    classes = set(artifacts["decisions"]["execution_class"].unique())
    add(
        "execution_classes_valid",
        classes.issubset(set(EXECUTION_CLASSES)),
        f"classes={sorted(classes)}",
    )
    add(
        "no_negative_messages",
        (artifacts["monthly_kpis"]["messages_sent"] >= 0).all(),
        "messages_sent >= 0",
    )
    add(
        "conversion_bounds",
        artifacts["decisions"]["converted"].isin([0, 1]).all(),
        "converted in {0,1}",
    )
    add(
        "versions_present",
        set(artifacts["model_versions"]["model_version"]) >= {"v1.0", "v1.1"},
        "v1.0 and v1.1",
    )
    # Reconciliation: sum of decision NIR ~ monthly NIR
    recon = (
        artifacts["decisions"]
        .groupby("run_id")["net_incremental_revenue"]
        .sum()
        .reset_index()
        .merge(artifacts["monthly_kpis"][["run_id", "net_incremental_revenue"]], on="run_id")
    )
    recon_ok = np.allclose(
        recon["net_incremental_revenue_x"], recon["net_incremental_revenue_y"], rtol=1e-6
    )
    add("nir_reconciliation", recon_ok, "monthly NIR equals decision sum")

    return pd.DataFrame(checks)


def main() -> None:
    rng = _rng()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    source_note = {
        "choice": "Option B — synthetic fallback",
        "reason": (
            "Hillstrom was not required as a runtime dependency; synthetic data provides a "
            "reproducible offline demo inspired by uplift-marketing structure."
        ),
        "generated_at": pd.Timestamp("2026-07-22").strftime("%Y-%m-%d"),
        "seed": SEED,
        "brand": BRAND,
        "product": PRODUCT_NAME,
        "disclosure": DISCLOSURE,
    }
    (RAW_DIR / "SOURCE.md").write_text(
        "# Data source\n\n"
        f"- Choice: {source_note['choice']}\n"
        f"- Access date: {source_note['generated_at']}\n"
        f"- Seed: {SEED}\n\n"
        f"{DISCLOSURE}\n",
        encoding="utf-8",
    )
    (RAW_DIR / "source_manifest.json").write_text(json.dumps(source_note, indent=2), encoding="utf-8")

    print("Building customers...")
    customers = build_customers(rng)
    print("Fitting T-learners...")
    models_v10, models_v11, feature_influence = fit_t_learner(customers, rng)

    model_versions = pd.DataFrame(
        [
            {
                "model_version": "v1.0",
                "status": "Retired",
                "trained_on": "Synthetic A.Typical panel (seed 42)",
                "method": "T-learner · logistic regression per treatment",
                "treatments": ", ".join(PRIMARY_TREATMENTS),
                "feature_influence_methods": "Standardized coefficient; Permutation importance",
                "change_notes": "Initial production treatment-selection model.",
                "primary_metric_notes": "Selected treatment maximizes expected net value vs suppression.",
            },
            {
                "model_version": "v1.1",
                "status": "Production",
                "trained_on": "Synthetic A.Typical panel with boundary recalibration (seed 42)",
                "method": "T-learner · logistic regression per treatment",
                "treatments": ", ".join(PRIMARY_TREATMENTS),
                "feature_influence_methods": "Standardized coefficient; Permutation importance",
                "change_notes": (
                    "Recalibrated New Season Edit vs Performance Collection boundary using "
                    "performance_affinity, prior response, and channel signals."
                ),
                "primary_metric_notes": "Improved exact-match adoption quality after Dec 2025 business action.",
            },
        ]
    )

    decision_frames = []
    run_rows = []
    for month_idx, period in enumerate(RUN_MONTHS):
        run_id = f"RUN-{period.strftime('%Y%m')}"
        version = _model_version(month_idx)
        models = models_v11 if version == "v1.1" else models_v10
        # Score ~1000 eligible customers per run
        eligible = customers.sample(n=1600, random_state=SEED + month_idx)
        scored_customers = eligible.sample(n=1000, random_state=SEED + 100 + month_idx)
        scored = score_customers(scored_customers, models, version)
        executed = simulate_execution(scored, scored_customers, month_idx, rng)
        outcomes = simulate_outcomes(executed, month_idx, rng)
        outcomes.insert(0, "decision_id", [f"{run_id}-{cid}" for cid in outcomes["customer_id"]])
        outcomes.insert(1, "run_id", run_id)
        outcomes.insert(2, "run_month", str(period))
        outcomes.insert(3, "run_date", period.to_timestamp().strftime("%Y-%m-%d"))

        outside = classify_outside_pool(
            customers, set(scored_customers["customer_id"]), month_idx, run_id, rng
        )
        full = pd.concat([outcomes, outside], ignore_index=True)
        decision_frames.append(full)

        run_rows.append(
            {
                "run_id": run_id,
                "run_month": str(period),
                "run_date": period.to_timestamp().strftime("%Y-%m-%d"),
                "model_version": version,
                "phase": _phase(month_idx),
                "status": "Completed",
                "eligible_customers": len(eligible),
                "records_scored": len(scored_customers),
                "batch_schedule": "Monthly · first business Monday",
            }
        )
        print(f"  scored {run_id} ({version})")

    decisions = pd.concat(decision_frames, ignore_index=True)
    model_runs = pd.DataFrame(run_rows)
    monthly = compute_monthly_kpis(decisions, model_runs)
    (
        outliers,
        exceptions,
        insights,
        reviews,
        measurements,
        actions,
        monthly,
    ) = build_outliers_and_insights(monthly)

    feature_dictionary = pd.DataFrame(FEATURE_DEFINITIONS)

    artifacts = {
        "model_versions": model_versions,
        "model_runs": model_runs,
        "customers": customers,
        "decisions": decisions,
        "monthly_kpis": monthly,
        "feature_influence": feature_influence,
        "feature_dictionary": feature_dictionary,
        "business_exceptions": exceptions,
        "statistical_outliers": outliers,
        "generated_insights": insights,
        "human_insight_reviews": reviews,
        "suggested_actions": actions,
        "action_measurements": measurements,
    }
    validation = validate(artifacts)
    artifacts["validation_report"] = validation

    for name, df in artifacts.items():
        path = OUT_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"Wrote {path} ({len(df)} rows)")

    failed = validation[~validation["passed"]]
    if len(failed):
        print("VALIDATION FAILURES:")
        print(failed.to_string(index=False))
        raise SystemExit(1)
    print("All validation checks passed.")


if __name__ == "__main__":
    main()
