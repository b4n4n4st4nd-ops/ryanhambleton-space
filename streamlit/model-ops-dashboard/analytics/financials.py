"""Financial methodology helpers."""

from __future__ import annotations

import pandas as pd

from data.schema import FINANCIAL_ASSUMPTIONS

PERIOD_MAP = {
    "monthly": None,
    "quarterly": "Q",
    "yearly": "Y",
}


def retail_season(month: int) -> str:
    if month in (1, 2, 3):
        return "Spring"
    if month in (4, 5, 6):
        return "Summer"
    if month in (7, 8, 9):
        return "Fall"
    return "Holiday"


def enrich_periods(monthly: pd.DataFrame) -> pd.DataFrame:
    out = monthly.copy()
    out["run_dt"] = pd.to_datetime(out["run_date"])
    out["year"] = out["run_dt"].dt.year
    out["quarter"] = out["run_dt"].dt.to_period("Q").astype(str)
    out["retail_season"] = out["run_dt"].dt.month.map(retail_season)
    return out


def aggregate_financials(monthly: pd.DataFrame, grain: str) -> pd.DataFrame:
    df = enrich_periods(monthly)
    if grain == "monthly":
        key = "run_month"
    elif grain == "quarterly":
        key = "quarter"
    elif grain == "retail-season":
        key = "retail_season"
    else:
        key = "year"
    agg = (
        df.groupby(key)
        .agg(
            conversion_rate=("conversion_rate", "mean"),
            net_incremental_revenue=("net_incremental_revenue", "sum"),
            gross_revenue=("gross_revenue", "sum"),
            campaign_cost=("campaign_cost", "sum"),
            missed_value=("missed_value", "sum"),
            wasted_spend=("wasted_spend", "sum"),
            messages_sent=("messages_sent", "sum"),
            campaign_choice_adoption=("campaign_choice_adoption", "mean"),
        )
        .reset_index()
        .rename(columns={key: "period"})
    )
    return agg


def methodology_markdown() -> str:
    a = FINANCIAL_ASSUMPTIONS
    costs = "\n".join(
        f"- {k}: ${v:.2f} per message" for k, v in a["campaign_cost_per_message"].items()
    )
    return f"""
### Financial methodology (simulated)

**Formula**  
`{a["formula"]}`

**Assumptions**
- Average order value: ${a["average_order_value"]:.2f}
- Gross margin: {a["gross_margin"]:.0%}
- Message cost: ${a["message_cost"]:.2f}
- Follow-up cost: ${a["followup_cost"]:.2f}
- Campaign allocated costs:
{costs}

Values labeled **estimated** or **simulated** are modeled for demonstration and are not real A.Typical financial results.
"""
