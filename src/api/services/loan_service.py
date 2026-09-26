"""
Loan Default Prediction Service — Business logic decoupled from API routes.
"""

import logging
import numpy as np
import pandas as pd
from ..core.exceptions import ModelNotLoadedError, PredictionError
from .model_loader import ModelManager

logger = logging.getLogger("api.services.loan")


def classify_risk_band(probability: float) -> str:
    if probability >= 0.60:
        return "High"
    elif probability >= 0.30:
        return "Medium"
    return "Low"


def recommend_action(probability: float) -> str:
    if probability >= 0.60:
        return "Decline"
    elif probability >= 0.30:
        return "Review"
    return "Approve"


def predict_loan_default(features: dict) -> dict:
    """
    Run loan default prediction for a single application.
    Returns: { will_default, default_probability, risk_band, recommended_action }
    """
    manager = ModelManager()
    model = manager.get_loan_model()
    selected_features = manager.get_loan_features()

    if model is None:
        raise ModelNotLoadedError(
            "loan_xgboost", "XGBoost loan model not found on disk"
        )

    try:
        df = pd.DataFrame([features])

        if selected_features is not None:
            available = [c for c in selected_features if c in df.columns]
            missing = [c for c in selected_features if c not in df.columns]
            for col in missing:
                df[col] = 0
            df = df[selected_features]

        proba = model.predict_proba(df)[0][1]
        will_default = bool(proba >= 0.5)

        return {
            "will_default": will_default,
            "default_probability": round(float(proba), 4),
            "risk_band": classify_risk_band(proba),
            "recommended_action": recommend_action(proba),
        }
    except Exception as e:
        logger.error("Loan default prediction failed: %s", str(e))
        raise PredictionError("loan_xgboost", str(e))
