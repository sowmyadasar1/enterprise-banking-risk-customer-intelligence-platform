"""
Enterprise FastAPI Configuration
Centralized settings management using Pydantic BaseSettings.
"""

import os
from pathlib import Path
from functools import lru_cache

# Project root detection
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Model artifact paths
FRAUD_MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "fraud_detection" / "models"
LOAN_MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "loan_default" / "models"
SEGMENT_MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "customer_segmentation" / "models"
FORECAST_MODEL_DIR = PROJECT_ROOT / "src" / "ml" / "forecasting" / "models"
PERSONA_PATH = (
    PROJECT_ROOT
    / "src"
    / "ml"
    / "customer_segmentation"
    / "personas"
    / "persona_profiles.json"
)
DW_PATH = PROJECT_ROOT / "data" / "warehouse" / "enterprise_dw.db"

# API metadata
API_TITLE = "Enterprise Banking Risk & Customer Intelligence Platform"
API_DESCRIPTION = """
Production-grade REST API serving four machine learning systems:
- **Fraud Detection** — Real-time transaction fraud scoring
- **Loan Default Prediction** — Credit risk assessment
- **Customer Segmentation** — Persona-based customer intelligence
- **Revenue Forecasting** — ARIMA-based business outlook

Built on FastAPI with lazy-loaded model registry, Pydantic validation,
and structured logging.
"""
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Runtime settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "enterprise-banking-dev-key-2026")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
