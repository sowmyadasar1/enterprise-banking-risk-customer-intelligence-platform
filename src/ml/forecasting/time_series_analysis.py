"""Time series statistical analysis (Stationarity, Decomposition)."""

import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf


def run_analysis(df: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  STEP 2: TIME SERIES ANALYSIS")
    print("=" * 70)

    analysis_results = {}

    for col in df.columns:
        series = df[col]
        print(f"\n  [{col.replace('_', ' ').title()}]")

        # 1. Stationarity Test (Augmented Dickey-Fuller)
        # H0: Time series is non-stationary.
        try:
            adf_result = adfuller(series.dropna())
            p_value = adf_result[1]
            is_stationary = p_value < 0.05
            print(
                f"    ADF p-value: {p_value:.4f} -> {'Stationary' if is_stationary else 'Non-Stationary'}"
            )
        except Exception as e:
            is_stationary = False
            p_value = 1.0
            print(f"    ADF Test failed: {e}")

        # 2. ACF / PACF (Summary metrics)
        try:
            acf_vals = acf(series.dropna(), nlags=7, fft=True)
            lag_7_acf = acf_vals[7] if len(acf_vals) > 7 else 0
            print(f"    Autocorrelation (Lag 7): {lag_7_acf:.4f}")
        except:
            lag_7_acf = 0

        # 3. Seasonal Decomposition
        try:
            # Assume weekly seasonality for daily data
            decomp = seasonal_decompose(series.dropna(), model="additive", period=7)
            trend_var = decomp.trend.var()
            seasonal_var = decomp.seasonal.var()
            resid_var = decomp.resid.var()
            total_var = trend_var + seasonal_var + resid_var

            seasonal_strength = seasonal_var / total_var if total_var > 0 else 0
            trend_strength = trend_var / total_var if total_var > 0 else 0

            print(f"    Trend Strength: {trend_strength:.1%}")
            print(f"    Seasonal Strength (Weekly): {seasonal_strength:.1%}")

            decomp_data = {
                "trend": decomp.trend,
                "seasonal": decomp.seasonal,
                "resid": decomp.resid,
            }
        except Exception as e:
            decomp_data = None
            seasonal_strength = 0
            trend_strength = 0

        analysis_results[col] = {
            "is_stationary": is_stationary,
            "adf_p_value": p_value,
            "lag_7_acf": lag_7_acf,
            "seasonal_strength": seasonal_strength,
            "trend_strength": trend_strength,
            "decomposition": decomp_data,
        }

    return analysis_results
