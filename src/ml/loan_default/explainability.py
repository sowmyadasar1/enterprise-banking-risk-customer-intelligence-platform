"""SHAP explainability: global and local explanations for loan default."""

import numpy as np
import pandas as pd
import shap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from . import config
import warnings

warnings.filterwarnings("ignore")


def generate_shap_explanations(best_model, best_name, X_train, X_test, feature_names):
    """Generate SHAP global + local explanations for the calibrated model."""
    print("\n" + "=" * 70)
    print("  STEP 10: EXPLAINABLE AI (SHAP)")
    print("=" * 70)
    print(f"  Model: {best_name} (Calibrated)")

    X_train_np = X_train.fillna(0).values
    X_test_np = X_test.fillna(0).values

    # To explain a CalibratedClassifierCV, we typically need to explain the underlying base_estimator.
    # We'll try to extract it. If it fails, we fall back to KernelExplainer on predict_proba.
    try:
        base_estimator = best_model.estimator
        is_tree = best_name in [
            "RandomForest",
            "GradientBoosting",
            "XGBoost",
            "LightGBM",
            "CatBoost",
            "DecisionTree",
        ]
    except AttributeError:
        base_estimator = best_model
        is_tree = False

    if is_tree:
        print("  Using TreeExplainer on base estimator...")
        explainer = shap.TreeExplainer(base_estimator)
        shap_values = explainer.shap_values(X_test_np)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        elif len(np.array(shap_values).shape) == 3:
            shap_values = shap_values[:, :, 1]
    else:
        print("  Using KernelExplainer (sampling 50 background)...")
        background = shap.sample(X_train_np, min(50, len(X_train_np)))

        # It is safer to explain only the positive class probability to avoid multi-output confusion
        def predict_positive_class(X):
            return best_model.predict_proba(X)[:, 1]

        explainer = shap.KernelExplainer(predict_positive_class, background)
        shap_values = explainer.shap_values(X_test_np[:100])

        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        elif len(np.array(shap_values).shape) == 3:
            shap_values = shap_values[:, :, 1]

        X_test_np = X_test_np[:100]
        feature_names = feature_names[: len(X_test_np)]

    # Global feature importance (mean |SHAP|)
    print("\n  [Global Feature Importance]")
    mean_abs = np.abs(shap_values).mean(axis=0)
    importance = pd.Series(mean_abs, index=feature_names).sort_values(ascending=False)
    for feat, val in importance.head(10).items():
        print(f"    {feat}: {val:.4f}")

    # --- SHAP Summary Plot ---
    plt.figure(figsize=(12, 8))
    shap.summary_plot(
        shap_values, X_test_np, feature_names=feature_names, show=False, max_display=20
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(config.VIS_DIR, "shap_summary.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()

    # --- SHAP Bar Plot (global importance) ---
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X_test_np,
        feature_names=feature_names,
        plot_type="bar",
        show=False,
        max_display=20,
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(config.VIS_DIR, "shap_importance_bar.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # --- Waterfall plot for a sample ---
    try:
        sample_idx = 0
        plt.figure(figsize=(10, 6))

        base_val = explainer.expected_value
        if isinstance(base_val, list) or isinstance(base_val, np.ndarray):
            base_val = base_val[1] if len(base_val) > 1 else base_val[0]

        explanation = shap.Explanation(
            values=shap_values[sample_idx],
            base_values=base_val,
            data=X_test_np[sample_idx],
            feature_names=feature_names,
        )
        shap.waterfall_plot(explanation, show=False, max_display=15)
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.VIS_DIR, "shap_waterfall_sample.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()
    except Exception as e:
        print(f"  [WARN] Waterfall plot skipped: {e}")

    # --- Dependence plot for top feature ---
    try:
        top_feat_idx = np.argmax(mean_abs)
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(
            top_feat_idx,
            shap_values,
            X_test_np,
            feature_names=feature_names,
            show=False,
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.VIS_DIR, "shap_dependence_top.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()
    except Exception as e:
        print(f"  [WARN] Dependence plot skipped: {e}")

    print("  Saved: SHAP visualization plots")

    return {
        "shap_values": shap_values,
        "feature_importance": importance,
    }
