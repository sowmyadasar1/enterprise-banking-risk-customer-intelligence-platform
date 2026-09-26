"""Feature engineering for time series modeling."""

import pandas as pd
from . import config


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 70)
    print("  STEP 3: FEATURE ENGINEERING")
    print("=" * 70)

    features_df = df.copy()

    # 1. Calendar Features
    features_df["year"] = features_df.index.year
    features_df["quarter"] = features_df.index.quarter
    features_df["month"] = features_df.index.month
    features_df["week"] = features_df.index.isocalendar().week.astype(int)
    features_df["day"] = features_df.index.day
    features_df["day_of_week"] = features_df.index.dayofweek
    features_df["is_weekend"] = (features_df["day_of_week"] >= 5).astype(int)

    # 2. Lags & Rolling Statistics
    for target in config.TARGETS:
        if target not in features_df.columns:
            continue

        # Lag features
        for lag in config.LAG_DAYS:
            features_df[f"{target}_lag_{lag}"] = features_df[target].shift(lag)

        # Rolling Means
        for window in config.ROLLING_WINDOWS:
            features_df[f"{target}_rolling_mean_{window}"] = (
                features_df[target].rolling(window=window).mean()
            )
            features_df[f"{target}_rolling_std_{window}"] = (
                features_df[target].rolling(window=window).std()
            )

        # Growth Rate (7-day momentum)
        features_df[f"{target}_growth_7d"] = (
            features_df[target] - features_df[f"{target}_lag_7"]
        ) / (features_df[f"{target}_lag_7"] + 1e-5)

    print(f"  Added {len(features_df.columns) - len(df.columns)} new features.")
    print(f"  Dropping {max(config.ROLLING_WINDOWS)} days of NaN rows due to windows.")

    features_df = features_df.dropna()
    print(f"  Final Engineered Dataset: {features_df.shape}")

    return features_df
