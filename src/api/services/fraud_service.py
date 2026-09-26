"""
Fraud Detection Service — Business logic decoupled from API routes.
"""

import logging
import numpy as np
import pandas as pd
from ..core.exceptions import ModelNotLoadedError, PredictionError
from .model_loader import ModelManager

logger = logging.getLogger("api.services.fraud")


def classify_risk(probability: float) -> str:
    """Map a fraud probability to a human-readable risk level."""
    if probability >= 0.85:
        return "Critical"
    elif probability >= 0.60:
        return "High"
    elif probability >= 0.30:
        return "Medium"
    return "Low"


def predict_fraud(features: dict) -> dict:
    """
    Run fraud prediction for a single transaction.
    Returns: { is_fraud, fraud_probability, risk_level }
    """
    manager = ModelManager()
    model = manager.get_fraud_model()
    selected_features = manager.get_fraud_features()

    if model is None:
        raise ModelNotLoadedError(
            "fraud_xgboost", "XGBoost fraud model not found on disk"
        )

    try:
        # Build a DataFrame from the request — only the features the model expects
        df = pd.DataFrame([features])

        # Map request fields to the model's expected feature set
        if selected_features is not None:
            # Keep only the columns that overlap with the trained feature set
            available = [c for c in selected_features if c in df.columns]
            missing = [c for c in selected_features if c not in df.columns]
            for col in missing:
                df[col] = 0  # Fill missing features with zero (safe default)
            df = df[selected_features]

        proba = model.predict_proba(df)[0][1]
        is_fraud = bool(proba >= 0.5)

        return {
            "is_fraud": is_fraud,
            "fraud_probability": round(float(proba), 4),
            "risk_level": classify_risk(proba),
        }
    except Exception as e:
        logger.error("Fraud prediction failed: %s", str(e))
        raise PredictionError("fraud_xgboost", str(e))


def predict_fraud_batch(transactions: list[dict]) -> list[dict]:
    """Run fraud prediction for a batch of transactions."""
    return [predict_fraud(txn) for txn in transactions]
