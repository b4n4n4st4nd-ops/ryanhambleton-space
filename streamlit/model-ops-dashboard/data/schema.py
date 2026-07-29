"""Canonical Transparensea data contract for the A.Typical demonstration."""

from __future__ import annotations

from typing import Final

PRODUCT_NAME: Final = "Transparensea"
PRODUCT_TAGLINE: Final = "Model Transparency, Adoption & Impact"
BRAND: Final = "A.Typical"
DISCLOSURE: Final = (
    "A.Typical is a fictional brand. Demonstration records are synthetic and "
    "modeled after common marketing uplift and production-model workflows."
)

CAMPAIGNS: Final = (
    "New Season Edit",
    "Performance Collection",
    "Member Access",
    "Re-Engagement",
    "Follow-Up",
    "Suppression",
)

PRIMARY_TREATMENTS: Final = (
    "New Season Edit",
    "Performance Collection",
    "Suppression",
)

REGIONS: Final = (
    "Pacific Northwest",
    "California",
    "Mountain West",
    "Southwest",
    "Midwest",
    "Northeast",
    "Southeast",
)

MARKET_TYPES: Final = ("Urban", "Suburban", "Rural")

LOYALTY_TIERS: Final = ("Explorer", "Member", "Insider", "Founders")

CHANNELS: Final = ("Direct", "Organic", "Paid Social", "Retail Partner")

SEGMENTS: Final = (
    "New Customer",
    "Returning Buyer",
    "High-Value",
    "At-Risk",
    "Performance Affinity",
    "Lifestyle Affinity",
)

EXECUTION_CLASSES: Final = (
    "Adopted",
    "Modified",
    "Ignored",
    "Outside recommendation",
    "Suppression adopted",
    "Suppression rejected",
)

ADOPTION_KPIS: Final = (
    "production_coverage",
    "message_volume_adoption",
    "customer_selection_adoption",
    "campaign_choice_adoption",
    "followup_adoption",
    "suppression_adoption",
    "priority_adoption",
)

REQUIRED_TABLES: Final = (
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
    "validation_report",
)

FINANCIAL_ASSUMPTIONS: Final = {
    "average_order_value": 88.0,
    "gross_margin": 0.55,
    "message_cost": 0.14,
    "followup_cost": 0.45,
    "campaign_cost_per_message": {
        "New Season Edit": 0.22,
        "Performance Collection": 0.26,
        "Member Access": 0.30,
        "Re-Engagement": 0.20,
        "Follow-Up": 0.18,
        "Suppression": 0.0,
    },
    "formula": (
        "Incremental conversions × AOV × gross margin − message costs − "
        "follow-up costs − allocated campaign cost = net incremental revenue"
    ),
}

FEATURE_DEFINITIONS: Final = [
    {
        "feature": "tenure_months",
        "definition": "Months since first A.Typical purchase or account creation.",
        "data_type": "numeric",
    },
    {
        "feature": "recency_days",
        "definition": "Days since most recent purchase.",
        "data_type": "numeric",
    },
    {
        "feature": "historical_spend",
        "definition": "Trailing twelve-month gross spend.",
        "data_type": "numeric",
    },
    {
        "feature": "purchase_frequency",
        "definition": "Purchases in trailing twelve months.",
        "data_type": "numeric",
    },
    {
        "feature": "digital_engagement",
        "definition": "Normalized site and app engagement score (0–1).",
        "data_type": "numeric",
    },
    {
        "feature": "email_engagement",
        "definition": "Trailing email open/click engagement score (0–1).",
        "data_type": "numeric",
    },
    {
        "feature": "prior_campaign_response",
        "definition": "Response rate to prior eligible campaigns.",
        "data_type": "numeric",
    },
    {
        "feature": "category_affinity",
        "definition": "Affinity toward core apparel assortment.",
        "data_type": "numeric",
    },
    {
        "feature": "performance_affinity",
        "definition": "Affinity toward technical / training products.",
        "data_type": "numeric",
    },
    {
        "feature": "lifestyle_affinity",
        "definition": "Affinity toward lifestyle / editorial assortment.",
        "data_type": "numeric",
    },
    {
        "feature": "days_since_visit",
        "definition": "Days since last website or app visit.",
        "data_type": "numeric",
    },
    {
        "feature": "followup_eligible",
        "definition": "Customer engaged a prior message without converting.",
        "data_type": "boolean",
    },
    {
        "feature": "primary_channel",
        "definition": "Dominant acquisition or engagement channel.",
        "data_type": "categorical",
    },
    {
        "feature": "loyalty_tier",
        "definition": "Current loyalty tier.",
        "data_type": "categorical",
    },
    {
        "feature": "customer_type",
        "definition": "New versus returning customer.",
        "data_type": "categorical",
    },
    {
        "feature": "region",
        "definition": "U.S. commercial region.",
        "data_type": "categorical",
    },
    {
        "feature": "market_type",
        "definition": "Urban, suburban, or rural market type.",
        "data_type": "categorical",
    },
]
