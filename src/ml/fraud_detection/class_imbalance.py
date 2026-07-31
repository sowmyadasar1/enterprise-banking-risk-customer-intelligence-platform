"""Class imbalance analysis and handling strategies."""
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


def analyze_imbalance(y_train):
    """Analyze and report class imbalance."""
    print("\n" + "="*70)
    print("  STEP 3: CLASS IMBALANCE ANALYSIS")
    print("="*70)

    counts = np.bincount(y_train.astype(int))
    total = len(y_train)
    ratio = counts[0] / max(counts[1], 1)

    print(f"  Class 0 (Legit):  {counts[0]} ({counts[0]/total*100:.1f}%)")
    print(f"  Class 1 (Fraud):  {counts[1]} ({counts[1]/total*100:.1f}%)")
    print(f"  Imbalance Ratio:  {ratio:.1f}:1")

    if ratio > 10:
        print("  Severity: SEVERE imbalance")
    elif ratio > 3:
        print("  Severity: MODERATE imbalance")
    else:
        print("  Severity: MILD imbalance")

    return {'counts': counts, 'ratio': ratio}


def get_class_weights(y_train):
    """Compute balanced class weights."""
    classes = np.unique(y_train)
    weights = compute_class_weight('balanced', classes=classes, y=y_train)
    weight_dict = dict(zip(classes.astype(int), weights))
    print(f"  Class weights: {weight_dict}")
    return weight_dict


def apply_smote(X_train, y_train):
    """Apply SMOTE oversampling."""
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_train, y_train)
    print(f"  SMOTE: {len(X_train)} -> {len(X_res)} samples")
    return X_res, y_res


def apply_undersample(X_train, y_train):
    """Apply random undersampling."""
    rus = RandomUnderSampler(random_state=42)
    X_res, y_res = rus.fit_resample(X_train, y_train)
    print(f"  Undersample: {len(X_train)} -> {len(X_res)} samples")
    return X_res, y_res


def apply_oversample(X_train, y_train):
    """Apply random oversampling."""
    ros = RandomOverSampler(random_state=42)
    X_res, y_res = ros.fit_resample(X_train, y_train)
    print(f"  Oversample: {len(X_train)} -> {len(X_res)} samples")
    return X_res, y_res
