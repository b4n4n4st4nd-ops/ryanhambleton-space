# Transparensea — Data Dictionary

Demonstration brand: **A.Typical** (fictional). All generated tables live under
`streamlit/model-ops-dashboard/data/generated/`.

## Entities

### model_versions
| Field | Description |
|-------|-------------|
| model_version | `v1.0` or `v1.1` |
| status | Production / Retired |
| method | T-learner logistic per treatment |
| feature_influence_methods | Standardized coefficient; Permutation importance |
| change_notes | Version narrative |

### model_runs
| Field | Description |
|-------|-------------|
| run_id | `RUN-YYYYMM` |
| run_month | Period label |
| model_version | Scoring version |
| phase | initial / recurring / intervention / improved |
| eligible_customers | Eligible population size |
| records_scored | Scored count |

### customers
Customer master with tenure, recency, spend, engagement, affinities, channel, loyalty, region, state, market type, segment. No protected personal attributes.

### decisions
Grain: one row per scored (or outside-recommendation) customer-run.

| Field | Description |
|-------|-------------|
| decision_id | Stable demo ID |
| recommended_campaign | Model recommendation |
| actual_campaign | Business execution |
| execution_class | Adopted / Modified / Ignored / Outside recommendation / Suppression adopted / Suppression rejected |
| predicted_conversion / estimated_uplift / estimated_net_value | Model outputs (estimated) |
| converted / gross_revenue / campaign_cost / net_incremental_revenue | Outcomes (simulated) |
| missed_value / wasted_spend | Estimated opportunity metrics |

### monthly_kpis
Run-level adoption, conversion, and financial rollups including p-chart helper columns.

### feature_influence / feature_dictionary
Feature definitions plus method-specific influence scores by model version and treatment.

### business_exceptions / statistical_outliers
Known operational exceptions vs statistically detected outliers.

### generated_insights / human_insight_reviews
Automated insight text (preserved) and human review edits.

### suggested_actions / action_measurements
Business / model / data actions with before/after measurement windows and result classification.

### validation_report
Minimum validation checks and pass/fail status.

## Financial assumptions

See `data/schema.py` → `FINANCIAL_ASSUMPTIONS`.

Formula:

`Incremental conversions × AOV × gross margin − message costs − follow-up costs − allocated campaign cost = net incremental revenue`
