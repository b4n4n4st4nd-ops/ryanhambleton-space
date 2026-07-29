"""Transparensea design tokens and global product chrome CSS."""

from __future__ import annotations

TOKENS = {
    "chrome": "#0f1a22",
    "chrome_elevated": "#182633",
    "canvas": "#f7f3eb",
    "panel": "#fffcf7",
    "panel_muted": "#f3eee4",
    "ink": "#14202a",
    "ink_soft": "#2a3440",
    "muted": "#5a6570",
    "chrome_text": "#f6f1e8",
    "chrome_muted": "#9aabB6",
    "ocean": "#1a4a5c",
    "sea": "#2f7f7f",
    "lime": "#c5d06a",
    "clay": "#c45c26",
    "warn": "#b45309",
    "crit": "#9b1c1c",
    "neutral": "#8a8478",
    "border": "#ddd5c6",
    "grid": "#ebe4d6",
    "recommend": "#1a4a5c",
    "adopted": "#2f7f7f",
    "modified": "#b7c45a",
    "ignored": "#8a8478",
    "suppression": "#a89f8e",
    "outlier": "#9b1c1c",
    "intervention": "#c45c26",
    "post": "#2a6a6a",
    "conversion": "#2f6f4e",
    "revenue": "#1a4a5c",
    "radius": "10px",
    "radius_sm": "7px",
    "font_sans": '"Source Sans 3", "Segoe UI", sans-serif',
    "font_display": '"Fraunces", Georgia, serif',
}

# Fix typo in chrome_muted hex if any
TOKENS["chrome_muted"] = "#9aabb6"

COLORS = {
    "canvas": TOKENS["canvas"],
    "panel": TOKENS["panel"],
    "ink": TOKENS["ink"],
    "ocean": TOKENS["ocean"],
    "sea": TOKENS["sea"],
    "accent": TOKENS["clay"],
    "lime": TOKENS["lime"],
    "recommend": TOKENS["recommend"],
    "actual": TOKENS["clay"],
    "adoption": TOKENS["adopted"],
    "conversion": TOKENS["conversion"],
    "revenue": TOKENS["revenue"],
    "outlier": TOKENS["outlier"],
    "intervention": TOKENS["intervention"],
    "post": TOKENS["post"],
    "modified": TOKENS["modified"],
    "ignored": TOKENS["ignored"],
    "suppression": TOKENS["suppression"],
    "band": "rgba(47, 127, 127, 0.14)",
    "grid": TOKENS["grid"],
    "muted": TOKENS["muted"],
}

