"""
Forecasting Service — ARIMA model-based forecast generation.
"""
import logging
import numpy as np
from ..core.exceptions import ModelNotLoadedError, PredictionError
from .model_loader import ModelManager

logger = logging.getLogger("api.services.forecast")

VALID_TARGETS = ["transaction_volume", "revenue", "loan_demand", "new_customers"]


def generate_forecast(target: str, horizon: int) -> dict:
    """
    Generate a time series forecast from a persisted ARIMA model.
    Returns: { target_metric, horizon_days, forecast: [...], cumulative_total }
    """
    if target not in VALID_TARGETS:
        raise PredictionError("arima", f"Invalid target: {target}. Must be one of {VALID_TARGETS}")

    manager = ModelManager()
    model = manager.get_forecast_model(target)

    if model is None:
        raise ModelNotLoadedError(f"arima_{target}", f"ARIMA model for '{target}' not found on disk")

    try:
        forecast_obj = model.get_forecast(steps=horizon)
        mean = forecast_obj.predicted_mean.values
        conf_int = forecast_obj.conf_int()
        lower = conf_int.iloc[:, 0].values
        upper = conf_int.iloc[:, 1].values

        # Clamp to non-negative
        mean = np.maximum(mean, 0)
        lower = np.maximum(lower, 0)
        upper = np.maximum(upper, 0)

        forecast_points = []
        for i in range(horizon):
            forecast_points.append({
                "day": i + 1,
                "mean": round(float(mean[i]), 2),
                "lower_bound": round(float(lower[i]), 2),
                "upper_bound": round(float(upper[i]), 2),
            })

        return {
            "target_metric": target,
            "horizon_days": horizon,
            "forecast": forecast_points,
            "cumulative_total": round(float(mean.sum()), 2),
        }
    except Exception as e:
        logger.error("Forecast generation failed for %s: %s", target, str(e))
        raise PredictionError(f"arima_{target}", str(e))
