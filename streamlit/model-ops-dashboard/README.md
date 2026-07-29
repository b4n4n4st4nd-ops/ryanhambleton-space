# Transparensea

**Predictive model AI/ML visualization and reporting companion software**  
**Model Transparency, Adoption & Impact**

Streamlit product demonstration for the fictional apparel brand **A.Typical**.

A.Typical is a fictional brand. Demonstration records are synthetic and modeled after common marketing uplift and production-model workflows. Simulated financial results are not real.

## What it shows

The full loop:

`Inputs → Recommendation → Adoption → Outcome → Outlier/Exception → Insight → Action → Measurement → Historical Learning`

Primary campaigns: **New Season Edit**, **Performance Collection**, and **Suppression**, plus Member Access, Re-Engagement, and Follow-Up in execution layers.

## Local run

```bash
cd streamlit/model-ops-dashboard
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_demo_data.py   # if generated/ is missing
streamlit run app.py
```

## Regenerate demo data

```bash
python scripts/build_demo_data.py
```

Uses a fixed seed (`42`), fits a scikit-learn T-learner, and writes CSVs under `data/generated/`.

## Tests

```bash
pip install pytest
pytest tests/ -q
python -m compileall .
```

## Deploy (Streamlit Community Cloud)

1. Point the app at this repository.
2. Set **Main file path** to `streamlit/model-ops-dashboard/app.py`.
3. Paste the public URL into `content/lab/analytics-explorer.json` and `content/lab/transparensea.json` as `embedUrl`.

## Customize

| Area | Location |
|------|----------|
| Schema / campaigns / financials | `data/schema.py` |
| Data generation / model | `scripts/build_demo_data.py` |
| Views | `views/pages.py` |
| Visual identity | `components/styles.py` |
| Lab metadata | `content/lab/*.json` |

## Documentation

See `docs/transparensea/` in the repository root for the product spec, data dictionary, and build report.
