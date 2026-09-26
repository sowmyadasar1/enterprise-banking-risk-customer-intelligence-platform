"""Data preparation: load Feature Store, scale, handle outliers."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, PowerTransformer
import joblib
import os
from . import config


def load_and_validate():
    """Load feature store and perform validation."""
    print("\n" + "=" * 70)
    print("  STEP 1: DATA PREPARATION")
    print("=" * 70)

    df = pd.read_parquet(config.FEATURE_STORE)
    print(f"  Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    # Validation
    print(f"\n  [Validation]")
    print(f"    Missing values: {df.isnull().sum().sum()}")
    print(f"    Duplicate rows: {df.duplicated().sum()}")
    print(f"    Columns: {df.shape[1]}")

    return df


def prepare_features(df):
    """Prepare numeric features for clustering."""
    customer_ids = df[config.ID_COL].values

    drop = [c for c in config.DROP_COLS if c in df.columns]
    X = df.drop(columns=drop).select_dtypes(include=[np.number]).fillna(0)

    print(f"  Features for clustering: {X.shape[1]}")
    print(f"  Customers: {X.shape[0]}")

    # Power Transform to stabilize highly skewed financial distributions
    print("  Applying Yeo-Johnson PowerTransform...")
    pt = PowerTransformer(method="yeo-johnson", standardize=False)
    X_transformed = pd.DataFrame(pt.fit_transform(X), columns=X.columns, index=X.index)

    # Standard Scaling
    print("  Applying StandardScaler...")
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X_transformed), columns=X.columns, index=X.index
    )

    # Save scaler and transformer for reproducibility
    joblib.dump(scaler, os.path.join(config.MODELS_DIR, "scaler.joblib"))
    joblib.dump(pt, os.path.join(config.MODELS_DIR, "power_transformer.joblib"))

    print(f"  Scaled features shape: {X_scaled.shape}")
    return X_scaled, X, customer_ids
