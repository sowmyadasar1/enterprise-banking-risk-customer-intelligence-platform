"""
Feature Selection Module
Implements algorithmic feature selection: Variance Threshold, Correlation Filtering,
Mutual Information, and generates recommended feature sets per ML task.
"""
import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold, mutual_info_classif
import warnings
warnings.filterwarnings('ignore')


def variance_threshold_selection(df, threshold=0.01):
    """Remove features with variance below threshold."""
    numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
    if numeric_df.shape[1] == 0:
        return [], numeric_df.columns.tolist()

    selector = VarianceThreshold(threshold=threshold)
    selector.fit(numeric_df)
    selected = numeric_df.columns[selector.get_support()].tolist()
    dropped = [c for c in numeric_df.columns if c not in selected]
    print(f"  [Variance] Kept {len(selected)}, dropped {len(dropped)} low-variance features.")
    if dropped:
        print(f"    Dropped: {dropped[:10]}")
    return selected, dropped


def correlation_filtering(df, threshold=0.95):
    """Remove one feature from each pair of highly correlated features."""
    numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
    if numeric_df.shape[1] < 2:
        return numeric_df.columns.tolist(), []

    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = set()
    for col in upper.columns:
        correlated = upper.index[upper[col] > threshold].tolist()
        if correlated:
            to_drop.add(col)

    kept = [c for c in numeric_df.columns if c not in to_drop]
    dropped = list(to_drop)
    print(f"  [Correlation] Kept {len(kept)}, dropped {len(dropped)} highly-correlated features.")
    if dropped:
        print(f"    Dropped: {dropped[:10]}")
    return kept, dropped


def mutual_information_ranking(df, target_col, top_n=20):
    """Rank features by mutual information with a binary target."""
    numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
    if target_col not in numeric_df.columns:
        print(f"  [MI] Target '{target_col}' not in numeric columns. Skipping.")
        return pd.Series(dtype=float)

    X = numeric_df.drop(columns=[target_col])
    y = numeric_df[target_col].astype(int)

    if X.shape[1] == 0 or y.nunique() < 2:
        print("  [MI] Insufficient data for MI computation.")
        return pd.Series(dtype=float)

    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    print(f"  [MI] Top {min(top_n, len(mi_series))} features for '{target_col}':")
    for feat, score in mi_series.head(top_n).items():
        print(f"    - {feat}: {score:.4f}")
    return mi_series


def generate_recommended_sets(df):
    """Generate recommended feature sets for each ML task."""
    print("\n" + "=" * 60)
    print("  FEATURE SELECTION REPORT")
    print("=" * 60)

    # Step 1: Variance Threshold
    print("\n--- Step 1: Variance Threshold ---")
    var_kept, var_dropped = variance_threshold_selection(df)

    # Step 2: Correlation Filtering
    print("\n--- Step 2: Correlation Filtering ---")
    corr_kept, corr_dropped = correlation_filtering(df[var_kept] if var_kept else df)

    # Step 3: MI for Fraud Detection
    print("\n--- Step 3: Mutual Information for Fraud Detection ---")
    fraud_mi = pd.Series(dtype=float)
    if 'fraud_risk_indicator' in df.columns:
        fraud_mi = mutual_information_ranking(df, 'fraud_risk_indicator', top_n=15)

    # Step 4: MI for Loan Default
    print("\n--- Step 4: Mutual Information for Loan Default ---")
    loan_mi = pd.Series(dtype=float)
    if 'loan_risk_indicator' in df.columns:
        loan_mi = mutual_information_ranking(df, 'loan_risk_indicator', top_n=15)

    print("\n" + "=" * 60)
    print("  FEATURE SELECTION COMPLETE")
    print("=" * 60)

    return {
        'variance_kept': var_kept,
        'variance_dropped': var_dropped,
        'correlation_kept': corr_kept,
        'correlation_dropped': corr_dropped,
        'fraud_mi': fraud_mi,
        'loan_mi': loan_mi,
    }
