"""
Loan Default Prediction Router
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from ..schemas.requests import LoanDefaultRequest
from ..schemas.responses import (
    LoanDefaultResponse,
    LoanDefaultResult,
    APIMetadata,
)
from ..services.loan_service import predict_loan_default
from ..core.security import verify_api_key

router = APIRouter(prefix="/predict", tags=["Loan Default"], dependencies=[Depends(verify_api_key)])


@router.post("/loan-default", response_model=LoanDefaultResponse, summary="Predict Loan Default Risk")
async def predict_default(request: LoanDefaultRequest):
    """
    Predicts whether a loan application will default using the XGBoost model from Phase 7B.

    Returns default probability, risk band (Low/Medium/High), and a recommended action
    (Approve/Review/Decline).
    """
    start = time.perf_counter()
    result = predict_loan_default(request.model_dump())
    elapsed = (time.perf_counter() - start) * 1000

    return LoanDefaultResponse(
        prediction=LoanDefaultResult(**result),
        metadata=APIMetadata(
            model_name="loan_xgboost",
            model_version="1.0.0",
            timestamp=datetime.utcnow(),
            latency_ms=round(elapsed, 2),
        ),
    )
