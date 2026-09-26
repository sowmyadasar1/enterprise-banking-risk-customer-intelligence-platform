"""
Feature Validation Module
Validates feature quality: missing values, constant features, duplicates, distributions.
"""

import pandas as pd
import numpy as np


def validate_missing_values(df, threshold=0.3):
    """Flag features with missing value ratio above threshold."""
    missing = df.isnull().mean().round(4)
    flagged = missing[missing > threshold]
    if len(flagged) > 0:
        print(
            f"  [WARN] {len(flagged)} features exceed {threshold*100}% missing threshold:"
        )
        for col, pct in flagged.items():
            print(f"    - {col}: {pct*100:.1f}%")
    else:
        print(f"  [OK] All features below {threshold*100}% missing threshold.")
    return flagged


def validate_constant_features(df):
    """Detect features with zero variance (constant)."""
    numeric_df = df.select_dtypes(include=[np.number])
    nunique = numeric_df.nunique()
    constants = nunique[nunique <= 1].index.tolist()
    if constants:
        print(f"  [WARN] {len(constants)} constant features detected: {constants}")
    else:
        print("  [OK] No constant features detected.")
    return constants


def validate_duplicate_features(df):
    """Detect columns with identical values (duplicates)."""
    numeric_df = df.select_dtypes(include=[np.number])
    cols = numeric_df.columns.tolist()
    duplicates = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if numeric_df[cols[i]].equals(numeric_df[cols[j]]):
                duplicates.append((cols[i], cols[j]))
    if duplicates:
        print(f"  [WARN] {len(duplicates)} duplicate feature pairs detected:")
        for a, b in duplicates:
            print(f"    - {a} == {b}")
    else:
        print("  [OK] No duplicate features detected.")
    return duplicates


def validate_highly_correlated(df, threshold=0.95):
    """Detect highly correlated feature pairs."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return []
    corr = numeric_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    high_corr = []
    for col in upper.columns:
        for idx in upper.index:
            val = upper.loc[idx, col]
            if pd.notna(val) and val > threshold:
                high_corr.append((idx, col, round(val, 4)))
    if high_corr:
        print(f"  [WARN] {len(high_corr)} highly correlated pairs (>{threshold}):")
        for a, b, v in high_corr[:10]:
            print(f"    - {a} <-> {b}: {v}")
        if len(high_corr) > 10:
            print(f"    ... and {len(high_corr) - 10} more.")
    else:
        print(f"  [OK] No feature pairs exceed {threshold} correlation.")
    return high_corr


def validate_distributions(df):
    """Print basic distribution statistics for numeric features."""
    numeric_df = df.select_dtypes(include=[np.number])
    stats = numeric_df.describe().T
    stats["skew"] = numeric_df.skew()
    stats["kurtosis"] = numeric_df.kurtosis()
    print(
        f"  [INFO] Distribution summary for {len(numeric_df.columns)} numeric features generated."
    )
    return stats


def run_full_validation(df, name="Feature Set"):
    """Run complete validation suite on a DataFrame."""
    print(f"\n{'='*60}")
    print(f"  FEATURE VALIDATION: {name}")
    print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"{'='*60}")

    results = {}
    print("\n1. Missing Values Check:")
    results["missing"] = validate_missing_values(df)

    print("\n2. Constant Features Check:")
    results["constants"] = validate_constant_features(df)

    print("\n3. Duplicate Features Check:")
    results["duplicates"] = validate_duplicate_features(df)

    print("\n4. Highly Correlated Features Check:")
    results["high_corr"] = validate_highly_correlated(df)

    print("\n5. Distribution Statistics:")
    results["distributions"] = validate_distributions(df)

    print(f"\n{'='*60}")
    print(f"  VALIDATION COMPLETE: {name}")
    print(f"{'='*60}\n")
    return results
