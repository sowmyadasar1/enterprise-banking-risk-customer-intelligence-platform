"""Threshold optimization: find business-optimal decision threshold."""
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, f1_score, precision_score, recall_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config


def optimize_threshold(y_true, y_proba, model_name="Best Model"):
    """Find optimal threshold balancing precision/recall for fraud detection."""
    print("\n" + "="*70)
    print("  STEP 7: THRESHOLD OPTIMIZATION")
    print("="*70)

    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    # F1 for each threshold
    f1s = 2 * (precisions[:-1] * recalls[:-1]) / (precisions[:-1] + recalls[:-1] + 1e-8)

    # Find threshold that maximizes F1
    best_idx = np.argmax(f1s)
    best_threshold = thresholds[best_idx]
    best_f1 = f1s[best_idx]

    # Also find threshold where recall >= 0.8 (business requirement: catch most fraud)
    recall_mask = recalls[:-1] >= 0.8
    if recall_mask.any():
        # Among those with recall >= 0.8, pick highest precision
        candidates = np.where(recall_mask)[0]
        high_recall_idx = candidates[np.argmax(precisions[:-1][candidates])]
        high_recall_threshold = thresholds[high_recall_idx]
    else:
        high_recall_threshold = best_threshold

    print(f"\n  Model: {model_name}")
    print(f"  Max-F1 Threshold:      {best_threshold:.4f} (F1={best_f1:.4f})")
    print(f"  High-Recall Threshold: {high_recall_threshold:.4f} (Recall≥80%)")

    # Evaluate at both thresholds
    for name, thresh in [("Max-F1", best_threshold), ("High-Recall", high_recall_threshold)]:
        y_pred = (y_proba >= thresh).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f = f1_score(y_true, y_pred, zero_division=0)
        print(f"    {name}: Precision={p:.4f} Recall={r:.4f} F1={f:.4f}")

    # Plot threshold analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(thresholds, precisions[:-1], label='Precision', color='blue')
    ax1.plot(thresholds, recalls[:-1], label='Recall', color='red')
    ax1.plot(thresholds, f1s, label='F1', color='green', linewidth=2)
    ax1.axvline(best_threshold, color='green', linestyle='--', alpha=0.7, label=f'Best F1={best_f1:.3f}')
    ax1.set_xlabel('Threshold')
    ax1.set_ylabel('Score')
    ax1.set_title('Precision / Recall / F1 vs Threshold')
    ax1.legend()

    # FPR vs threshold
    y_pred_all = np.array([(y_proba >= t).astype(int) for t in thresholds]).T
    fprs = []
    for i, t in enumerate(thresholds):
        yp = (y_proba >= t).astype(int)
        fp = ((yp == 1) & (y_true == 0)).sum()
        tn = ((yp == 0) & (y_true == 0)).sum()
        fprs.append(fp / max(fp + tn, 1))
    ax2.plot(thresholds, fprs, color='orange', linewidth=2)
    ax2.axhline(0.05, color='red', linestyle='--', alpha=0.5, label='5% FPR Target')
    ax2.axvline(best_threshold, color='green', linestyle='--', alpha=0.7)
    ax2.set_xlabel('Threshold')
    ax2.set_ylabel('False Positive Rate')
    ax2.set_title('FPR vs Threshold')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'threshold_optimization.png'), dpi=150)
    plt.close()
    print("  Saved: threshold_optimization.png")

    return {
        'best_threshold': best_threshold,
        'best_f1': best_f1,
        'high_recall_threshold': high_recall_threshold,
        'thresholds': thresholds,
        'precisions': precisions,
        'recalls': recalls,
        'f1s': f1s,
    }
