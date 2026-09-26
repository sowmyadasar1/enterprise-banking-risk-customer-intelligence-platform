"""Configuration for the Fraud Detection Platform."""

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

for d in [MODELS_DIR, REPORTS_DIR, VIS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

TARGET = "fraud_risk_indicator"
ID_COL = "customer_id"
DROP_COLS = [
    "customer_id",
    "customer_type",
    "risk_rating",
    "income_band",
    "risk_category",
    "credit_score_band",
]
RANDOM_STATE = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15

# Cost assumptions
AVG_FRAUD_LOSS = 5000  # Cost per missed fraud (FN)
REVIEW_COST = 50  # Cost per false alarm (FP)