PRODUCT_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
:root {{
  --ts-chrome: {TOKENS["chrome"]};
  --ts-chrome-elevated: {TOKENS["chrome_elevated"]};
  --ts-canvas: {TOKENS["canvas"]};
  --ts-panel: {TOKENS["panel"]};
  --ts-panel-muted: {TOKENS["panel_muted"]};
  --ts-ink: {TOKENS["ink"]};
  --ts-ink-soft: {TOKENS["ink_soft"]};
  --ts-muted: {TOKENS["muted"]};
  --ts-chrome-text: {TOKENS["chrome_text"]};
  --ts-chrome-muted: {TOKENS["chrome_muted"]};
  --ts-ocean: {TOKENS["ocean"]};
  --ts-sea: {TOKENS["sea"]};
  --ts-lime: {TOKENS["lime"]};
  --ts-border: {TOKENS["border"]};
  --ts-radius: {TOKENS["radius"]};
  --ts-radius-sm: {TOKENS["radius_sm"]};
  --ts-crit: {TOKENS["crit"]};
}}
html, body, [class*="css"] {{ font-family: {TOKENS["font_sans"]}; color: var(--ts-ink); }}
.stApp {{
  background:
    radial-gradient(1200px 500px at 12% -8%, rgba(197,208,106,0.10), transparent 55%),
    radial-gradient(900px 420px at 92% 0%, rgba(47,127,127,0.07), transparent 50%),
    linear-gradient(180deg, #f3efe6 0%, var(--ts-canvas) 28%, #f5f1e9 100%);
}}
.block-container {{
  padding-top: 0 !important;
  padding-bottom: 1.1rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  max-width: 1180px;
}}
header[data-testid="stHeader"], #MainMenu, footer, div[data-testid="stToolbar"],
div[data-testid="stDecoration"], a[href*="share.streamlit.io"], button[kind="header"],
[data-testid="stStatusWidget"], [data-testid="stAppDeployButton"],
[data-testid="stBaseButton-headerNoPadding"] {{
  display: none !important; visibility: hidden !important;
}}
section[data-testid="stSidebar"] {{ display: none !important; }}
div[data-testid="stVerticalBlock"] > div {{ gap: 0.28rem !important; }}
[data-testid="stElementToolbar"] {{ display:none !important; }}
/* Tighten shell → page content */
.ts-toolbar {{ margin-bottom: 0.2rem !important; }}
div[data-testid="stExpander"] {{ margin-bottom: 0.15rem !important; }}
.ts-page-title {{ margin-top: 0.05rem !important; }}

/* —— Masthead —— */
.ts-masthead {{
  background: linear-gradient(105deg, var(--ts-chrome) 0%, #152433 58%, #1a2c3a 100%);
  color: var(--ts-chrome-text);
  margin: 0 -1rem 0.5rem -1rem;
  padding: 12px 18px 11px;
  border-bottom: 2px solid var(--ts-lime);
  box-shadow: 0 8px 24px rgba(15,26,34,0.18);
}}
.ts-masthead-row {{ display:flex; justify-content:space-between; gap:14px; align-items:center; flex-wrap:wrap; }}
.ts-wordmark {{
  font-family: {TOKENS["font_display"]}; font-size:1.42rem; font-weight:700;
  margin:0; letter-spacing:-0.03em; line-height:1.05; color:#fff;
}}
.ts-tagline {{ margin:3px 0 0; font-size:0.74rem; color: var(--ts-chrome-muted); font-weight:500; }}
.ts-workspace {{ font-family: {TOKENS["font_display"]}; color: var(--ts-lime); font-weight:600; }}
.ts-meta-chip-row {{ display:flex; flex-wrap:wrap; gap:7px; justify-content:flex-end; }}
.ts-meta-chip {{
  background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.12);
  border-radius: var(--ts-radius-sm); padding:6px 10px; min-width:100px;
}}
.ts-meta-chip .k {{ display:block; font-size:0.56rem; letter-spacing:0.07em; text-transform:uppercase; color: var(--ts-chrome-muted); }}
.ts-meta-chip .v {{ display:block; font-size:0.8rem; font-weight:650; color: #fff; margin-top:1px; }}

/* —— Nav pills (Streamlit st.pills → stButtonGroup) —— */
div[data-testid="stButtonGroup"],
div[data-testid="stPills"] {{
  margin:0 0 0.35rem !important; padding:0 !important;
}}
div[data-testid="stButtonGroup"] button[data-variant="pills"],
div[data-testid="stPills"] button {{
  border-radius:999px !important; border:1px solid transparent !important; font-weight:600 !important;
  font-size:0.76rem !important; color: var(--ts-muted) !important; background:transparent !important;
  padding:0.32rem 0.78rem !important; min-height:1.9rem !important;
  transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
}}
div[data-testid="stButtonGroup"] button[data-variant="pills"]:hover {{
  background: rgba(26,74,92,0.06) !important; color: var(--ts-ocean) !important;
}}
div[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"],
div[data-testid="stButtonGroup"] button[data-variant="pills"][data-selected="true"],
div[data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stPills"] button[kind="pillsActive"],
div[data-testid="stPills"] button[data-selected="true"],
div[data-testid="stPills"] button[kind="primary"] {{
  background: var(--ts-ocean) !important; border-color: var(--ts-ocean) !important;
  color: #fff !important; box-shadow: 0 2px 8px rgba(26,74,92,0.22);
}}
div[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] p,
div[data-testid="stButtonGroup"] button[data-variant="pills"][data-selected="true"] p,
div[data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] span,
div[data-testid="stButtonGroup"] button[data-variant="pills"][data-selected="true"] span {{
  color: #fff !important;
}}
div[data-testid="stRadio"] [role="radiogroup"] {{ display:flex !important; flex-wrap:wrap !important; gap:5px !important; flex-direction:row !important; }}
div[data-testid="stRadio"] [role="radiogroup"] label {{
  border-radius:999px !important; border:1px solid var(--ts-border) !important;
  padding:5px 11px !important; background: var(--ts-panel) !important;
}}
div[data-testid="stRadio"] svg {{ display:none !important; }}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {{
  background: var(--ts-ocean) !important; border-color: var(--ts-ocean) !important; color:#fff !important;
}}

/* —— Filter toolbar —— */
.ts-toolbar {{
  display:flex; flex-wrap:wrap; align-items:center; gap:8px 10px; background: var(--ts-panel);
  border:1px solid var(--ts-border); border-radius: var(--ts-radius); padding:7px 11px; margin-bottom:0.25rem;
  box-shadow: 0 1px 0 rgba(20,32,42,0.03);
}}
.ts-toolbar-label {{ font-size:0.64rem; font-weight:700; color: var(--ts-muted); letter-spacing:0.05em; text-transform:uppercase; }}
div[data-testid="stExpander"] {{ background:transparent !important; border:none !important; margin-bottom:0.28rem !important; }}
div[data-testid="stExpander"] details {{
  border:1px solid var(--ts-border) !important; border-radius: var(--ts-radius) !important;
  background: var(--ts-panel-muted) !important;
}}
div[data-testid="stExpander"] summary {{
  font-size:0.74rem !important; font-weight:650 !important; color: var(--ts-ocean) !important;
  padding: 0.28rem 0.5rem !important; min-height: 1.7rem !important;
}}
div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{ padding: 0.3rem 0.5rem 0.5rem !important; }}

/* —— Typography —— */
.ts-page-title {{
  font-family: {TOKENS["font_display"]}; font-size:1.38rem; font-weight:650; color: var(--ts-ink);
  margin:0.2rem 0 2px; letter-spacing:-0.02em; line-height:1.15;
}}
.ts-page-subtitle {{ font-size:0.86rem; color: var(--ts-muted); margin:0 0 0.7rem; max-width:66ch; line-height:1.4; }}
.ts-section {{
  font-size:0.72rem; font-weight:700; color: var(--ts-ocean); margin:0.85rem 0 0.28rem;
  letter-spacing:0.04em; text-transform:uppercase;
}}
.ts-caption {{ font-size:0.74rem; color: var(--ts-muted); margin:0 0 0.45rem; max-width:74ch; line-height:1.35; }}
.ts-chart-title {{
  font-size:0.78rem; font-weight:700; color: var(--ts-ink); margin:0.1rem 0 -0.15rem 2px;
  letter-spacing:-0.01em;
}}

/* —— KPI / cards —— */
.ts-kpi {{
  background: var(--ts-panel); border:1px solid var(--ts-border); border-radius: var(--ts-radius);
  border-left:3px solid var(--ts-ocean); padding:11px 13px; min-height:98px;
  box-shadow: 0 1px 2px rgba(20,32,42,0.04);
}}
.ts-kpi.secondary {{
  min-height:68px; padding:9px 11px; border-left-width:2px; background: var(--ts-panel-muted);
  box-shadow:none;
}}
.ts-kpi .label {{ font-size:0.64rem; font-weight:650; color: var(--ts-muted); letter-spacing:0.02em; text-transform:uppercase; }}
.ts-kpi .value {{ font-size:1.36rem; font-weight:700; color: var(--ts-ink); margin:4px 0 2px; line-height:1.08; letter-spacing:-0.02em; }}
.ts-kpi.secondary .value {{ font-size:1.05rem; }}
.ts-kpi .delta-up {{ color: var(--ts-sea); font-size:0.72rem; font-weight:650; }}
.ts-kpi .delta-down {{ color: var(--ts-crit); font-size:0.72rem; font-weight:650; }}
.ts-kpi .delta-flat {{ color: var(--ts-muted); font-size:0.72rem; font-weight:650; }}
.ts-kpi .interp {{ font-size:0.7rem; color: var(--ts-muted); margin-top:3px; line-height:1.3; }}

.ts-card {{
  background: var(--ts-panel); border:1px solid var(--ts-border); border-radius: var(--ts-radius);
  padding:13px 15px; box-shadow: 0 1px 2px rgba(20,32,42,0.04);
}}
.ts-card h3 {{ font-family: {TOKENS["font_display"]}; font-size:0.98rem; font-weight:650; color: var(--ts-ink); margin:0 0 6px; }}
.ts-card .body {{ font-size:0.84rem; color: var(--ts-ink-soft); line-height:1.42; max-width:68ch; margin:0 0 8px; }}
.ts-evidence-row {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0; }}
.ts-evidence {{ background: var(--ts-panel-muted); border:1px solid var(--ts-border); border-radius: var(--ts-radius-sm); padding:7px 9px; min-width:110px; }}
.ts-evidence .k {{ display:block; font-size:0.58rem; color: var(--ts-muted); text-transform:uppercase; letter-spacing:0.03em; }}
.ts-evidence .v {{ display:block; font-size:0.88rem; font-weight:700; color: var(--ts-ink); }}
.ts-action-card {{
  background: var(--ts-panel); border:1px solid var(--ts-border); border-radius: var(--ts-radius);
  padding:13px 15px; border-top:3px solid var(--ts-sea); height:100%;
  box-shadow: 0 1px 2px rgba(20,32,42,0.04);
}}
.ts-action-card.model {{ border-top-color: var(--ts-ocean); }}
.ts-action-card.data {{ border-top-color: var(--ts-lime); }}
.ts-field-k {{ font-size:0.58rem; font-weight:700; color: var(--ts-muted); margin:8px 0 2px; text-transform:uppercase; letter-spacing:0.04em; }}
.ts-field-v {{ font-size:0.84rem; color: var(--ts-ink); line-height:1.35; margin:0; }}
.ts-badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.66rem; font-weight:700; border:1px solid var(--ts-border); background:#efe9dc; }}
.ts-badge.ok {{ background:#dcefe8; color:#1f5c40; border-color:#b7d8c8; }}
.ts-badge.warn {{ background:#f8e4d4; color:#8a3d0a; border-color:#e7c3a4; }}
.ts-badge.crit {{ background:#f6d9d9; color:#7a1515; border-color:#e3b0b0; }}
.ts-badge.info {{ background:#e4eef1; color:#1f4e5f; border-color:#b7c9cf; }}
.ts-chip-row {{ display:flex; flex-wrap:wrap; gap:6px; margin:0; }}
.ts-chip {{
  display:inline-block; background:#e7f0f2; color: var(--ts-ocean); border:1px solid #b5c9cf;
  border-radius:999px; padding:2px 9px; font-size:0.7rem; font-weight:650;
}}
.ts-chart-wrap {{
  background: var(--ts-panel); border:1px solid var(--ts-border); border-radius: var(--ts-radius);
  padding:8px 10px 2px; margin-bottom:0.45rem;
}}
.ts-table-wrap {{
  background: var(--ts-panel); border:1px solid var(--ts-border); border-radius: var(--ts-radius);
  padding:4px; overflow-x:auto; box-shadow: 0 1px 2px rgba(20,32,42,0.03);
}}
.ts-disclosure {{ font-size:0.7rem; color: var(--ts-muted); border-top:1px solid var(--ts-border); margin-top:0.9rem; padding-top:0.55rem; max-width:80ch; }}
.ts-empty {{ background: var(--ts-panel-muted); border:1px dashed var(--ts-border); border-radius: var(--ts-radius); padding:16px; color: var(--ts-muted); text-align:center; }}
.ts-timeline-step {{ background: var(--ts-panel); border:1px solid var(--ts-border); border-left:3px solid var(--ts-sea); border-radius: var(--ts-radius); padding:10px 12px; margin-bottom:8px; }}
.ts-timeline-step .step {{ font-size:0.62rem; font-weight:700; color: var(--ts-ocean); margin-bottom:2px; text-transform:uppercase; letter-spacing:0.04em; }}

/* —— Plotly / widgets —— */
.stPlotlyChart {{
  background: var(--ts-panel) !important;
  border: 1px solid var(--ts-border) !important;
  border-radius: var(--ts-radius) !important;
  padding: 2px 4px 0 !important;
  margin-bottom: 0.5rem !important;
  box-shadow: 0 1px 2px rgba(20,32,42,0.04);
}}
.stPlotlyChart > div {{ width: 100% !important; }}
.js-plotly-plot .plotly .gtitle {{ display:none !important; }}
.stSelectbox label, .stSlider label, .stTextInput label, .stNumberInput label {{
  font-size:0.7rem !important; color: var(--ts-muted) !important; font-weight:650 !important;
  letter-spacing:0.02em;
}}
div[data-baseweb="select"] > div {{
  background: var(--ts-panel) !important; border-color: var(--ts-border) !important;
  min-height: 2rem !important;
}}
[data-testid="stDataFrame"] {{
  border: 1px solid var(--ts-border) !important;
  border-radius: var(--ts-radius) !important;
  background: var(--ts-panel) !important;
  overflow: hidden !important;
  margin-bottom: 0.45rem !important;
}}
[data-testid="stDataFrame"] table {{ font-size: 0.78rem !important; }}
hr {{ border-color: var(--ts-border) !important; margin: 0.55rem 0 !important; }}
</style>
"""
