"""
Customer Segmentation Service — Business logic decoupled from API routes.
Handles feature alignment between API schema and the trained K-Means model.
"""
import logging
import numpy as np
import pandas as pd
from ..core.exceptions import ModelNotLoadedError, PredictionError
from .model_loader import ModelManager

logger = logging.getLogger("api.services.segment")

# Default persona mapping if persona JSON unavailable
DEFAULT_PERSONAS = {
    0: ("Mass Market", "Standard customers with typical banking usage"),
    1: ("VIP / High-Value", "High-balance, high-activity premium customers"),
    2: ("Emerging Growth", "Newer customers with increasing engagement"),
    3: ("Dormant / At-Risk", "Low-activity customers at risk of churn"),
}

# Feature names the K-Means pipeline was trained on (from Phase 7C scaler)
TRAINED_FEATURES = [
    'customer_age', 'customer_tenure_days', 'customer_tenure_years', 'is_active',
    'account_count', 'avg_balance', 'total_balance', 'max_balance', 'min_balance',
    'products_owned', 'balance_range', 'support_ticket_count', 'marketing_responses',
    'marketing_engagement_score', 'customer_lifetime_value', 'avg_transaction_amount',
    'median_transaction_amount', 'max_transaction_amount', 'min_transaction_amount',
    'std_transaction_amount', 'total_transaction_count', 'total_spend',
    'avg_daily_txn_count', 'avg_weekly_txn_count', 'avg_monthly_txn_count',
    'rolling_7d_spend', 'rolling_30d_spend', 'transaction_velocity',
    'weekend_spending_ratio', 'night_transaction_ratio', 'large_transaction_ratio',
    'merchant_diversity', 'total_loan_amount', 'total_loans', 'avg_loan_amount',
    'avg_interest_rate', 'avg_loan_age_days', 'total_remaining_balance',
    'avg_repayment_rate', 'avg_loan_utilization', 'total_late_payments',
    'total_missed_payments', 'total_payments', 'avg_interest_burden',
    'avg_missed_payment_ratio', 'avg_installment', 'risk_score', 'credit_score',
    'fraud_case_count', 'total_fraud_loss', 'days_since_last_transaction',
    'preferred_day_of_week', 'preferred_month', 'preferred_quarter',
    'summer_txn_ratio', 'winter_txn_ratio', 'days_since_last_loan_payment',
]

# Mapping from API schema fields -> trained feature names
FIELD_MAP = {
    "avg_balance": "avg_balance",
    "total_transactions": "total_transaction_count",
    "avg_transaction_amount": "avg_transaction_amount",
    "tenure_days": "customer_tenure_days",
    "num_products": "products_owned",
    "credit_score": "credit_score",
}


def predict_segment(features: dict) -> dict:
    """
    Assign a customer to a segment based on their financial behavior.
    Maps the simplified API input onto the full 57-feature trained model space.
    Returns: { cluster_id, persona, persona_description }
    """
    manager = ModelManager()
    model = manager.get_segmentation_model()
    scaler = manager.get_segmentation_scaler()
    transformer = manager.get_segmentation_transformer()

    if model is None:
        raise ModelNotLoadedError("kmeans", "K-Means model not found on disk")

    try:
        # Build a zero-filled DataFrame with all 57 trained features
        row = {feat: 0.0 for feat in TRAINED_FEATURES}

        # Map API fields to trained feature columns
        for api_field, model_field in FIELD_MAP.items():
            if api_field in features:
                row[model_field] = features[api_field]

        # Derive tenure_years from tenure_days
        if "tenure_days" in features:
            row["customer_tenure_years"] = features["tenure_days"] / 365.25

        df = pd.DataFrame([row], columns=TRAINED_FEATURES)

        # Apply the same preprocessing pipeline as training
        if transformer is not None:
            df_transformed = pd.DataFrame(
                transformer.transform(df), columns=TRAINED_FEATURES
            )
        else:
            df_transformed = df

        if scaler is not None:
            df_scaled = scaler.transform(df_transformed)
        else:
            df_scaled = df_transformed.values

        cluster_id = int(model.predict(df_scaled)[0])

        # Look up persona
        personas = manager.get_personas()
        if personas and isinstance(personas, dict):
            persona_info = personas.get(str(cluster_id), {})
            persona_name = persona_info.get(
                "persona", DEFAULT_PERSONAS.get(cluster_id, ("Unknown", ""))[0]
            )
            persona_desc = persona_info.get(
                "description", DEFAULT_PERSONAS.get(cluster_id, ("", ""))[1]
            )
        else:
            fallback = DEFAULT_PERSONAS.get(cluster_id, ("Unknown", "No description"))
            persona_name = fallback[0]
            persona_desc = fallback[1]

        return {
            "cluster_id": cluster_id,
            "persona": persona_name,
            "persona_description": persona_desc,
        }
    except Exception as e:
        logger.error("Segmentation failed: %s", str(e))
        raise PredictionError("kmeans", str(e))
