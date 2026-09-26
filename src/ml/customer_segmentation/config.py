"""Configuration for the Customer Segmentation & Intelligence Platform."""

import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
FEATURE_STORE = os.path.join(
    PROJECT_ROOT, "data", "feature_store", "customer_features.parquet"
)
MODULE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(MODULE_DIR, "models")
REPORTS_DIR = os.path.join(MODULE_DIR, "reports")
VIS_DIR = os.path.join(MODULE_DIR, "visualizations")
DATA_DIR = os.path.join(MODULE_DIR, "data")
PERSONAS_DIR = os.path.join(MODULE_DIR, "personas")
RECS_DIR = os.path.join(MODULE_DIR, "recommendations")

for d in [MODELS_DIR, REPORTS_DIR, VIS_DIR, DATA_DIR, PERSONAS_DIR, RECS_DIR]:
    os.makedirs(d, exist_ok=True)

ID_COL = "customer_id"
RANDOM_STATE = 42

# Columns to use for clustering (numeric behavioral features)
# We exclude identifiers, categorical strings, and target labels from other models
DROP_COLS = [
    "customer_id",
    "customer_type",
    "risk_rating",
    "income_band",
    "risk_category",
    "credit_score_band",
    "fraud_risk_indicator",
    "loan_risk_indicator",
]

# Clustering hyperparameters
K_RANGE = range(3, 11)  # K values to evaluate for K-Means
DBSCAN_EPS_RANGE = [0.5, 1.0, 1.5, 2.0]
DBSCAN_MIN_SAMPLES = [5, 10, 15]

# RFM column mappings (from feature store)
RFM_RECENCY_COL = "days_since_last_transaction"
RFM_FREQUENCY_COL = "avg_monthly_txn_count"
RFM_MONETARY_COL = "avg_balance"
