"""Reusable Transparensea UI shell and components."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from components.styles import PRODUCT_CSS
from data.loaders import load_all, product_meta


def inject_styles() -> None:
    st.markdown(PRODUCT_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading Transparensea demo data…")
def get_data() -> dict[str, pd.DataFrame]:
    return load_all()


def status_badge(text: str, kind: str = "info") -> str:
    return f'<span class="ts-badge {kind}">{text}</span>'


def kpi_primary(
    label: str,
    value: str,
    comparison: str = "",
    interpretation: str = "",
    direction: str = "flat",
) -> str:
    delta_class = {"up": "delta-up", "down": "delta-down"}.get(direction, "delta-flat")
    delta_html = f'<div class="{delta_class}">{comparison}</div>' if comparison else ""
    interp = f'<div class="interp">{interpretation}</div>' if interpretation else ""
    return f"""
    <div class="ts-kpi">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      {delta_html}
      {interp}
    </div>
    """


def kpi_secondary(label: str, value: str, subtext: str = "") -> str:
    sub = f'<div class="interp">{subtext}</div>' if subtext else ""
    return f"""
    <div class="ts-kpi secondary">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      {sub}
    </div>
    """


def page_heading(title: str, subtitle: str = "") -> None:
    st.markdown(f'<p class="ts-page-title">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="ts-page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def section_heading(title: str, caption: str = "") -> None:
    st.markdown(f'<p class="ts-section">{title}</p>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<p class="ts-caption">{caption}</p>', unsafe_allow_html=True)


def chart_container(fig, key: str | None = None, title: str | None = None) -> None:
    """Render a Plotly figure with an HTML title (never Plotly title)."""
    # Guard against Plotly title bleed / Streamlit empty-string title bugs.
    try:
        fig.layout.title = None
    except Exception:  # noqa: BLE001
        pass
    if title:
        st.markdown(f'<div class="ts-chart-title">{title}</div>', unsafe_allow_html=True)
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        config={
            "displayModeBar": False,
            "responsive": True,
            "displaylogo": False,
        },
    )


def table_container(df: pd.DataFrame, height: int | None = None) -> None:
    # Style via CSS on stDataFrame — do not wrap with open/close HTML (breaks nesting).
    # Streamlit ≥1.40 rejects height=None; omit the kwarg for auto height.
    kwargs: dict[str, Any] = {"use_container_width": True, "hide_index": True}
    if height is not None:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)


def empty_state(message: str) -> None:
    st.markdown(f'<div class="ts-empty">{message}</div>', unsafe_allow_html=True)


def insight_card(
    title: str,
    summary: str,
    evidence: list[tuple[str, str]],
    status: str,
    status_kind: str = "info",
    detail: str = "",
    link_note: str = "",
) -> str:
    ev = "".join(
        f'<div class="ts-evidence"><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in evidence
    )
    detail_html = f'<p class="body">{detail}</p>' if detail else ""
    link_html = f'<p class="ts-caption">{link_note}</p>' if link_note else ""
    return f"""
    <div class="ts-card">
      <div style="display:flex;justify-content:space-between;gap:8px;align-items:flex-start;flex-wrap:wrap;">
        <h3 style="margin:0;">{title}</h3>
        {status_badge(status, status_kind)}
      </div>
      <p class="body" style="margin-top:8px;">{summary}</p>
      <div class="ts-evidence-row">{ev}</div>
      {detail_html}
      {link_html}
    </div>
    """


def action_card(
    category: str,
    status: str,
    owner: str,
    statement: str,
    expected: str,
    impl_state: str,
    insight_link: str,
    variant: str = "",
    status_kind: str = "info",
) -> str:
    return f"""
    <div class="ts-action-card {variant}">
      <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
        <span class="ts-badge info">{category}</span>
        {status_badge(status, status_kind)}
      </div>
      <p class="ts-field-v" style="margin-top:10px;font-weight:600;">{statement}</p>
      <div class="ts-field-k">Owner</div><p class="ts-field-v">{owner}</p>
      <div class="ts-field-k">Expected effect</div><p class="ts-field-v">{expected}</p>
      <div class="ts-field-k">Implementation / review</div><p class="ts-field-v">{impl_state}</p>
      <div class="ts-field-k">Supporting insight</div><p class="ts-field-v">{insight_link}</p>
    </div>
    """


def methodology_drawer(title: str, markdown_body: str) -> None:
    with st.expander(title, expanded=False):
        st.markdown(markdown_body)


def disclosure() -> None:
    meta = product_meta()
    st.markdown(f'<p class="ts-disclosure">{meta["disclosure"]}</p>', unsafe_allow_html=True)


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value * 100:.{digits}f}%"


def fmt_money(value: float | None, digits: int = 0) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"${value:,.{digits}f}"


def fmt_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{int(value):,}"


def render_masthead(data: dict[str, pd.DataFrame]) -> None:
    meta = product_meta()
    monthly = data["monthly_kpis"].sort_values("run_date")
    latest = monthly.iloc[-1]
    prod = data["model_versions"]
    version = prod.loc[prod["status"] == "Production", "model_version"]
    version = version.iloc[0] if len(version) else latest["model_version"]
    st.markdown(
        f"""
        <div class="ts-masthead">
          <div class="ts-masthead-row">
            <div>
              <p class="ts-wordmark">{meta['product']}</p>
              <p class="ts-tagline">{meta['tagline']} · <span class="ts-workspace">{meta['brand']}</span> workspace</p>
            </div>
            <div class="ts-meta-chip-row">
              <div class="ts-meta-chip"><span class="k">Status</span><span class="v">Production</span></div>
              <div class="ts-meta-chip"><span class="k">Model</span><span class="v">{version}</span></div>
              <div class="ts-meta-chip"><span class="k">Latest run</span><span class="v">{latest['run_month']}</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


