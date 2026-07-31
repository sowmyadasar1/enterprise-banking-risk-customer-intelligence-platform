"""Threshold optimization: multi-tier thresholds for Auto-Approve, Review, and Auto-Reject."""
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config


def optimize_thresholds(y_true, y_proba, model_name="Best Model"):
    """Find multiple thresholds for banking approval workflows."""
    print("\n" + "="*70)
    print("  STEP 6: THRESHOLD OPTIMIZATION (MULTI-TIER)")
    print("="*70)

    fpr, tpr, thresholds_roc = roc_curve(y_true, y_proba)
    
    # Threshold 1: Auto-Approve (Very Low FPR so we don't accidentally approve defaults)
    # Target: FPR <= 5% (i.e. of the actual defaults, we only wrongly approve 5%)
    # Note: FPR = FP / (FP + TN). In loan default context: 
    # Positive = Default, Negative = Good Loan. 
    # FPR is % of Good Loans wrongly classified as Default? No.
    # Wait, 1 = Default, 0 = Good.
    # FP = Predict Default (Reject) but actually Good.
    # TN = Predict Good (Approve) and actually Good.
    # FN = Predict Good (Approve) but actually Default.
    # TP = Predict Default (Reject) and actually Default.
    # So we want to limit FN (Auto-Approve defaults). 
    # FNR = FN / (FN + TP) = 1 - TPR. We want TPR >= 0.95 (catch 95% of defaults), so we only miss 5%.
    
    # Auto-Approve: we want to auto-approve only those with VERY LOW probability of default.
    # Let's find threshold where TPR >= 0.95 (so we reject/review 95% of defaults).
    # Then anything below this threshold is Auto-Approve.
    tpr_mask = tpr >= 0.95
    if tpr_mask.any():
        auto_approve_idx = np.where(tpr_mask)[0][0] # first threshold that achieves 95% TPR
        auto_approve_thresh = thresholds_roc[auto_approve_idx]
    else:
        auto_approve_thresh = 0.2
        
    # Auto-Reject: we want to auto-reject only those with VERY HIGH probability of default.
    # Let's target Precision >= 0.90 for defaults (so if we auto-reject, 90% chance they would have defaulted).
    precisions, recalls, thresholds_pr = precision_recall_curve(y_true, y_proba)
    prec_mask = precisions[:-1] >= 0.90
    if prec_mask.any():
        auto_reject_idx = np.where(prec_mask)[0][0]
        auto_reject_thresh = thresholds_pr[auto_reject_idx]
    else:
        # Fallback to a high threshold if 90% precision isn't reached
        auto_reject_thresh = 0.8
        
    # Ensure thresholds make sense
    auto_approve_thresh = min(auto_approve_thresh, 0.4)
    auto_reject_thresh = max(auto_reject_thresh, auto_approve_thresh + 0.1)

    print(f"\n  Model: {model_name}")
    print(f"  Auto-Approve Threshold: < {auto_approve_thresh:.4f}")
    print(f"  Manual Review Range:      {auto_approve_thresh:.4f} to {auto_reject_thresh:.4f}")
    print(f"  Auto-Reject Threshold:  >= {auto_reject_thresh:.4f}")

    # Plot threshold bands
    plt.figure(figsize=(10, 6))
    plt.hist(y_proba[y_true == 0], bins=50, alpha=0.5, label='Actual Good Loans', color='green', density=True)
    plt.hist(y_proba[y_true == 1], bins=50, alpha=0.5, label='Actual Defaults', color='red', density=True)
    plt.axvline(auto_approve_thresh, color='blue', linestyle='--', linewidth=2, label='Auto-Approve Max')
    plt.axvline(auto_reject_thresh, color='black', linestyle='--', linewidth=2, label='Auto-Reject Min')
    plt.axvspan(auto_approve_thresh, auto_reject_thresh, alpha=0.2, color='yellow', label='Manual Review')
    plt.xlabel('Predicted Default Probability')
    plt.ylabel('Density')
    plt.title('Loan Default Probability Distributions & Decision Tiers')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'threshold_tiers.png'), dpi=150)
    plt.close()
    
    return {
        'auto_approve_thresh': auto_approve_thresh,
        'auto_reject_thresh': auto_reject_thresh
    }
