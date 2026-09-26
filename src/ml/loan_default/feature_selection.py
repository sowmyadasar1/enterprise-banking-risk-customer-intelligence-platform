"""Feature selection: correlation, MI, tree importance, RFE."""

import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif, RFE
from sklearn.ensemble import RandomForestClassifier
import warnings

warnings.filterwarnings("ignore")


def run_feature_selection(X_train, y_train):
    """Run multi-method feature selection and return recommended features."""
    print("\n" + "=" * 70)
    print("  STEP 2: FEATURE SELECTION")
    print("=" * 70)
    results = {}

    # 1. Correlation filtering
    print("\n  [Correlation Filtering]")
    corr = X_train.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > 0.95)]
    results["corr_dropped"] = to_drop
    print(f"    Dropped {len(to_drop)} features with >0.95 correlation")

    # 2. Mutual Information
    print("\n  [Mutual Information]")
    mi = mutual_info_classif(X_train.fillna(0), y_train, random_state=42)
    mi_series = pd.Series(mi, index=X_train.columns).sort_values(ascending=False)
    results["mi_scores"] = mi_series
    print(f"    Top 10 by MI:")
    for feat, score in mi_series.head(10).items():
        print(f"      {feat}: {score:.4f}")

    # 3. Tree-based importance
    print("\n  [Tree-Based Importance]")
    rf = RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1, max_depth=10
    )
    rf.fit(X_train.fillna(0), y_train)
    importances = pd.Series(rf.feature_importances_, index=X_train.columns).sort_values(
        ascending=False
    )
    results["tree_importance"] = importances
    print(f"    Top 10 by RF importance:")
    for feat, score in importances.head(10).items():
        print(f"      {feat}: {score:.4f}")

    # 4. Permutation importance
    print("\n  [Permutation Importance]")
    from sklearn.inspection import permutation_importance

    perm = permutation_importance(
        rf, X_train.fillna(0), y_train, n_repeats=5, random_state=42, n_jobs=-1
    )
    perm_imp = pd.Series(perm.importances_mean, index=X_train.columns).sort_values(
        ascending=False
    )
    results["perm_importance"] = perm_imp
    print(f"    Top 10 by permutation importance:")
    for feat, score in perm_imp.head(10).items():
        print(f"      {feat}: {score:.4f}")

    # 5. RFE (top 20)
    print("\n  [Recursive Feature Elimination]")
    rfe_estimator = RandomForestClassifier(
        n_estimators=50, random_state=42, max_depth=8, n_jobs=-1
    )
    n_select = min(20, X_train.shape[1])
    rfe = RFE(rfe_estimator, n_features_to_select=n_select, step=5)
    rfe.fit(X_train.fillna(0), y_train)
    rfe_selected = X_train.columns[rfe.support_].tolist()
    results["rfe_selected"] = rfe_selected
    print(f"    RFE selected {len(rfe_selected)} features.")

    # Combine: union of top-20 from each method
    top_mi = set(mi_series.head(20).index)
    top_tree = set(importances.head(20).index)
    top_perm = set(perm_imp.head(20).index)
    top_rfe = set(rfe_selected)
    consensus = top_mi | top_tree | top_perm | top_rfe
    # Remove correlated drops
    final = [f for f in consensus if f not in to_drop]
    results["selected_features"] = sorted(final)

    print(f"\n  [Final Selection] {len(final)} features selected via consensus.")
    return results
