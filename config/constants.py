"""
Project-wide static variables and constants.
"""

# Categorical mappings
TRANSACTION_TYPES = ["PURCHASE", "WITHDRAWAL", "DEPOSIT", "TRANSFER", "FEE", "REFUND"]
ACCOUNT_STATUSES = ["ACTIVE", "CLOSED", "FROZEN", "PENDING"]
LOAN_STATUSES = ["CURRENT", "DELINQUENT", "DEFAULT", "PAID_OFF", "PENDING_APPROVAL"]

# ML Model Thresholds
FRAUD_PROBABILITY_THRESHOLD = 0.85
DEFAULT_PROBABILITY_THRESHOLD = 0.75

# File Extensions
DATA_FILE_EXTENSION = ".csv"
PARQUET_EXTENSION = ".parquet"

# Roles for API access
ROLES = {
    "ADMIN": "administrator",
    "ANALYST": "data_analyst",
    "VIEWER": "viewer",
}
