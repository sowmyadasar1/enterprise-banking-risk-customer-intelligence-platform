"""Data preparation: load Feature Store, validate, split."""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from . import config


def load_and_validate():
    """Load feature store and perform data quality checks."""
    print("\n" + "="*70)
    print("  STEP 1: DATA PREPARATION")
    print("="*70)

    df = pd.read_parquet(config.FEATURE_STORE)
    print(f"  Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    # --- Validation ---
    print("\n  [Validation]")
    print(f"    Missing values: {df.isnull().sum().sum()}")
    print(f"    Duplicate rows: {df.duplicated().sum()}")
    print(f"    Target column: '{config.TARGET}'")
    print(f"    Target distribution:")
    vc = df[config.TARGET].value_counts()
    for val, cnt in vc.items():
        print(f"      {val}: {cnt} ({cnt/len(df)*100:.1f}%)")
    print(f"    Fraud prevalence: {vc.get(1, 0)/len(df)*100:.2f}%")

    # --- Check for data leakage ---
    print("\n  [Leakage Check]")
    leakage_cols = ['fraud_case_count', 'total_fraud_loss']
    found = [c for c in leakage_cols if c in df.columns]
    if found:
        print(f"    Removing leakage columns: {found}")
    else:
        print("    No leakage columns detected.")

    return df


def prepare_splits(df):
    """Create train/val/test splits with stratification."""
    drop = [c for c in config.DROP_COLS + ['fraud_case_count', 'total_fraud_loss']
            if c in df.columns]
    X = df.drop(columns=[config.TARGET] + drop)
    y = df[config.TARGET].astype(int)

    # Keep only numeric
    X = X.select_dtypes(include=[np.number]).fillna(0)

    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y)

    # Second split: train vs val
    val_ratio = config.VAL_SIZE / (1 - config.TEST_SIZE)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=config.RANDOM_STATE, stratify=y_temp)

    print(f"\n  [Splits]")
    print(f"    Train: {X_train.shape[0]} rows ({y_train.mean()*100:.1f}% fraud)")
    print(f"    Val:   {X_val.shape[0]} rows ({y_val.mean()*100:.1f}% fraud)")
    print(f"    Test:  {X_test.shape[0]} rows ({y_test.mean()*100:.1f}% fraud)")
    print(f"    Features: {X_train.shape[1]}")

    return X_train, X_val, X_test, y_train, y_val, y_test
