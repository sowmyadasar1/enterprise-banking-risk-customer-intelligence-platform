"""Comprehensive model evaluation: metrics, curves, confusion matrices."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    matthews_corrcoef,
    classification_report,
    roc_curve,
    precision_recall_curve,
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from . import config


def evaluate_model(name, model, X, y, is_isolation=False):
    """Evaluate a single model and return metrics dict."""
    if is_isolation:
        preds_raw = model.predict(X.fillna(0))
        y_pred = np.where(preds_raw == -1, 1, 0)  # -1 = anomaly = fraud
        y_proba = None
    else:
        y_pred = model.predict(X.fillna(0))
        try:
            y_proba = model.predict_proba(X.fillna(0))[:, 1]
        except Exception:
            y_proba = None

    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y, y_pred),
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "f1": f1_score(y, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y, y_proba) if y_proba is not None else 0,
        "pr_auc": average_precision_score(y, y_proba) if y_proba is not None else 0,
        "mcc": matthews_corrcoef(y, y_pred),
        "fpr": fp / max(fp + tn, 1),
        "fnr": fn / max(fn + tp, 1),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }
    return metrics, y_pred, y_proba


def evaluate_all_models(trained_models, X_test, y_test, iso_model=None):
    """Evaluate all models and return comparison DataFrame."""
    print("\n" + "=" * 70)
    print("  STEP 6: MODEL EVALUATION")
    print("=" * 70)

    all_metrics = []
    predictions = {}

    for name, model in trained_models.items():
        metrics, y_pred, y_proba = evaluate_model(name, model, X_test, y_test)
        all_metrics.append(metrics)
        predictions[name] = {"y_pred": y_pred, "y_proba": y_proba}
        print(f"\n  {name}:")
        print(
            f"    Accuracy={metrics['accuracy']:.4f}  Precision={metrics['precision']:.4f}  "
            f"Recall={metrics['recall']:.4f}  F1={metrics['f1']:.4f}"
        )
        print(
            f"    ROC-AUC={metrics['roc_auc']:.4f}  PR-AUC={metrics['pr_auc']:.4f}  "
            f"MCC={metrics['mcc']:.4f}"
        )
        print(
            f"    TP={metrics['tp']}  FP={metrics['fp']}  TN={metrics['tn']}  FN={metrics['fn']}"
        )

    # Isolation Forest
    if iso_model is not None:
        metrics, y_pred, _ = evaluate_model(
            "IsolationForest", iso_model, X_test, y_test, is_isolation=True
        )
        all_metrics.append(metrics)
        predictions["IsolationForest"] = {"y_pred": y_pred, "y_proba": None}
        print(f"\n  IsolationForest:")
        print(
            f"    Accuracy={metrics['accuracy']:.4f}  Precision={metrics['precision']:.4f}  "
            f"Recall={metrics['recall']:.4f}  F1={metrics['f1']:.4f}"
        )

    comparison = pd.DataFrame(all_metrics).sort_values("f1", ascending=False)
    print("\n  === MODEL COMPARISON (sorted by F1) ===")
    print(
        comparison[
            ["model", "accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]
        ].to_string(index=False)
    )

    return comparison, predictions


def plot_roc_curves(trained_models, X_test, y_test):
    """Plot ROC curves for all models."""
    plt.figure(figsize=(10, 8))
    for name, model in trained_models.items():
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            auc = roc_auc_score(y_test, y_proba)
            plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
        except Exception:
            pass
    plt.plot([0, 1], [0, 1], "k--", alpha=0.3)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves — Fraud Detection Models")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "roc_curves.png"), dpi=150)
    plt.close()
    print("  Saved: roc_curves.png")


def plot_pr_curves(trained_models, X_test, y_test):
    """Plot Precision-Recall curves for all models."""
    plt.figure(figsize=(10, 8))
    for name, model in trained_models.items():
        try:
            y_proba = model.predict_proba(X_test.fillna(0))[:, 1]
            prec, rec, _ = precision_recall_curve(y_test, y_proba)
            ap = average_precision_score(y_test, y_proba)
            plt.plot(rec, prec, label=f"{name} (AP={ap:.3f})")
        except Exception:
            pass
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curves — Fraud Detection Models")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "pr_curves.png"), dpi=150)
    plt.close()
    print("  Saved: pr_curves.png")


def plot_confusion_matrices(trained_models, X_test, y_test):
    """Plot confusion matrices for top models."""
    n = len(trained_models)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = np.array(axes).flatten() if n > 1 else [axes]

    for idx, (name, model) in enumerate(trained_models.items()):
        if idx >= len(axes):
            break
        y_pred = model.predict(X_test.fillna(0))
        cm = confusion_matrix(y_test, y_pred)
        ax = axes[idx]
        im = ax.imshow(cm, cmap="Blues")
        ax.set_title(name, fontsize=10)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j,
                    i,
                    str(cm[i, j]),
                    ha="center",
                    va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black",
                )

    for idx in range(len(trained_models), len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, "confusion_matrices.png"), dpi=150)
    plt.close()
    print("  Saved: confusion_matrices.png")