NAV_ITEMS = [
    "Overview",
    "Inputs",
    "Recommendations",
    "Adoption",
    "Impact",
    "Exceptions",
    "Insights & Actions",
    "Improvement",
    "Model Details",
]


def render_navigation() -> str:
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Overview"
    if hasattr(st, "pills"):
        selected = st.pills(
            "Navigate",
            NAV_ITEMS,
            selection_mode="single",
            default=st.session_state.nav_page
            if st.session_state.nav_page in NAV_ITEMS
            else "Overview",
            label_visibility="collapsed",
            key="nav_pills",
        )
        if selected:
            st.session_state.nav_page = selected
        return st.session_state.nav_page
    return st.radio(
        "Navigate",
        NAV_ITEMS,
        horizontal=True,
        label_visibility="collapsed",
        key="nav_page",
    )


def init_filter_state(data: dict[str, pd.DataFrame]) -> None:
    months = sorted(data["monthly_kpis"]["run_month"].unique().tolist())
    defaults = {
        "filter_months": (months[0], months[-1]),
        "filter_campaign": "All",
        "filter_region": "All",
        "filter_market_type": "All",
        "filter_segment": "All",
        "filter_execution": "All",
        "filter_model_version": "All",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_filter_bar(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    init_filter_state(data)
    months = sorted(data["monthly_kpis"]["run_month"].unique().tolist())
    decisions = data["decisions"]

    start, end = st.session_state.filter_months
    chips = [
        f"{start} → {end}",
    ]
    for label, key in [
        ("Campaign", "filter_campaign"),
        ("Region", "filter_region"),
        ("Market", "filter_market_type"),
        ("Segment", "filter_segment"),
        ("Adoption", "filter_execution"),
    ]:
        val = st.session_state[key]
        if val != "All":
            chips.append(f"{label}: {val}")

    chip_html = "".join(f'<span class="ts-chip">{c}</span>' for c in chips)
    st.markdown(
        f'<div class="ts-toolbar"><span class="ts-toolbar-label">Active filters</span>'
        f'<div class="ts-chip-row" style="margin:0;">{chip_html}</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Adjust filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.filter_months = st.select_slider(
                "Date window",
                options=months,
                value=st.session_state.filter_months,
            )
            campaigns = ["All"] + sorted(decisions["recommended_campaign"].dropna().unique().tolist())
            st.session_state.filter_campaign = st.selectbox(
                "Campaign",
                campaigns,
                index=campaigns.index(st.session_state.filter_campaign)
                if st.session_state.filter_campaign in campaigns
                else 0,
            )
        with c2:
            regions = ["All"] + sorted(decisions["region"].dropna().unique().tolist())
            st.session_state.filter_region = st.selectbox(
                "U.S. region",
                regions,
                index=regions.index(st.session_state.filter_region)
                if st.session_state.filter_region in regions
                else 0,
            )
            markets = ["All"] + sorted(decisions["market_type"].dropna().unique().tolist())
            st.session_state.filter_market_type = st.selectbox(
                "Market type",
                markets,
                index=markets.index(st.session_state.filter_market_type)
                if st.session_state.filter_market_type in markets
                else 0,
            )
        with c3:
            segments = ["All"] + sorted(decisions["segment"].dropna().unique().tolist())
            st.session_state.filter_segment = st.selectbox(
                "Customer segment",
                segments,
                index=segments.index(st.session_state.filter_segment)
                if st.session_state.filter_segment in segments
                else 0,
            )
            executions = ["All"] + sorted(decisions["execution_class"].dropna().unique().tolist())
            st.session_state.filter_execution = st.selectbox(
                "Adoption classification",
                executions,
                index=executions.index(st.session_state.filter_execution)
                if st.session_state.filter_execution in executions
                else 0,
            )

    start, end = st.session_state.filter_months
    return {
        "start": start,
        "end": end,
        "model_version": st.session_state.filter_model_version,
        "campaign": st.session_state.filter_campaign,
        "region": st.session_state.filter_region,
        "market_type": st.session_state.filter_market_type,
        "segment": st.session_state.filter_segment,
        "execution": st.session_state.filter_execution,
    }


def apply_filters(
    data: dict[str, pd.DataFrame], filters: dict[str, Any]
) -> dict[str, pd.DataFrame]:
    months = sorted(data["monthly_kpis"]["run_month"].unique().tolist())
    start_i = months.index(filters["start"])
    end_i = months.index(filters["end"])
    keep_months = set(months[start_i : end_i + 1])

    monthly = data["monthly_kpis"][data["monthly_kpis"]["run_month"].isin(keep_months)].copy()
    decisions = data["decisions"][data["decisions"]["run_month"].isin(keep_months)].copy()
    runs = data["model_runs"][data["model_runs"]["run_month"].isin(keep_months)].copy()

    if filters["model_version"] != "All":
        monthly = monthly[monthly["model_version"] == filters["model_version"]]
        decisions = decisions[decisions["model_version"] == filters["model_version"]]
        runs = runs[runs["model_version"] == filters["model_version"]]
    if filters["campaign"] != "All":
        decisions = decisions[decisions["recommended_campaign"] == filters["campaign"]]
    if filters["region"] != "All":
        decisions = decisions[decisions["region"] == filters["region"]]
    if filters["market_type"] != "All":
        decisions = decisions[decisions["market_type"] == filters["market_type"]]
    if filters["segment"] != "All":
        decisions = decisions[decisions["segment"] == filters["segment"]]
    if filters["execution"] != "All":
        decisions = decisions[decisions["execution_class"] == filters["execution"]]

    out = dict(data)
    out["monthly_kpis"] = monthly
    out["decisions"] = decisions
    out["model_runs"] = runs
    return out
