"""Configuration for the Loan Default Prediction Platform."""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FEATURE_STORE = os.path.join(PROJECT_ROOT, 'data', 'feature_store', 'customer_features.parquet')
MODULE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(MODULE_DIR, 'models')
REPORTS_DIR = os.path.join(MODULE_DIR, 'reports')
VIS_DIR = os.path.join(MODULE_DIR, 'visualizations')
DATA_DIR = os.path.join(MODULE_DIR, 'data')

for d in [MODELS_DIR, REPORTS_DIR, VIS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

TARGET = 'loan_risk_indicator'
ID_COL = 'customer_id'

# Exclude non-numeric, direct leakages (fraud flags, loan counts if they leak risk directly), etc.
# We keep loan statistics, but risk_rating/credit_score_band are categorical strings.
DROP_COLS = [
    'customer_id', 'customer_type', 'risk_rating', 'income_band',
    'risk_category', 'credit_score_band', 'fraud_risk_indicator',
    'loan_risk_indicator', 'risk_score'
]

RANDOM_STATE = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15

# Cost assumptions for loans
AVG_LOAN_AMOUNT = 15000       # Average amount of a loan
PROFIT_MARGIN = 0.10          # 10% profit margin on a good loan (True Negative)
RECOVERY_RATE = 0.20          # Recover 20% of defaulted loans (so loss is 80% of loan)
REVIEW_COST = 100             # Cost per manual review (False Positive or True Positive requiring review)

# thresholds for decisions
AUTO_APPROVE_FPR = 0.05       # Max FPR to auto-approve
AUTO_REJECT_TPR = 0.80        # Min TPR to auto-reject (catch 80% of defaults)
