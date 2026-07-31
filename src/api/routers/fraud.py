"""
Fraud Detection Router — Endpoints for real-time and batch fraud scoring.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from ..schemas.requests import FraudPredictionRequest, FraudBatchRequest
from ..schemas.responses import (
    FraudPredictionResponse,
    FraudPredictionResult,
    FraudBatchResponse,
    APIMetadata,
)
from ..services.fraud_service import predict_fraud, predict_fraud_batch
from ..core.security import verify_api_key

router = APIRouter(prefix="/predict", tags=["Fraud Detection"], dependencies=[Depends(verify_api_key)])


@router.post("/fraud", response_model=FraudPredictionResponse, summary="Score a Single Transaction")
async def score_transaction(request: FraudPredictionRequest):
    """
    Scores a single transaction for fraud risk using the XGBoost model trained in Phase 7A.
    
    Returns a fraud probability (0-1), a boolean flag, and a risk level (Low/Medium/High/Critical).
    """
    start = time.perf_counter()
    result = predict_fraud(request.model_dump())
    elapsed = (time.perf_counter() - start) * 1000

    return FraudPredictionResponse(
        prediction=FraudPredictionResult(**result),
        metadata=APIMetadata(
            model_name="fraud_xgboost",
            model_version="1.0.0",
            timestamp=datetime.utcnow(),
            latency_ms=round(elapsed, 2),
        ),
    )


@router.post("/fraud/batch", response_model=FraudBatchResponse, summary="Score a Batch of Transactions")
async def score_batch(request: FraudBatchRequest):
    """
    Scores up to 1,000 transactions in a single API call.
    Returns individual predictions plus aggregate statistics.
    """
    start = time.perf_counter()
    raw_results = predict_fraud_batch([t.model_dump() for t in request.transactions])
    elapsed = (time.perf_counter() - start) * 1000

    predictions = [FraudPredictionResult(**r) for r in raw_results]
    flagged = sum(1 for p in predictions if p.is_fraud)

    return FraudBatchResponse(
        predictions=predictions,
        total_scored=len(predictions),
        flagged_count=flagged,
        metadata=APIMetadata(
            model_name="fraud_xgboost",
            model_version="1.0.0",
            timestamp=datetime.utcnow(),
            latency_ms=round(elapsed, 2),
        ),
    )
