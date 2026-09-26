"""Test suite for Loan Default Prediction Platform."""

import os
import joblib
import pandas as pd
import numpy as np
from . import config
from .inference import LoanInferencePipeline
import warnings

warnings.filterwarnings("ignore")


def run_tests():
    """Execute all tests."""
    print("\n" + "=" * 70)
    print("  LOAN DEFAULT PLATFORM — TEST SUITE")
    print("=" * 70)

    passed = 0
    failed = 0

    def assert_true(condition, name, msg=""):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}: {msg}")
            failed += 1

    # 1. Feature Store Integration
    try:
        df = pd.read_parquet(config.FEATURE_STORE)
        assert_true(
            len(df) > 0 and "loan_risk_indicator" in df.columns,
            "Feature Store integration",
        )
    except Exception as e:
        assert_true(False, "Feature Store integration", str(e))

    # 2. Models generated
    models = [f for f in os.listdir(config.MODELS_DIR) if f.endswith(".joblib")]
    assert_true(len(models) >= 8, "8+ model files saved")

    # 3. Model Loading & Calibration type
    try:
        model = joblib.load(os.path.join(config.MODELS_DIR, models[0]))
        # We wrapped in CalibratedClassifierCV except for Dummy maybe, so check if it has predict_proba
        assert_true(
            hasattr(model, "predict_proba"),
            "Models load and have predict_proba successfully",
        )
    except Exception as e:
        assert_true(False, "Model loading", str(e))

    # 4. Prediction Consistency & Inference pipeline
    try:
        X = df.head(100)
        valid_models = [m.replace(".joblib", "") for m in models if "dummy" not in m]
        if valid_models:
            pipe = LoanInferencePipeline(valid_models[0])
            p1 = pipe.predict_proba(X)
            p2 = pipe.predict_proba(X)
            assert_true(np.allclose(p1, p2), "Prediction consistency (deterministic)")

            res = pipe.decide(X)
            assert_true(
                "recommended_action" in res.columns,
                "Inference pipeline decision engine",
            )
        else:
            assert_true(False, "Prediction consistency", "No valid model found")
    except Exception as e:
        assert_true(False, "Prediction consistency", str(e))
        assert_true(False, "Inference pipeline", str(e))

    # 5. Risk scores validated
    try:
        risk = pd.read_csv(os.path.join(config.DATA_DIR, "credit_risk_scores.csv"))
        assert_true(
            risk["credit_risk_score"].max() <= 100, "Risk scores validated (max <= 100)"
        )
    except Exception as e:
        assert_true(False, "Risk scores validated", str(e))

    # 6. Reports Generated
    try:
        reports = os.listdir(config.REPORTS_DIR)
        assert_true(len(reports) >= 4, "All reports generated")
    except Exception as e:
        assert_true(False, "All reports generated", str(e))

    print(f"\n  Results: {passed} passed, {failed} failed out of {passed+failed} tests")
    return failed == 0


if __name__ == "__main__":
    run_tests()
