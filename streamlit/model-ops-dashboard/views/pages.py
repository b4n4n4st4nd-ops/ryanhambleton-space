"""Transparensea product views — polished visual experience."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from analytics.adoption import ADOPTION_LABELS, decision_class_summary, pareto_gap, pchart_limits
from analytics.financials import aggregate_financials, methodology_markdown
from charts.product_charts import (
    class_outcome_bars,
    control_chart,
    heatmap,
    horizontal_rank_bar,
    metric_trend,
    px_hist,
    rates_trend,
    revenue_trend,
    stacked_class_bar,
    volume_lines,
    pareto_chart,
)
from components.styles import COLORS
from components.ui import (
    action_card,
    chart_container,
    disclosure,
    empty_state,
    fmt_int,
    fmt_money,
    fmt_pct,
    insight_card,
    kpi_primary,
    kpi_secondary,
    methodology_drawer,
    page_heading,
    section_heading,
    status_badge,
    table_container,
)


def _status_kind(status: str) -> str:
    s = (status or "").lower()
    if s in {"successful", "confirmed", "ok", "production"}:
        return "ok"
    if s in {"inconclusive", "under review", "measuring", "warn", "high"}:
        return "warn"
    if s in {"unsuccessful", "rejected", "crit"}:
        return "crit"
    return "info"


def render_overview(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Overview",
        "Commercial performance of the A.Typical treatment-selection model — adoption, conversion, and value.",
    )
    monthly = data["monthly_kpis"].sort_values("run_date").reset_index(drop=True)
    decisions = data["decisions"]
    if monthly.empty:
        empty_state("No runs in the selected date window.")
        return

    latest = monthly.iloc[-1]
    prior = monthly.iloc[-2] if len(monthly) > 1 else latest
    insight = data["generated_insights"].iloc[0]
    actions = data["suggested_actions"]
    biz = actions[actions["category"] == "Business action"].iloc[0]
    mdl = actions[actions["category"] == "Model action"].iloc[0]
    version = (
        data["model_versions"].loc[data["model_versions"]["status"] == "Production", "model_version"].iloc[0]
    )

    def _dir(curr: float, prev: float, higher_better: bool = True) -> str:
        if curr == prev:
            return "flat"
        better = curr > prev if higher_better else curr < prev
        return "up" if better else "down"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        kpi_primary(
            "Campaign-choice adoption",
            fmt_pct(latest["campaign_choice_adoption"]),
            f"{fmt_pct(latest['campaign_choice_adoption'] - prior['campaign_choice_adoption'], 1)} vs prior month",
            "Exact-match execution of recommended campaigns",
            _dir(latest["campaign_choice_adoption"], prior["campaign_choice_adoption"]),
        ),
        unsafe_allow_html=True,
    )
    c2.markdown(
        kpi_primary(
            "Conversion rate",
            fmt_pct(latest["conversion_rate"]),
            f"{fmt_pct(latest['conversion_rate'] - prior['conversion_rate'], 1)} vs prior month",
            "Observed conversions in latest completed run",
            _dir(latest["conversion_rate"], prior["conversion_rate"]),
        ),
        unsafe_allow_html=True,
    )
    c3.markdown(
        kpi_primary(
            "Net incremental revenue",
            fmt_money(monthly["net_incremental_revenue"].sum()),
            f"Latest month {fmt_money(latest['net_incremental_revenue'])}",
            "Simulated value across selected window",
            _dir(latest["net_incremental_revenue"], prior["net_incremental_revenue"]),
        ),
        unsafe_allow_html=True,
    )
    missed_dir = _dir(latest["missed_value"], prior["missed_value"], higher_better=False)
    c4.markdown(
        kpi_primary(
            "Estimated missed value",
            fmt_money(monthly["missed_value"].sum()),
            f"Latest month {fmt_money(latest['missed_value'])}",
            "Opportunity from modified/ignored recommendations",
            missed_dir,
        ),
        unsafe_allow_html=True,
    )

    section_heading("Context", "Supporting operating metrics")
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(kpi_secondary("Customers scored", fmt_int(monthly["customers_scored"].sum())), unsafe_allow_html=True)
    s2.markdown(kpi_secondary("Production coverage", fmt_pct(latest["production_coverage"]), "Latest run"), unsafe_allow_html=True)
    s3.markdown(kpi_secondary("Follow-up adoption", fmt_pct(latest["followup_adoption"]), "Latest run"), unsafe_allow_html=True)
    s4.markdown(kpi_secondary("Current model", version, "Production"), unsafe_allow_html=True)

    section_heading("Historical trend", "Intervention markers: Dec 2025 business action · Feb 2026 model v1.1")
    if hasattr(st, "pills"):
        metric = st.pills(
            "Primary trend metric",
            [
                "Adoption & conversion",
                "Net incremental revenue",
                "Campaign-choice adoption only",
                "Conversion only",
            ],
            selection_mode="single",
            default="Adoption & conversion",
            label_visibility="collapsed",
            key="ov_metric_pills",
        ) or "Adoption & conversion"
    else:
        metric = st.radio(
            "Primary trend metric",
            [
                "Adoption & conversion",
                "Net incremental revenue",
                "Campaign-choice adoption only",
                "Conversion only",
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="ov_metric_radio",
        )
    if metric == "Adoption & conversion":
        left, right = st.columns(2, gap="medium")
        with left:
            chart_container(rates_trend(monthly), key="ov_rates", title="Adoption and conversion")
        with right:
            chart_container(revenue_trend(monthly), key="ov_rev", title="Net incremental revenue")
    elif metric == "Net incremental revenue":
        chart_container(revenue_trend(monthly), key="ov_rev_only", title="Net incremental revenue")
    elif metric == "Campaign-choice adoption only":
        chart_container(
            metric_trend(monthly, "campaign_choice_adoption", "Campaign-choice adoption", COLORS["adoption"]),
            key="ov_adopt",
            title="Campaign-choice adoption",
        )
    else:
        chart_container(
            metric_trend(monthly, "conversion_rate", "Conversion rate", COLORS["conversion"]),
            key="ov_conv",
            title="Conversion rate",
        )

    section_heading("Active insight")
    outlier_note = ""
    if len(data["statistical_outliers"]):
        ol = data["statistical_outliers"].iloc[0]
        outlier_note = f"Related outlier: {ol['outlier_id']} · Open Exceptions to inspect evidence."
    st.markdown(
        insight_card(
            insight["title"],
            "Recurring Performance Collection substitutions in Midwest/Southwest suburban segments reduced adoption quality and net value until process and model interventions.",
            [
                ("Pre adoption", fmt_pct(monthly.loc[monthly["phase"].isin(["initial", "recurring"]), "campaign_choice_adoption"].mean()) if len(monthly) else "—"),
                ("Post adoption", fmt_pct(monthly.loc[monthly["phase"] == "improved", "campaign_choice_adoption"].mean()) if (monthly["phase"] == "improved").any() else "—"),
                ("Evidence", insight["evidence_strength"]),
            ],
            f"{insight['status']} · {insight['evidence_strength']}",
            _status_kind(insight["status"]),
            detail="Full generated narrative and methodology live on Insights & Actions.",
            link_note=outlier_note,
        ),
        unsafe_allow_html=True,
    )

    section_heading("Recommended actions")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown(
            action_card(
                "Business action",
                biz["status"],
                biz["owner"],
                biz["human_reviewed_text"],
                biz["expected_effect"],
                f"Implemented {biz['implemented_at']} · {biz['result_classification']}",
                biz["related_insight_id"],
                "",
                _status_kind(biz["result_classification"]),
            ),
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            action_card(
                "Model action",
                mdl["status"],
                mdl["owner"],
                mdl["human_reviewed_text"],
                mdl["expected_effect"],
                f"Implemented {mdl['implemented_at']} · {mdl['result_classification']}",
                mdl["related_insight_id"],
                "model",
                _status_kind(mdl["result_classification"]),
            ),
            unsafe_allow_html=True,
        )

    section_heading("Supporting visuals")
    v1, v2 = st.columns(2)
    with v1:
        mix = decisions["recommended_campaign"].value_counts().reset_index()
        mix.columns = ["campaign", "count"]
        chart_container(horizontal_rank_bar(mix, "campaign", "count", "Recommended campaign mix", COLORS["recommend"], "int"), key="ov_mix", title="Recommended campaign mix")
    with v2:
        reg = (
            decisions.groupby("region", as_index=False)["net_incremental_revenue"]
            .sum()
            .sort_values("net_incremental_revenue", ascending=False)
        )
        chart_container(
            horizontal_rank_bar(reg, "region", "net_incremental_revenue", "Regional net incremental revenue", COLORS["sea"], "money"),
            key="ov_reg",
            title="Regional net incremental revenue",
        )
    chart_container(stacked_class_bar(decisions["execution_class"].value_counts()), key="ov_class", title="Decision classifications")
    disclosure()


def render_input_transparency(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Inputs",
        "Feature Influence for the treatment-selection models — methods are not interchangeable.",
    )
    feats = data["feature_dictionary"]
    infl = data["feature_influence"]
    decisions = data["decisions"]

    c1, c2, c3 = st.columns(3)
    method = c1.selectbox("Feature Influence method", ["Standardized coefficient", "Permutation importance"])
    version = c2.selectbox("Model version", ["v1.0", "v1.1"])
    treatment = c3.selectbox("Treatment model", ["New Season Edit", "Performance Collection", "Suppression"])

    view = infl[
        (infl["method"] == method)
        & (infl["model_version"] == version)
        & (infl["treatment"] == treatment)
    ].copy()
    view["abs_importance"] = view["importance"].abs()
    view = view.sort_values("abs_importance", ascending=False)

    left, right = st.columns([1.15, 1])
    with left:
        section_heading("Feature catalog", f"Method in view: {method}")
        q = st.text_input("Search features", "", placeholder="e.g. performance affinity")
        table = feats.merge(
            view[["feature", "importance", "method", "direction_note"]],
            on="feature",
            how="left",
        )
        table["influence_level"] = pd.cut(
            table["importance"].abs().fillna(0),
            bins=[-0.01, 0.02, 0.05, 1.0, 100],
            labels=["Low", "Medium", "High", "Very high"],
        )
        table["direction"] = table["importance"].apply(
            lambda x: "—" if pd.isna(x) else ("Increases" if x > 0 else "Decreases")
        )
        if q:
            mask = table["feature"].str.contains(q, case=False) | table["definition"].str.contains(q, case=False)
            table = table[mask]
        show = table[
            ["feature", "definition", "data_type", "influence_level", "direction", "method", "importance"]
        ].rename(columns={"importance": "score"})
        table_container(show, height=360)

        feature = st.selectbox("Selected feature", show["feature"].tolist() if len(show) else ["tenure_months"])

    with right:
        section_heading("Selected feature detail")
        row = table[table["feature"] == feature]
        if row.empty:
            empty_state("Select a feature to inspect.")
        else:
            r = row.iloc[0]
            compare = infl[
                (infl["feature"] == feature)
                & (infl["treatment"] == treatment)
                & (infl["method"] == method)
            ]
            st.markdown(
                f"""
                <div class="ts-card">
                  <h3>{feature}</h3>
                  <p class="body">{r.get('definition', '')}</p>
                  <div class="ts-evidence-row">
                    <div class="ts-evidence"><span class="k">Influence</span><span class="v">{r.get('influence_level', '—')}</span></div>
                    <div class="ts-evidence"><span class="k">Direction</span><span class="v">{r.get('direction', '—')}</span></div>
                    <div class="ts-evidence"><span class="k">Score</span><span class="v">{r.get('importance', float('nan')):.3f}</span></div>
                  </div>
                  <div class="ts-field-k">Method</div>
                  <p class="ts-field-v">{method}</p>
                  <div class="ts-field-k">Interpretation</div>
                  <p class="ts-field-v">{r.get('direction_note', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if feature in decisions.columns and pd.api.types.is_numeric_dtype(decisions[feature]):
                chart_container(px_hist(decisions, feature, f"Current distribution · {feature}"), key="in_dist")
            if len(compare):
                cmp = compare.pivot_table(index="model_version", values="importance", aggfunc="mean").reset_index()
                chart_container(
                    horizontal_rank_bar(cmp, "model_version", "importance", "Model-version comparison", COLORS["ocean"]),
                    key="in_ver",
                )
            st.caption(
                "Natural-language summary: under the selected treatment model, this feature’s "
                f"{method.lower()} indicates a {str(r.get('direction', 'unclear')).lower()} relationship "
                "with predicted conversion. This is not causal proof."
            )

    methodology_drawer(
        "Methodology — Feature Influence methods",
        """
- **Standardized coefficient**: direction and relative magnitude inside a logistic model on scaled numeric inputs.
- **Permutation importance**: drop in predictive score when a feature is shuffled.
- **Statistical correlation** (if shown elsewhere): association only — not interchangeable with the above.
        """,
    )
    disclosure()


def render_recommendations(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Recommendations",
        "What the model recommended this period — audience mix, priority, and record-level investigation.",
    )
    d = data["decisions"]
    contact = d[d["recommended_campaign"] != "Suppression"]
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_primary("Recommendations", fmt_int(len(d)), interpretation="Scored decisions in view"), unsafe_allow_html=True)
    c2.markdown(kpi_primary("Recommended messages", fmt_int(len(contact)), interpretation="Non-suppression audience"), unsafe_allow_html=True)
    c3.markdown(kpi_primary("Suppressions", fmt_int((d["recommended_campaign"] == "Suppression").sum()), interpretation="No-contact recommendations"), unsafe_allow_html=True)
    c4.markdown(kpi_primary("Expected net value", fmt_money(d["estimated_net_value"].sum()), interpretation=f"Mean conversion {fmt_pct(d['predicted_conversion'].mean())}"), unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    s1.markdown(kpi_secondary("Follow-ups recommended", fmt_int(d["recommend_followup"].sum())), unsafe_allow_html=True)
    s2.markdown(kpi_secondary("Mean estimated uplift", fmt_pct(d["estimated_uplift"].mean())), unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        mix = d["recommended_campaign"].value_counts().reset_index()
        mix.columns = ["campaign", "audience"]
        chart_container(horizontal_rank_bar(mix, "campaign", "audience", "Recommended audience by campaign", COLORS["recommend"], "int"), key="rec_mix", title="Recommended audience by campaign")
    with right:
        chart_container(px_hist(contact if len(contact) else d, "priority_score", "Priority-score distribution"), key="rec_pri", title="Priority-score distribution")

    section_heading("Segment breakdown")
    seg = (
        contact.groupby("segment", as_index=False)
        .agg(customers=("decision_id", "count"), expected_net=("estimated_net_value", "sum"))
        .sort_values("customers", ascending=False)
    )
    table_container(seg)

    section_heading("Record-level investigation")
    cols_show = [
        "customer_id",
        "run_month",
        "region",
        "segment",
        "recommended_campaign",
        "priority_score",
        "predicted_conversion",
        "estimated_net_value",
        "actual_campaign",
        "execution_class",
        "converted",
        "gross_revenue",
    ]
    sample = d[cols_show].sort_values("priority_score", ascending=False)
    q = st.text_input("Search customer ID", "")
    if q:
        sample = sample[sample["customer_id"].str.contains(q, case=False)]
    page_size = st.selectbox("Rows", [20, 40, 80], index=0)
    max_page = max(1, (len(sample) - 1) // page_size + 1)
    page = st.number_input("Page", min_value=1, max_value=max_page, value=1)
    start = (page - 1) * page_size
    page_df = sample.iloc[start : start + page_size]
    table_container(page_df, height=320)

    if len(page_df):
        pick = st.selectbox("Customer detail", page_df["customer_id"].tolist())
        row = d[d["customer_id"] == pick].iloc[0]
        st.markdown(
            f"""
            <div class="ts-card">
              <h3>{pick}</h3>
              <div class="ts-evidence-row">
                <div class="ts-evidence"><span class="k">Recommended</span><span class="v">{row['recommended_campaign']}</span></div>
                <div class="ts-evidence"><span class="k">Actual</span><span class="v">{row['actual_campaign']}</span></div>
                <div class="ts-evidence"><span class="k">Class</span><span class="v">{row['execution_class']}</span></div>
                <div class="ts-evidence"><span class="k">Converted</span><span class="v">{'Yes' if row['converted'] else 'No'}</span></div>
              </div>
              <p class="body">Priority {row['priority_score']:.2f} · predicted conversion {fmt_pct(row['predicted_conversion'])} ·
              estimated net {fmt_money(row['estimated_net_value'], 2)} · revenue {fmt_money(row['gross_revenue'], 2)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    disclosure()


def render_adoption(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Adoption",
        "Flagship control-chart and Pareto investigation of whether the business followed the model.",
    )
    monthly = data["monthly_kpis"].reset_index(drop=True)
    decisions = data["decisions"]
    if monthly.empty:
        empty_state("No runs in the selected date window.")
        return

    kpi_keys = list(ADOPTION_LABELS.keys())
    if hasattr(st, "pills"):
        kpi_label = st.pills(
            "Adoption KPI",
            [ADOPTION_LABELS[k] for k in kpi_keys],
            selection_mode="single",
            default=ADOPTION_LABELS["campaign_choice_adoption"],
            label_visibility="collapsed",
            key="ad_kpi_pills",
        ) or ADOPTION_LABELS["campaign_choice_adoption"]
        kpi = next(k for k, v in ADOPTION_LABELS.items() if v == kpi_label)
    else:
        kpi = st.selectbox(
            "Adoption KPI",
            kpi_keys,
            format_func=lambda k: ADOPTION_LABELS[k],
            index=kpi_keys.index("campaign_choice_adoption"),
        )
    n = monthly["recommended_messages"] if "message" in kpi or "campaign" in kpi or "priority" in kpi or "customer_selection" in kpi else monthly["customers_scored"]
    limits = pchart_limits(monthly[kpi].fillna(monthly[kpi].mean()), n.clip(lower=1))

    section_heading("Control chart", "p-chart with 3σ limits weighted by opportunity volume. Clay markers: interventions.")
    chart_container(control_chart(monthly, ADOPTION_LABELS[kpi], limits), key="ad_ctrl", title=f"Control chart · {ADOPTION_LABELS[kpi]}")
    methodology_drawer(
        "Control-chart methodology",
        """
Uses a **p-chart** for proportion metrics. Centerline is the weighted average rate; UCL/LCL are ±3σ under a binomial assumption with sample size = opportunity volume for that month.
Outliers are months below the lower control limit (or the weakest months if limits are quiet).
        """,
    )

    outlier_months = monthly.loc[limits["outlier"].to_numpy(), "run_month"].tolist()
    if not outlier_months:
        outlier_months = monthly.nsmallest(3, "campaign_choice_adoption")["run_month"].tolist()
    selected_month = st.selectbox(
        "Focus month (updates Pareto and drill-down)",
        options=monthly["run_month"].tolist(),
        index=monthly["run_month"].tolist().index(outlier_months[0])
        if outlier_months and outlier_months[0] in monthly["run_month"].tolist()
        else 0,
    )
    month_row = monthly[monthly["run_month"] == selected_month].iloc[0]
    st.markdown(
        f"""
        <div class="ts-card">
          <h3>Selected month · {selected_month}</h3>
          <div class="ts-evidence-row">
            <div class="ts-evidence"><span class="k">KPI</span><span class="v">{fmt_pct(month_row[kpi])}</span></div>
            <div class="ts-evidence"><span class="k">Phase</span><span class="v">{month_row['phase']}</span></div>
            <div class="ts-evidence"><span class="k">Model</span><span class="v">{month_row['model_version']}</span></div>
            <div class="ts-evidence"><span class="k">Missed value</span><span class="v">{fmt_money(month_row['missed_value'])}</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_heading("Pareto contributor analysis")
    dim = st.selectbox(
        "Pareto dimension",
        ["region", "state", "market_type", "segment", "primary_channel", "model_version", "recommended_campaign"],
    )
    month_decisions = decisions[decisions["run_month"] == selected_month]
    pareto = pareto_gap(month_decisions, dim)
    if pareto.empty:
        empty_state("No contributors for this slice.")
    else:
        chart_container(pareto_chart(pareto, dim), key="ad_pareto", title=f"Pareto of adoption misses by {dim}")
        contributor = st.selectbox("Selected contributor", pareto[dim].astype(str).tolist())
        drill = month_decisions[month_decisions[dim].astype(str) == contributor].copy()
        drill["why"] = drill["execution_class"].map(
            {
                "Adopted": "Business sent the recommended campaign to the recommended customer.",
                "Modified": "Recommended customer received a different campaign.",
                "Ignored": "Recommended customer received no communication.",
                "Outside recommendation": "Business contacted a customer outside the recommendation set.",
                "Suppression adopted": "Model recommended no contact and none was sent.",
                "Suppression rejected": "Model recommended no contact but a campaign was sent.",
            }
        )
        section_heading("Lowest-grain records", f"{dim} = {contributor} · {selected_month}")
        table_container(
            drill[
                [
                    "customer_id",
                    "recommended_campaign",
                    "actual_campaign",
                    "execution_class",
                    "why",
                    "converted",
                    "gross_revenue",
                    "net_incremental_revenue",
                ]
            ].head(100),
            height=300,
        )

    section_heading("Segment heatmap")
    chart_container(heatmap(decisions), key="ad_heat", title="Exact-match rate by segment × campaign")
    chart_container(volume_lines(monthly), key="ad_vol", title="Recommended vs executed message volume")
    disclosure()


def render_conversion_revenue(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Impact",
        "Adopted vs modified vs ignored performance — conversion and simulated net incremental revenue.",
    )
    monthly = data["monthly_kpis"]
    decisions = data["decisions"]
    grain = st.selectbox("Period aggregation", ["monthly", "quarterly", "retail-season", "yearly"])
    agg = aggregate_financials(monthly, grain)

    summary = decision_class_summary(decisions)
    section_heading("Decision-group comparison", "Primary commercial contrast for Transparensea")
    display = summary.rename(
        columns={
            "execution_class": "Group",
            "customers": "Customers",
            "messages": "Msgs",
            "conversion_rate": "Conv.",
            "incremental_conversion_rate": "Inc. conv.",
            "net_incremental_revenue": "Net incr. rev.",
            "missed_value": "Missed",
            "wasted_spend": "Wasted",
            "revenue_per_message": "Rev / msg",
        }
    )[
        [
            "Group",
            "Customers",
            "Msgs",
            "Conv.",
            "Inc. conv.",
            "Net incr. rev.",
            "Missed",
            "Wasted",
            "Rev / msg",
        ]
    ]
    for col in ["Conv.", "Inc. conv."]:
        display[col] = display[col].map(lambda x: fmt_pct(x))
    for col in ["Net incr. rev.", "Missed", "Wasted", "Rev / msg"]:
        display[col] = display[col].map(lambda x: fmt_money(x))
    display["Customers"] = display["Customers"].map(fmt_int)
    display["Msgs"] = display["Msgs"].map(fmt_int)
    table_container(display)

    left, right = st.columns(2)
    with left:
        chart_container(
            class_outcome_bars(summary, "conversion_rate", "Conversion by decision group", "pct"),
            key="im_conv",
            title="Conversion by decision group",
        )
    with right:
        chart_container(
            class_outcome_bars(summary, "net_incremental_revenue", "Net incremental revenue by group", "money"),
            key="im_nir",
            title="Net incremental revenue by group",
        )

    section_heading("Trends")
    t1, t2 = st.columns(2)
    with t1:
        chart_container(
            metric_trend(agg.rename(columns={"period": "run_month"}), "conversion_rate", f"Conversion · {grain}", COLORS["conversion"])
            if "conversion_rate" in agg
            else rates_trend(monthly),
            key="im_trend_c",
            title=f"Conversion · {grain}",
        )
    with t2:
        if grain == "monthly":
            chart_container(revenue_trend(monthly), key="im_trend_r", title="Net incremental revenue")
        else:
            chart_container(
                horizontal_rank_bar(agg, "period", "net_incremental_revenue", f"NIR · {grain}", COLORS["revenue"], "money"),
                key="im_trend_r2",
                title=f"Net incremental revenue · {grain}",
            )

    section_heading("Recommended vs actual campaign matrix")
    matrix = pd.crosstab(decisions["recommended_campaign"], decisions["actual_campaign"])
    table_container(matrix)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(kpi_secondary("Missed value", fmt_money(decisions["missed_value"].sum())), unsafe_allow_html=True)
    m2.markdown(kpi_secondary("Wasted spend", fmt_money(decisions["wasted_spend"].sum())), unsafe_allow_html=True)
    m3.markdown(kpi_secondary("Gross revenue", fmt_money(decisions["gross_revenue"].sum())), unsafe_allow_html=True)
    m4.markdown(kpi_secondary("Campaign cost", fmt_money(decisions["campaign_cost"].sum())), unsafe_allow_html=True)

    methodology_drawer("Financial methodology", methodology_markdown())
    disclosure()


def render_exceptions(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Exceptions",
        "Statistical outliers and recorded business exceptions that affect interpretation.",
    )
    outliers = data["statistical_outliers"].copy()
    exceptions = data["business_exceptions"].copy()
    outliers["issue_type"] = "Statistical outlier"
    exceptions["issue_type"] = "Business exception"
    outliers_list = outliers.rename(columns={"outlier_id": "issue_id"})
    exceptions_list = exceptions.rename(columns={"exception_id": "issue_id"})
    cols = [
        "issue_id",
        "issue_type",
        "timestamp",
        "scope",
        "metric",
        "actual_value",
        "severity",
        "status",
        "evidence",
        "related_insight_id",
        "related_action_id",
    ]
    for frame in (outliers_list, exceptions_list):
        for c in cols:
            if c not in frame.columns:
                frame[c] = ""
    issues = pd.concat([outliers_list[cols], exceptions_list[cols]], ignore_index=True)

    left, right = st.columns([1, 1.15])
    with left:
        section_heading("Issue list")
        kind = st.selectbox("Type", ["All", "Statistical outlier", "Business exception"])
        sev = st.selectbox("Severity", ["All"] + sorted(issues["severity"].dropna().unique().tolist()))
        q = st.text_input("Search issues", "")
        view = issues.copy()
        if kind != "All":
            view = view[view["issue_type"] == kind]
        if sev != "All":
            view = view[view["severity"] == sev]
        if q:
            view = view[view.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)]
        table_container(view[["issue_id", "issue_type", "severity", "status", "scope"]], height=360)
        selected = st.selectbox("Selected issue", view["issue_id"].tolist() if len(view) else ["—"])

    with right:
        section_heading("Issue detail")
        row = issues[issues["issue_id"] == selected]
        if row.empty:
            empty_state("Select an issue.")
        else:
            r = row.iloc[0]
            st.markdown(
                f"""
                <div class="ts-card">
                  <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                    <h3 style="margin:0;">{r['issue_id']}</h3>
                    {status_badge(str(r['severity']), _status_kind(str(r['severity'])))}
                  </div>
                  <div class="ts-field-k">Type / source status</div>
                  <p class="ts-field-v">{r['issue_type']} · {r['status']}</p>
                  <div class="ts-field-k">Metric</div>
                  <p class="ts-field-v">{r['metric']}</p>
                  <div class="ts-field-k">Expected vs actual</div>
                  <p class="ts-field-v">{r.get('expected_range', r.get('expected_range', '—'))} → {r['actual_value']}</p>
                  <div class="ts-field-k">Evidence</div>
                  <p class="ts-field-v">{r['evidence']}</p>
                  <div class="ts-field-k">Related insight / action</div>
                  <p class="ts-field-v">{r['related_insight_id'] or '—'} · {r['related_action_id'] or '—'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    disclosure()


def render_insights_actions(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Insights & Actions",
        "Automated analytical insights preserved beside human review, with suggested actions for approval.",
    )
    insights = data["generated_insights"]
    reviews = data["human_insight_reviews"]
    actions = data["suggested_actions"]

    section_heading("Insights")
    for _, insight in insights.iterrows():
        review = reviews[reviews["insight_id"] == insight["insight_id"]]
        st.markdown(
            f"""
            <div class="ts-card" style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                <h3 style="margin:0;">{insight['insight_id']} · {insight['title']}</h3>
                {status_badge(insight['status'], _status_kind(insight['status']))}
              </div>
              <div class="ts-field-k">Original automated generation</div>
              <p class="ts-field-v">{insight['automated_text']}</p>
              <div class="ts-evidence-row">
                <div class="ts-evidence"><span class="k">Method</span><span class="v">{insight['method'][:42]}…</span></div>
                <div class="ts-evidence"><span class="k">Confidence</span><span class="v">{insight['evidence_strength']}</span></div>
                <div class="ts-evidence"><span class="k">Magnitude</span><span class="v">{insight['magnitude'][:32]}</span></div>
              </div>
              <div class="ts-field-k">Evidence dimensions</div>
              <p class="ts-field-v">{insight['contributing_dimensions']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if len(review):
            r = review.iloc[0]
            st.markdown(
                f"""
                <div class="ts-card" style="margin-bottom:14px;border-left:3px solid {COLORS['lime']};">
                  <h3>Human-reviewed version</h3>
                  <div class="ts-field-k">Reviewer</div>
                  <p class="ts-field-v">{r['reviewer']} · {r['reviewed_at']} · {r['status']}</p>
                  <div class="ts-field-k">Reviewed text</div>
                  <p class="ts-field-v">{r['human_edited_text']}</p>
                  <div class="ts-field-k">Edit reason</div>
                  <p class="ts-field-v">{r['edit_reason']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    section_heading("Suggested actions", "Not auto-approved — labeled for human review")
    cols = st.columns(2)
    for i, (_, action) in enumerate(actions.iterrows()):
        variant = "model" if "Model" in action["category"] else ("data" if "Data" in action["category"] else "")
        with cols[i % 2]:
            st.markdown(
                action_card(
                    action["category"],
                    action["status"],
                    action["owner"],
                    action["human_reviewed_text"],
                    action["expected_effect"],
                    f"{action['implemented_at']} · {action['measurement_window']} · {action['result_classification']}",
                    action["related_insight_id"],
                    variant,
                    _status_kind(action["result_classification"]),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="ts-caption" style="margin-bottom:12px;">
                  Original automated suggestion preserved: {action['original_suggestion']}
                </div>
                """,
                unsafe_allow_html=True,
            )
    disclosure()


def render_improvement_history(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Improvement",
        "Learning loop from insight through measurement — including successful and inconclusive outcomes.",
    )
    measures = data["action_measurements"].merge(
        data["suggested_actions"][
            ["action_id", "category", "human_reviewed_text", "status", "related_insight_id", "implemented_at"]
        ],
        on="action_id",
        how="left",
    )

    section_heading("Learning sequence")
    for _, m in measures.iterrows():
        st.markdown(
            f"""
            <div class="ts-timeline-step">
              <div class="step">Insight → Review → Action → Implementation → Measurement → Result</div>
              <strong>{m['action_id']}</strong> · {m['category']} · {status_badge(m['result_classification'], _status_kind(m['result_classification']))}
              <div class="ts-field-k">Action</div>
              <p class="ts-field-v">{m['human_reviewed_text']}</p>
              <div class="ts-evidence-row">
                <div class="ts-evidence"><span class="k">Metric</span><span class="v">{m['metric']}</span></div>
                <div class="ts-evidence"><span class="k">Before</span><span class="v">{m['before_value']:.3g}</span></div>
                <div class="ts-evidence"><span class="k">After</span><span class="v">{m['after_value']:.3g}</span></div>
                <div class="ts-evidence"><span class="k">Δ</span><span class="v">{m['actual_effect']:.3g}</span></div>
              </div>
              <div class="ts-caption">{m['before_window']} → {m['after_window']} · {m['notes']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    monthly = data["monthly_kpis"]
    chart_container(rates_trend(monthly), key="imp_rates")
    st.markdown(
        """
- **ACT-BIZ-001** business default plan — **Successful**
- **ACT-MDL-001** model v1.1 boundary — **Successful** (partially confounded)
- **ACT-BIZ-002** follow-up checklist — **Inconclusive**
        """
    )
    disclosure()


def render_model_details(data: dict[str, pd.DataFrame]) -> None:
    page_heading(
        "Model Details",
        "Product documentation for the A.Typical treatment-selection demonstration.",
    )
    versions = data["model_versions"]
    validation = data["validation_report"]

    section_heading("Model summary")
    st.markdown(
        f"""
        <div class="ts-card">
          <p class="body">The model estimates which marketing action is most likely to create an
          <strong>incremental</strong> customer response, rather than only predicting which customers
          are already likely to purchase.</p>
          <div class="ts-evidence-row">
            <div class="ts-evidence"><span class="k">Approach</span><span class="v">T-learner</span></div>
            <div class="ts-evidence"><span class="k">Learners</span><span class="v">Logistic</span></div>
            <div class="ts-evidence"><span class="k">Primary treatments</span><span class="v">3</span></div>
            <div class="ts-evidence"><span class="k">Schedule</span><span class="v">Monthly</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        section_heading("Model versions")
        table_container(versions)
        section_heading("Feature Influence methods")
        st.markdown(
            """
            <div class="ts-card">
              <div class="ts-field-k">Standardized coefficient</div>
              <p class="ts-field-v">Direction and magnitude in a scaled logistic model.</p>
              <div class="ts-field-k">Permutation importance</div>
              <p class="ts-field-v">Drop in predictive score when a feature is shuffled.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        section_heading("Adoption definitions")
        for key, label in ADOPTION_LABELS.items():
            st.markdown(f"- **{label}** (`{key}`)")
        methodology_drawer("Financial assumptions", methodology_markdown())

    section_heading("Validation status")
    passed = int(validation["passed"].sum())
    total = len(validation)
    st.markdown(
        f'{status_badge(f"{passed}/{total} checks passed", "ok" if passed == total else "warn")}',
        unsafe_allow_html=True,
    )
    table_container(validation)

    section_heading("Data disclosure & limitations")
    st.markdown(
        """
        <div class="ts-card">
          <div class="ts-field-k">Data</div>
          <p class="ts-field-v">Synthetic A.Typical panel (seed 42). Not Hillstrom runtime data.</p>
          <div class="ts-field-k">Known limitations</div>
          <p class="ts-field-v">Financial results are simulated. Business and model interventions overlap in time.
          Incremental revenue is a modeled estimate, not proven live causal attribution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    disclosure()
