"""Fraud detection API schemas."""

from pydantic import BaseModel
from typing import Dict, Any


class FraudPredictionRequest(BaseModel):
    """Schema for fraud prediction request."""

    transaction_id: str
    amount: float
    features: Dict[str, Any]


class FraudPredictionResponse(BaseModel):
    """Schema for fraud prediction response."""

    transaction_id: str
    is_fraud: bool
    fraud_probability: float


class FraudAlert(BaseModel):
    """Schema for fraud alert representation."""

    alert_id: str
    transaction_id: str
    severity: str
    timestamp: str
