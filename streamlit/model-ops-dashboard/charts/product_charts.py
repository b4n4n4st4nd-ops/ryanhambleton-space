"""Shared Plotly theme and chart builders for Transparensea.

Chart titles live in HTML section headings — never inside Plotly —
to avoid legend/title collisions.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from components.styles import COLORS

SEMANTIC = {
    "Adopted": COLORS["adoption"],
    "Modified": COLORS["modified"],
    "Ignored": COLORS["ignored"],
    "Outside recommendation": COLORS["accent"],
    "Suppression adopted": COLORS["suppression"],
    "Suppression rejected": COLORS["outlier"],
}


def apply_theme(fig: go.Figure, height: int = 300, show_legend: bool = True) -> go.Figure:
    # Never set title_text="" — Streamlit/orjson can drop empty strings and Plotly.js
    # then renders the literal word "undefined" as the chart title.
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=16, t=8, b=58 if show_legend else 32),
        paper_bgcolor="#fffdf8",
        plot_bgcolor="#fffdf8",
        font=dict(family="Source Sans 3, Segoe UI, sans-serif", color=COLORS["ink"], size=12),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            x=0,
            xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=11, color=COLORS["ink"]),
            itemsizing="constant",
            traceorder="normal",
        ),
        hoverlabel=dict(bgcolor="#fffdf8", font_size=12, font_color=COLORS["ink"], bordercolor=COLORS["grid"]),
        bargap=0.28,
        separators=".,",
    )
    # Explicitly remove any title object so JS never sees text:null / missing text.
    fig.layout.title = None
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(color=COLORS["ink"], size=11),
        linecolor=COLORS["grid"],
        automargin=True,
        tickangle=0,
        nticks=min(8, 24),
        ticks="outside",
        tickcolor=COLORS["grid"],
        showline=True,
        linewidth=1,
        mirror=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#ece6da",
        gridwidth=1,
        tickfont=dict(color=COLORS["ink"], size=11),
        zeroline=False,
        automargin=True,
        ticks="outside",
        tickcolor=COLORS["grid"],
        showline=False,
    )
    return fig


def add_intervention_markers(fig: go.Figure, months: set[str]) -> None:
    for month, color in (
        ("2025-12", COLORS["intervention"]),
        ("2026-02", COLORS["post"]),
    ):
        if month in months:
            fig.add_shape(
                type="line",
                x0=month,
                x1=month,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color=color, width=1.6, dash="dot"),
            )


def rates_trend(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=monthly["campaign_choice_adoption"],
            name="Adoption",
            line=dict(color=COLORS["adoption"], width=2.6),
            hovertemplate="%{x}<br>Adoption %{y:.1%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=monthly["conversion_rate"],
            name="Conversion",
            line=dict(color=COLORS["conversion"], width=2.2),
            hovertemplate="%{x}<br>Conversion %{y:.1%}<extra></extra>",
        )
    )
    if "is_adoption_outlier" in monthly.columns:
        pts = monthly[monthly["is_adoption_outlier"]]
        if len(pts):
            fig.add_trace(
                go.Scatter(
                    x=pts["run_month"],
                    y=pts["campaign_choice_adoption"],
                    mode="markers",
                    name="Outlier",
                    marker=dict(color=COLORS["outlier"], size=9, symbol="diamond"),
                    hovertemplate="%{x}<br>Outlier %{y:.1%}<extra></extra>",
                )
            )
    add_intervention_markers(fig, set(monthly["run_month"]))
    fig.update_yaxes(tickformat=".0%")
    return apply_theme(fig, height=290)


def revenue_trend(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=monthly["run_month"],
            y=monthly["net_incremental_revenue"],
            name="Net incremental revenue",
            marker_color=COLORS["revenue"],
            opacity=0.88,
            hovertemplate="%{x}<br>NIR %{y:$,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    add_intervention_markers(fig, set(monthly["run_month"]))
    return apply_theme(fig, height=260, show_legend=False)


def metric_trend(monthly: pd.DataFrame, metric: str, label: str, color: str) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=monthly["run_month"],
            y=monthly[metric],
            name=label,
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(61,139,139,0.08)",
            hovertemplate="%{x}<br>%{y}<extra>" + label + "</extra>",
            showlegend=False,
        )
    )
    add_intervention_markers(fig, set(monthly["run_month"]))
    if metric.endswith("rate") or "adoption" in metric or metric == "production_coverage":
        fig.update_yaxes(tickformat=".0%")
    return apply_theme(fig, height=290, show_legend=False)


def control_chart(monthly: pd.DataFrame, kpi_label: str, limits: pd.DataFrame) -> go.Figure:
    """p-chart: band + centerline + series. Limit lines hidden from legend."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=limits["ucl"],
            name="UCL",
            line=dict(color=COLORS["sea"], width=1, dash="dot"),
            hovertemplate="UCL %{y:.1%}<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=limits["lcl"],
            name="LCL",
            line=dict(color=COLORS["sea"], width=1, dash="dot"),
            fill="tonexty",
            fillcolor=COLORS["band"],
            hovertemplate="LCL %{y:.1%}<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=limits["center"],
            name="Centerline",
            line=dict(color=COLORS["ink"], width=1.3, dash="dash"),
            hovertemplate="Centerline %{y:.1%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=limits["value"],
            name=kpi_label if len(kpi_label) < 28 else "Rate",
            line=dict(color=COLORS["adoption"], width=2.7),
            hovertemplate="%{x}<br>%{y:.1%}<extra>" + kpi_label + "</extra>",
        )
    )
    out = monthly[limits["outlier"].to_numpy()]
    if len(out):
        fig.add_trace(
            go.Scatter(
                x=out["run_month"],
                y=limits.loc[out.index, "value"],
                mode="markers",
                name="Outlier",
                marker=dict(color=COLORS["outlier"], size=10, symbol="x", line=dict(width=1.5)),
            )
        )
    add_intervention_markers(fig, set(monthly["run_month"]))
    fig.update_yaxes(tickformat=".0%")
    return apply_theme(fig, height=320)


