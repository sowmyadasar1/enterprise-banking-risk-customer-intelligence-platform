"""Master orchestration script for the Loan Default Prediction Platform."""
import os
import joblib

from . import config
from .data_preparation import load_and_validate, prepare_splits
from .feature_selection import run_feature_selection
from .models import get_models
from .training import train_all_models
from .evaluation import (evaluate_all_models, plot_roc_curves, 
                         plot_pr_curves, plot_calibration_curves)
from .threshold_optimizer import optimize_thresholds
from .cost_analysis import run_cost_analysis
from .risk_scoring import generate_risk_scores
from .decision_engine import build_decision_engine
from .explainability import generate_shap_explanations
from .reporting import generate_reports
from .tests import run_tests


def run_full_pipeline():
    print("\n" + "="*70)
    print("  ENTERPRISE LOAN DEFAULT PREDICTION PLATFORM")
    print("="*70)

    # 1. Data Prep
    df, leakage_cols = load_and_validate()
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_splits(df, leakage_cols)
    customer_ids = df.loc[X_test.index, config.ID_COL].values

    # 2. Feature Selection
    feature_results = run_feature_selection(X_train, y_train)
    selected = feature_results['selected_features']
    print(f"  Using {len(selected)} selected features for modeling.")
    
    X_train_sel = X_train[selected]
    X_val_sel = X_val[selected]
    X_test_sel = X_test[selected]

    # Save selected features for inference
    joblib.dump(selected, os.path.join(config.MODELS_DIR, 'selected_features.joblib'))

    # 3. Class Imbalance (Weights) - we calculate it here for the models
    ratio = (len(y_train) - sum(y_train)) / max(sum(y_train), 1)
    class_weights = {0: 1.0, 1: ratio}

    # 4. Models & Training (with Calibration)
    models_dict = get_models(class_weights)
    trained_models = train_all_models(models_dict, X_train_sel, y_train)

    # 5. Evaluation & Calibration Checks
    comparison_df, predictions = evaluate_all_models(trained_models, X_test_sel, y_test)
    plot_roc_curves(trained_models, X_test_sel, y_test)
    plot_pr_curves(trained_models, X_test_sel, y_test)
    plot_calibration_curves(trained_models, X_test_sel, y_test)

    best_model_name = comparison_df.iloc[0]['model']
    best_model = trained_models[best_model_name]
    best_probas = predictions[best_model_name]['y_proba']

    # 6. Threshold Optimization (Auto-Approve, Review, Auto-Reject)
    thresholds = optimize_thresholds(y_test, best_probas, best_model_name)

    # 7. Business Cost Analysis
    cost_df = run_cost_analysis(comparison_df, trained_models, X_test_sel, y_test, thresholds)

    # 8. SHAP Explainability
    shap_results = generate_shap_explanations(
        best_model, best_model_name, X_train_sel, X_test_sel, selected
    )

    # 9. Risk Scoring
    risk_df = generate_risk_scores(best_model, X_test_sel, customer_ids)

    # 10. Decision Engine
    decisions_df = build_decision_engine(risk_df, thresholds)

    # 11. Reports
    generate_reports(comparison_df, cost_df, thresholds, shap_results,
                     decisions_df, feature_results, best_model_name)

    # 12. Tests
    print("\n" + "="*70)
    print("  RUNNING PIPELINE TESTS")
    print("="*70)
    run_tests()

    print("\n" + "="*70)
    print("  LOAN DEFAULT PREDICTION PLATFORM — PIPELINE COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_full_pipeline()
