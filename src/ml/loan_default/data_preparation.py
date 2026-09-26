"""Data preparation: load Feature Store, validate, split."""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from . import config


def load_and_validate():
    """Load feature store and perform data quality checks."""
    print("\n" + "=" * 70)
    print("  STEP 1: DATA PREPARATION (LOAN DEFAULT)")
    print("=" * 70)

    df = pd.read_parquet(config.FEATURE_STORE)
    print(f"  Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    # --- Validation ---
    print("\n  [Validation]")
    missing = df.isnull().sum().sum()
    print(f"    Missing values: {missing}")
    print(f"    Duplicate rows: {df.duplicated().sum()}")
    print(f"    Target column: '{config.TARGET}'")

    if config.TARGET not in df.columns:
        raise ValueError(f"Target column {config.TARGET} not found in Feature Store!")

    print(f"    Target distribution:")
    vc = df[config.TARGET].value_counts()
    for val, cnt in vc.items():
        print(f"      {val}: {cnt} ({cnt/len(df)*100:.1f}%)")

    prevalence = vc.get(1, 0) / len(df) * 100
    print(f"    Default prevalence: {prevalence:.2f}%")

    if prevalence == 0:
        raise ValueError(
            "Default prevalence is 0%. Cannot train models without positive samples."
        )

    # --- Check for data leakage ---
    print("\n  [Leakage Check]")
    # For loans, we should ensure we aren't using things like 'total_missed_payments' directly if it leaks the outcome
    # (since the target loan_risk_indicator is based on risk score > 70 in our synthetic generation).
    leakage_cols = ["total_missed_payments"]
    found = [c for c in leakage_cols if c in df.columns]
    if found:
        print(f"    Removing leakage columns: {found}")
    else:
        print("    No highly obvious leakage columns detected.")

    return df, found


def prepare_splits(df, leakage_cols):
    """Create train/val/test splits with stratification."""
    drop = [c for c in config.DROP_COLS + leakage_cols if c in df.columns]
    X = df.drop(columns=drop)

    # Ensure target is present for y
    if config.TARGET not in df.columns:
        raise ValueError(f"Target {config.TARGET} missing when creating splits.")
    y = df[config.TARGET].astype(int)

    # Ensure no target in X
    if config.TARGET in X.columns:
        X = X.drop(columns=[config.TARGET])

    # Keep only numeric
    X = X.select_dtypes(include=[np.number]).fillna(0)

    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
    )

    # Second split: train vs val
    val_ratio = config.VAL_SIZE / (1 - config.TEST_SIZE)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=val_ratio,
        random_state=config.RANDOM_STATE,
        stratify=y_temp,
    )

    print(f"\n  [Splits]")
    print(f"    Train: {X_train.shape[0]} rows ({y_train.mean()*100:.1f}% defaults)")
    print(f"    Val:   {X_val.shape[0]} rows ({y_val.mean()*100:.1f}% defaults)")
    print(f"    Test:  {X_test.shape[0]} rows ({y_test.mean()*100:.1f}% defaults)")
    print(f"    Features: {X_train.shape[1]}")

    return X_train, X_val, X_test, y_train, y_val, y_test