def pareto_chart(pareto: pd.DataFrame, dimension: str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=pareto[dimension].astype(str),
            y=pareto["misses"],
            name="Misses",
            marker_color=COLORS["accent"],
            text=pareto["misses"],
            textposition="outside",
            textfont=dict(color=COLORS["ink"], size=11),
            cliponaxis=False,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=pareto[dimension].astype(str),
            y=pareto["cumulative"],
            name="Cumulative",
            line=dict(color=COLORS["ocean"], width=2),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(secondary_y=False)
    fig.update_yaxes(tickformat=".0%", secondary_y=True, showgrid=False)
    return apply_theme(fig, height=300)


def horizontal_rank_bar(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str | None = None,
    color: str = COLORS["recommend"],
    value_fmt: str | None = None,
) -> go.Figure:
    del title  # titles rendered in HTML
    ordered = df.sort_values(value_col, ascending=True)
    if value_fmt == "pct":
        text = [f"{v:.0%}" for v in ordered[value_col]]
    elif value_fmt == "money":
        text = [f"${v:,.0f}" for v in ordered[value_col]]
    elif value_fmt == "int":
        text = [f"{int(v):,}" for v in ordered[value_col]]
    else:
        text = None
    fig = go.Figure(
        go.Bar(
            x=ordered[value_col],
            y=ordered[label_col].astype(str),
            orientation="h",
            marker_color=color,
            text=text,
            textposition="outside",
            textfont=dict(color=COLORS["ink"], size=11),
            cliponaxis=False,
            hovertemplate="%{y}: %{x}<extra></extra>",
            showlegend=False,
        )
    )
    return apply_theme(fig, height=max(200, 26 * len(ordered) + 70), show_legend=False)


def stacked_class_bar(counts: pd.Series) -> go.Figure:
    total = counts.sum() or 1
    shares = (counts / total).tolist()
    labels = counts.index.tolist()
    colors = [SEMANTIC.get(lbl, COLORS["muted"]) for lbl in labels]
    fig = go.Figure()
    for label, share, color in zip(labels, shares, colors):
        fig.add_trace(
            go.Bar(
                x=[share],
                y=[" "],
                orientation="h",
                name=label,
                marker_color=color,
                text=f"{share:.0%}" if share >= 0.08 else "",
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#15202b", size=11),
                hovertemplate=f"{label}: {share:.1%}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(tickformat=".0%", range=[0, 1])
    fig.update_yaxes(showticklabels=False)
    return apply_theme(fig, height=150)


def heatmap(decisions: pd.DataFrame) -> go.Figure:
    pivot = (
        decisions.assign(exact=decisions["actual_campaign"] == decisions["recommended_campaign"])
        .groupby(["segment", "recommended_campaign"])["exact"]
        .mean()
        .reset_index()
        .pivot(index="segment", columns="recommended_campaign", values="exact")
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=[
                [0.0, "#f4f1ea"],
                [0.5, "#9ec5c5"],
                [1.0, "#1f4e5f"],
            ],
            zmin=0,
            zmax=1,
            colorbar=dict(tickformat=".0%", thickness=10, outlinewidth=0, len=0.85),
            hovertemplate="%{y} · %{x}<br>Exact match %{z:.0%}<extra></extra>",
        )
    )
    return apply_theme(fig, height=300, show_legend=False)


def volume_lines(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=monthly["recommended_messages"],
            name="Recommended",
            line=dict(color=COLORS["recommend"], width=2.4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["run_month"],
            y=monthly["messages_sent"],
            name="Executed",
            line=dict(color=COLORS["adoption"], width=2.4),
        )
    )
    return apply_theme(fig, height=260)


def class_outcome_bars(summary: pd.DataFrame, metric: str, title: str | None = None, fmt: str = "number") -> go.Figure:
    del title
    ordered = summary.sort_values(metric, ascending=True)
    colors = [SEMANTIC.get(c, COLORS["muted"]) for c in ordered["execution_class"]]
    if fmt == "pct":
        text = [f"{v:.0%}" for v in ordered[metric]]
    elif fmt == "money":
        text = [f"${v:,.0f}" for v in ordered[metric]]
    else:
        text = [f"{v:,.0f}" for v in ordered[metric]]
    fig = go.Figure(
        go.Bar(
            x=ordered[metric],
            y=ordered["execution_class"],
            orientation="h",
            marker_color=colors,
            text=text,
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color=COLORS["ink"], size=11),
            showlegend=False,
        )
    )
    return apply_theme(fig, height=270, show_legend=False)


def px_hist(df: pd.DataFrame, x: str, title: str | None = None) -> go.Figure:
    del title
    fig = px.histogram(df, x=x, nbins=28, color_discrete_sequence=[COLORS["sea"]])
    fig.update_traces(marker_line_width=0, showlegend=False)
    return apply_theme(fig, height=260, show_legend=False)
