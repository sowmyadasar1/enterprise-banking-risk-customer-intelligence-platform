"""Configuration for the Revenue & Transaction Forecasting Platform."""

import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "warehouse", "enterprise_dw.db")
MODULE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(MODULE_DIR, "models")
REPORTS_DIR = os.path.join(MODULE_DIR, "reports")
VIS_DIR = os.path.join(MODULE_DIR, "visualizations")
DATA_DIR = os.path.join(MODULE_DIR, "data")

# Target series available for forecasting
TARGETS = ["transaction_volume", "revenue", "loan_demand", "new_customers"]

# Forecasting Horizons (days)
HORIZONS = [30, 90, 180, 365]
DEFAULT_HORIZON = 90

# Calendar feature engineering
LAG_DAYS = [1, 7, 30]
ROLLING_WINDOWS = [7, 30]

RANDOM_STATE = 42

# Ensure directories exist
for d in [MODELS_DIR, REPORTS_DIR, VIS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)
