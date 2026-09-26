"""
Master Orchestrator — Enterprise Fraud Detection Pipeline
Executes the full ML lifecycle: data prep → feature selection → training →
evaluation → threshold optimization → cost analysis → SHAP → risk scoring →
decision engine → reporting → testing.
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, PROJECT_ROOT)

from src.ml.fraud_detection import config
from src.ml.fraud_detection.data_preparation import load_and_validate, prepare_splits
from src.ml.fraud_detection.feature_selection import run_feature_selection
from src.ml.fraud_detection.class_imbalance import (
    analyze_imbalance,
    get_class_weights,
    apply_smote,
)
from src.ml.fraud_detection.models import get_models, get_isolation_forest
from src.ml.fraud_detection.training import train_all_models, train_isolation_forest
from src.ml.fraud_detection.evaluation import (
    evaluate_all_models,
    plot_roc_curves,
    plot_pr_curves,
    plot_confusion_matrices,
)
from src.ml.fraud_detection.threshold_optimizer import optimize_threshold
from src.ml.fraud_detection.cost_analysis import run_cost_analysis
from src.ml.fraud_detection.explainability import generate_shap_explanations
from src.ml.fraud_detection.risk_scoring import generate_risk_scores
from src.ml.fraud_detection.decision_engine import build_decision_engine
from src.ml.fraud_detection.reporting import generate_reports
from src.ml.fraud_detection.tests import run_all_tests


def main():
    print("=" * 70)
    print("  ENTERPRISE FRAUD DETECTION PLATFORM")
    print("  Phase 7A — Full Pipeline Execution")
    print("=" * 70)

    # ===== STEP 1: Data Preparation =====
    df = load_and_validate()
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_splits(df)

    # Store customer IDs for risk scoring later
    drop = [
        c
        for c in config.DROP_COLS + ["fraud_case_count", "total_fraud_loss"]
        if c in df.columns
    ]
    customer_ids_all = df["customer_id"].values

    # ===== STEP 2: Feature Selection =====
    fs_results = run_feature_selection(X_train, y_train)

    # Use selected features for training
    selected = [f for f in fs_results["selected_features"] if f in X_train.columns]
    if len(selected) < 5:
        selected = X_train.columns.tolist()  # fallback
    print(f"\n  Using {len(selected)} features for training.")

    X_train_sel = X_train[selected]
    X_val_sel = X_val[selected]
    X_test_sel = X_test[selected]

    # Save selected features for inference
    import joblib

    joblib.dump(selected, os.path.join(config.MODELS_DIR, "selected_features.joblib"))

    # ===== STEP 3: Class Imbalance =====
    imbalance = analyze_imbalance(y_train)
    class_weights = get_class_weights(y_train)

    # Apply SMOTE to training data
    print("\n  Applying SMOTE to training data...")
    X_train_balanced, y_train_balanced = apply_smote(X_train_sel, y_train)

    # ===== STEP 4 & 5: Model Training with Hyperparameter Tuning =====
    models_dict = get_models(class_weights)
    trained_models = train_all_models(models_dict, X_train_balanced, y_train_balanced)

    # Train Isolation Forest separately (on original, not SMOTE)
    iso_model = get_isolation_forest()
    iso_model = train_isolation_forest(iso_model, X_train_sel)

    # ===== STEP 6: Model Evaluation =====
    comparison, predictions = evaluate_all_models(
        trained_models, X_test_sel, y_test, iso_model
    )

    # Generate visualization plots
    print("\n  Generating evaluation plots...")
    plot_roc_curves(trained_models, X_test_sel, y_test)
    plot_pr_curves(trained_models, X_test_sel, y_test)
    plot_confusion_matrices(trained_models, X_test_sel, y_test)

    # ===== STEP 7: Threshold Optimization (on best model) =====
    best_model_name = comparison.iloc[0]["model"]
    best_model = trained_models.get(best_model_name)
    if best_model is not None:
        try:
            y_proba_best = best_model.predict_proba(X_test_sel.fillna(0))[:, 1]
            threshold_results = optimize_threshold(
                y_test, y_proba_best, best_model_name
            )
            optimal_threshold = threshold_results["best_threshold"]
        except Exception as e:
            print(f"  [WARN] Threshold optimization skipped: {e}")
            threshold_results = None
            optimal_threshold = 0.5
    else:
        threshold_results = None
        optimal_threshold = 0.5

    # ===== STEP 8: Business Cost Analysis =====
    cost_df = run_cost_analysis(comparison, trained_models, X_test_sel, y_test)

    # ===== STEP 9: SHAP Explainability =====
    shap_results = None
    if best_model is not None:
        try:
            shap_results = generate_shap_explanations(
                best_model,
                best_model_name,
                X_train_sel,
                X_test_sel,
                feature_names=selected,
            )
        except Exception as e:
            print(f"  [WARN] SHAP explanations failed: {e}")

    # ===== STEP 10: Risk Scoring (on full dataset) =====
    # Prepare full dataset with selected features
    X_full = df.drop(columns=[c for c in drop + [config.TARGET] if c in df.columns])
    X_full = X_full.select_dtypes(include=["number"]).fillna(0)
    # Align columns
    for col in selected:
        if col not in X_full.columns:
            X_full[col] = 0
    X_full_sel = X_full[selected]

    risk_df = generate_risk_scores(
        best_model, X_full_sel, customer_ids_all, optimal_threshold
    )

    # ===== STEP 11: Decision Engine =====
    decisions_df = build_decision_engine(risk_df)

    # ===== STEP 12: Report Generation =====
    generate_reports(
        comparison,
        cost_df,
        threshold_results,
        shap_results,
        risk_df,
        fs_results,
        best_model_name,
    )

    # ===== STEP 13: Run Tests =====
    print("\n")
    test_passed = run_all_tests()

    # ===== FINAL SUMMARY =====
    print("\n" + "=" * 70)
    print("  FRAUD DETECTION PLATFORM — PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  Models Trained:       {len(trained_models) + 1}")
    print(f"  Best Model:           {best_model_name}")
    print(f"  Best F1:              {comparison.iloc[0]['f1']:.4f}")
    print(f"  Best ROC-AUC:         {comparison.iloc[0]['roc_auc']:.4f}")
    print(f"  Optimal Threshold:    {optimal_threshold:.4f}")
    print(f"  Risk Scores:          {len(risk_df)} customers scored")
    print(f"  Decisions:            {len(decisions_df)} actions generated")
    print(f"  Tests:                {'ALL PASSED' if test_passed else 'SOME FAILED'}")
    print(f"  Reports:              {len(os.listdir(config.REPORTS_DIR))} files")
    print(f"  Visualizations:       {len(os.listdir(config.VIS_DIR))} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
