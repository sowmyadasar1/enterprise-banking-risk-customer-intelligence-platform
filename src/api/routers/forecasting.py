"""
Revenue & Transaction Forecasting Router
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from ..schemas.responses import (
    ForecastResponse,
    ForecastDataPoint,
    APIMetadata,
)
from ..services.forecast_service import generate_forecast
from ..core.security import verify_api_key

router = APIRouter(prefix="/forecast", tags=["Forecasting"], dependencies=[Depends(verify_api_key)])


@router.get(
    "/{target_metric}",
    response_model=ForecastResponse,
    summary="Generate Time Series Forecast",
)
async def get_forecast(
    target_metric: str,
    horizon: int = Query(30, ge=1, le=365, description="Forecast horizon in days"),
):
    """
    Generates a multi-day time series forecast using the ARIMA models from Phase 7D.

    **Valid target_metric values**: `transaction_volume`, `revenue`, `loan_demand`, `new_customers`

    Returns daily mean predictions with 95% confidence intervals.
    """
    start = time.perf_counter()
    result = generate_forecast(target_metric, horizon)
    elapsed = (time.perf_counter() - start) * 1000

    forecast_points = [ForecastDataPoint(**fp) for fp in result["forecast"]]

    return ForecastResponse(
        target_metric=result["target_metric"],
        horizon_days=result["horizon_days"],
        forecast=forecast_points,
        cumulative_total=result["cumulative_total"],
        metadata=APIMetadata(
            model_name=f"arima_{target_metric}",
            model_version="1.0.0",
            timestamp=datetime.utcnow(),
            latency_ms=round(elapsed, 2),
        ),
    )
