"""Comprehensive model evaluation: metrics, curves, calibration curves, Brier score."""
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix,
                             brier_score_loss, roc_curve, precision_recall_curve)
from sklearn.calibration import calibration_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config


def evaluate_model(name, model, X, y):
    """Evaluate a single model and return metrics dict."""
    y_pred = model.predict(X.fillna(0))
    try:
        y_proba = model.predict_proba(X.fillna(0))[:, 1]
    except Exception:
        y_proba = None

    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    metrics = {
        'model': name,
        'accuracy': accuracy_score(y, y_pred),
        'precision': precision_score(y, y_pred, zero_division=0),
        'recall': recall_score(y, y_pred, zero_division=0),
        'f1': f1_score(y, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y, y_proba) if y_proba is not None else 0,
        'pr_auc': average_precision_score(y, y_proba) if y_proba is not None else 0,
        'brier_score': brier_score_loss(y, y_proba) if y_proba is not None else 0,
        'fpr': fp / max(fp + tn, 1),
        'fnr': fn / max(fn + tp, 1),
        'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
    }
    return metrics, y_pred, y_proba


def evaluate_all_models(trained_models, X_test, y_test):
    """Evaluate all models and return comparison DataFrame."""
    print("\n" + "="*70)
    print("  STEP 5: MODEL EVALUATION & CALIBRATION CHECK")
    print("="*70)

    all_metrics = []
    predictions = {}

    for name, model in trained_models.items():
        metrics, y_pred, y_proba = evaluate_model(name, model, X_test, y_test)
        all_metrics.append(metrics)
        predictions[name] = {'y_pred': y_pred, 'y_proba': y_proba}
        print(f"\n  {name}:")
        print(f"    F1={metrics['f1']:.4f}  ROC-AUC={metrics['roc_auc']:.4f}  PR-AUC={metrics['pr_auc']:.4f}")
        print(f"    Brier Score (Calibration Error): {metrics['brier_score']:.4f}")

    comparison = pd.DataFrame(all_metrics).sort_values('pr_auc', ascending=False)
    print("\n  === MODEL COMPARISON (sorted by PR-AUC) ===")
    print(comparison[['model', 'f1', 'roc_auc', 'pr_auc', 'brier_score']].to_string(index=False))

    return comparison, predictions


def plot_roc_curves(trained_models, X_test, y_test):
    """Plot ROC curves for all models."""
    plt.figure(figsize=(10, 8))
    for name, model in trained_models.items():
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            auc = roc_auc_score(y_test, y_proba)
            plt.plot(fpr, tpr, label=f'{name} (AUC={auc:.3f})')
        except Exception:
            pass
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.3)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves — Loan Default Models')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'roc_curves.png'), dpi=150)
    plt.close()


def plot_pr_curves(trained_models, X_test, y_test):
    """Plot Precision-Recall curves for all models."""
    plt.figure(figsize=(10, 8))
    for name, model in trained_models.items():
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
            prec, rec, _ = precision_recall_curve(y_test, y_proba)
            ap = average_precision_score(y_test, y_proba)
            plt.plot(rec, prec, label=f'{name} (AP={ap:.3f})')
        except Exception:
            pass
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curves — Loan Default Models')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'pr_curves.png'), dpi=150)
    plt.close()


def plot_calibration_curves(trained_models, X_test, y_test):
    """Plot Probability Calibration curves."""
    plt.figure(figsize=(10, 8))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0))

    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    
    for name, model in trained_models.items():
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
            fraction_of_positives, mean_predicted_value = calibration_curve(y_test, y_proba, n_bins=10)
            
            ax1.plot(mean_predicted_value, fraction_of_positives, "s-", label=f"{name}")
            ax2.hist(y_proba, range=(0, 1), bins=10, label=name, histtype="step", lw=2)
        except Exception:
            pass
            
    ax1.set_ylabel("Fraction of positives")
    ax1.set_ylim([-0.05, 1.05])
    ax1.legend(loc="lower right")
    ax1.set_title('Calibration Plots (Reliability Curve)')

    ax2.set_xlabel("Mean predicted value")
    ax2.set_ylabel("Count")
    ax2.legend(loc="upper center", ncol=2)

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'calibration_curves.png'), dpi=150)
    plt.close()
    print("  Saved: Evaluation and Calibration plots")
