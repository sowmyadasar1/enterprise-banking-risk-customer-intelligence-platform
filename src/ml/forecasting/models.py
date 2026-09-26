"""Time series forecasting models (Naïve, Moving Average, ARIMA)."""

import os
import joblib
import numpy as np
import pandas as pd
import warnings
from statsmodels.tsa.arima.model import ARIMA
from . import config

warnings.filterwarnings("ignore")


def naive_forecast(series: pd.Series, steps: int) -> tuple:
    """Last observation carried forward."""
    last_val = series.iloc[-1]
    forecast = np.full(steps, last_val)
    # Synthetic narrow CI for baseline
    std_dev = series.std() * 0.1
    ci_lower = forecast - (1.96 * std_dev)
    ci_upper = forecast + (1.96 * std_dev)
    return forecast, ci_lower, ci_upper


def moving_average_forecast(series: pd.Series, steps: int, window: int = 7) -> tuple:
    """Rolling mean carried forward."""
    ma_val = series.rolling(window=window).mean().iloc[-1]
    forecast = np.full(steps, ma_val)
    # Synthetic CI for baseline
    std_dev = series.tail(window).std()
    ci_lower = forecast - (1.96 * std_dev)
    ci_upper = forecast + (1.96 * std_dev)
    return forecast, ci_lower, ci_upper


def fit_arima(series: pd.Series, target_name: str) -> ARIMA:
    """Fit a basic auto-regressive model. Defaults to (7, 1, 1) for daily financial data."""
    print(f"    Fitting ARIMA for {target_name}...")
    try:
        # P=7 (weekly AR), D=1 (trend diff), Q=1 (MA smoothing)
        model = ARIMA(series, order=(7, 1, 1))
        fitted = model.fit()

        # Save model
        model_path = os.path.join(config.MODELS_DIR, f"arima_{target_name}.pkl")
        fitted.save(model_path)

        return fitted
    except Exception as e:
        print(f"    [ERROR] ARIMA fit failed for {target_name}: {e}")
        return None


def generate_forecasts(
    df: pd.DataFrame, target: str, steps: int = config.DEFAULT_HORIZON
):
    """Generate multi-model forecasts for a single target."""
    series = df[target]
    results = {}

    # 1. Naïve
    f_naive, l_naive, u_naive = naive_forecast(series, steps)
    results["naive"] = {"mean": f_naive, "lower": l_naive, "upper": u_naive}

    # 2. Moving Average
    f_ma, l_ma, u_ma = moving_average_forecast(series, steps, window=30)
    results["moving_average"] = {"mean": f_ma, "lower": l_ma, "upper": u_ma}

    # 3. ARIMA
    arima_model = fit_arima(series, target)
    if arima_model is not None:
        forecast_obj = arima_model.get_forecast(steps=steps)
        results["arima"] = {
            "mean": forecast_obj.predicted_mean.values,
            "lower": forecast_obj.conf_int().iloc[:, 0].values,
            "upper": forecast_obj.conf_int().iloc[:, 1].values,
        }

    return results


def train_and_forecast_all(df: pd.DataFrame, horizons: list = config.HORIZONS):
    print("\n" + "=" * 70)
    print("  STEP 4: MODEL DEVELOPMENT & TUNING")
    print("=" * 70)

    all_forecasts = {}

    for target in config.TARGETS:
        if target not in df.columns:
            continue

        print(f"\n  [{target.upper()}]")
        target_forecasts = {}
        for h in horizons:
            print(f"    Generating {h}-day forecast...")
            target_forecasts[h] = generate_forecasts(df, target, steps=h)

        all_forecasts[target] = target_forecasts

    return all_forecasts
