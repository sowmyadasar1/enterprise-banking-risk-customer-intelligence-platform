"""
Pydantic Response Schemas — Standardized output models for all endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─── Generic Wrappers ────────────────────────────────────────────────
class APIMetadata(BaseModel):
    """Standard metadata attached to every successful response."""
    model_name: str = Field(..., description="Name of the ML model used")
    model_version: str = Field("1.0.0", description="Model artifact version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: float = Field(0.0, ge=0, description="Processing time in milliseconds")


class ErrorResponse(BaseModel):
    """Standard error envelope."""
    error: str
    detail: Any
    path: Optional[str] = None


# ─── Fraud Detection ────────────────────────────────────────────────
class FraudPredictionResult(BaseModel):
    """Single fraud prediction output."""
    is_fraud: bool = Field(..., description="True if predicted fraudulent")
    fraud_probability: float = Field(..., ge=0, le=1, description="Probability score")
    risk_level: str = Field(..., description="Low / Medium / High / Critical")


class FraudPredictionResponse(BaseModel):
    """Full response envelope for fraud prediction."""
    prediction: FraudPredictionResult
    metadata: APIMetadata


class FraudBatchResponse(BaseModel):
    """Batch fraud prediction response."""
    predictions: List[FraudPredictionResult]
    total_scored: int
    flagged_count: int
    metadata: APIMetadata


# ─── Loan Default ───────────────────────────────────────────────────
class LoanDefaultResult(BaseModel):
    """Single loan default prediction output."""
    will_default: bool
    default_probability: float = Field(..., ge=0, le=1)
    risk_band: str = Field(..., description="Low / Medium / High")
    recommended_action: str = Field(..., description="Approve / Review / Decline")


class LoanDefaultResponse(BaseModel):
    """Full response envelope for loan default."""
    prediction: LoanDefaultResult
    metadata: APIMetadata


# ─── Customer Segmentation ──────────────────────────────────────────
class SegmentationResult(BaseModel):
    """Customer segmentation output."""
    cluster_id: int
    persona: str = Field(..., description="Business persona label (e.g., VIP, Dormant)")
    persona_description: str = Field("", description="Brief persona summary")


class SegmentationResponse(BaseModel):
    """Full response envelope for segmentation."""
    prediction: SegmentationResult
    metadata: APIMetadata


# ─── Forecasting ────────────────────────────────────────────────────
class ForecastDataPoint(BaseModel):
    """A single forecast data point."""
    day: int = Field(..., ge=1, description="Day offset from today")
    mean: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    """Full response envelope for forecast."""
    target_metric: str
    horizon_days: int
    forecast: List[ForecastDataPoint]
    cumulative_total: float = Field(..., description="Sum of forecasted means")
    metadata: APIMetadata


# ─── Health & System ────────────────────────────────────────────────
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    models_loaded: Dict[str, bool] = Field(default_factory=dict)


class ModelInfoResponse(BaseModel):
    """Information about a loaded model."""
    model_name: str
    model_type: str
    is_loaded: bool
    features_count: Optional[int] = None
    artifact_path: str
