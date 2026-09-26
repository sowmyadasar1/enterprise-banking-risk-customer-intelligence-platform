"""Model evaluation metrics (MAE, RMSE, MAPE)."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    if not mask.any():
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_models(df: pd.DataFrame, target: str, split_ratio: float = 0.8):
    """Perform a train/test split to evaluate models against actual data."""
    series = df[target]
    train_size = int(len(series) * split_ratio)
    train, test = series.iloc[:train_size], series.iloc[train_size:]
    steps = len(test)

    # We will import models locally to avoid circular imports if needed
    from .models import naive_forecast, moving_average_forecast, fit_arima

    results = {}

    # 1. Naïve
    f_naive, _, _ = naive_forecast(train, steps)
    results["naive"] = {
        "mae": mean_absolute_error(test, f_naive),
        "rmse": np.sqrt(mean_squared_error(test, f_naive)),
        "mape": mean_absolute_percentage_error(test, f_naive),
    }

    # 2. Moving Average
    f_ma, _, _ = moving_average_forecast(train, steps, window=30)
    results["moving_average"] = {
        "mae": mean_absolute_error(test, f_ma),
        "rmse": np.sqrt(mean_squared_error(test, f_ma)),
        "mape": mean_absolute_percentage_error(test, f_ma),
    }

    # 3. ARIMA
    arima_model = fit_arima(train, f"eval_{target}")
    if arima_model is not None:
        f_arima = arima_model.forecast(steps=steps)
        results["arima"] = {
            "mae": mean_absolute_error(test, f_arima),
            "rmse": np.sqrt(mean_squared_error(test, f_arima)),
            "mape": mean_absolute_percentage_error(test, f_arima),
        }

    return results


def run_evaluation(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  STEP 5: MODEL EVALUATION (80/20 SPLIT)")
    print("=" * 70)

    from . import config

    eval_results = {}
    for target in config.TARGETS:
        if target in df.columns:
            print(f"\n  Evaluating {target}...")
            res = evaluate_models(df, target)
            eval_results[target] = res

            for m, metrics in res.items():
                print(
                    f"    [{m.upper()}] MAE: {metrics['mae']:.2f} | RMSE: {metrics['rmse']:.2f} | MAPE: {metrics['mape']:.2f}%"
                )

    return eval_results
