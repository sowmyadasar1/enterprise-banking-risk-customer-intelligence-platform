"""SHAP explainability: global and local explanations."""
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from . import config
import warnings
warnings.filterwarnings('ignore')


def generate_shap_explanations(best_model, best_name, X_train, X_test, feature_names):
    """Generate SHAP global + local explanations for the best model."""
    print("\n" + "="*70)
    print("  STEP 9: EXPLAINABLE AI (SHAP)")
    print("="*70)
    print(f"  Model: {best_name}")

    X_train_np = X_train.fillna(0).values
    X_test_np = X_test.fillna(0).values

    # Select appropriate explainer
    tree_models = ['RandomForest', 'GradientBoosting', 'XGBoost', 'LightGBM', 'CatBoost', 'DecisionTree']
    if best_name in tree_models:
        print("  Using TreeExplainer...")
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(X_test_np)
        # For binary classifiers, shap_values may be a list or a 3D array
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # class 1 (fraud)
        elif len(np.array(shap_values).shape) == 3:
            shap_values = shap_values[:, :, 1]
    else:
        print("  Using KernelExplainer (sampling 100 background)...")
        background = shap.sample(X_train_np, min(100, len(X_train_np)))
        explainer = shap.KernelExplainer(best_model.predict_proba, background)
        shap_values = explainer.shap_values(X_test_np[:200])
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        X_test_np = X_test_np[:200]
        feature_names = feature_names[:len(X_test_np)]

    # Global feature importance (mean |SHAP|)
    print("\n  [Global Feature Importance]")
    mean_abs = np.abs(shap_values).mean(axis=0)
    importance = pd.Series(mean_abs, index=feature_names).sort_values(ascending=False)
    for feat, val in importance.head(15).items():
        print(f"    {feat}: {val:.4f}")

    # --- SHAP Summary Plot ---
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_test_np, feature_names=feature_names, show=False, max_display=20)
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'shap_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: shap_summary.png")

    # --- SHAP Bar Plot (global importance) ---
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test_np, feature_names=feature_names,
                      plot_type='bar', show=False, max_display=20)
    plt.tight_layout()
    plt.savefig(os.path.join(config.VIS_DIR, 'shap_importance_bar.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: shap_importance_bar.png")

    # --- Waterfall plot for first fraud case ---
    try:
        fraud_indices = np.where(X_test.fillna(0).values[:, -1] if len(X_test.columns) > 0 else [])[0]
        sample_idx = 0  # first test sample
        plt.figure(figsize=(10, 6))
        explanation = shap.Explanation(
            values=shap_values[sample_idx],
            base_values=explainer.expected_value if not isinstance(explainer.expected_value, list)
                        else explainer.expected_value[1],
            data=X_test_np[sample_idx],
            feature_names=feature_names
        )
        shap.waterfall_plot(explanation, show=False, max_display=15)
        plt.tight_layout()
        plt.savefig(os.path.join(config.VIS_DIR, 'shap_waterfall_sample.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: shap_waterfall_sample.png")
    except Exception as e:
        print(f"  [WARN] Waterfall plot skipped: {e}")

    # --- Dependence plot for top feature ---
    try:
        top_feat_idx = np.argmax(mean_abs)
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(top_feat_idx, shap_values, X_test_np,
                             feature_names=feature_names, show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(config.VIS_DIR, 'shap_dependence_top.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: shap_dependence_top.png")
    except Exception as e:
        print(f"  [WARN] Dependence plot skipped: {e}")

    return {
        'shap_values': shap_values,
        'feature_importance': importance,
        'explainer': explainer,
    }
