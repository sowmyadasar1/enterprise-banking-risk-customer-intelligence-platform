"""Tests for the fraud detection pipeline."""

import os
import sys
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, PROJECT_ROOT)

from src.ml.fraud_detection import config
from src.ml.fraud_detection.inference import FraudInferencePipeline


def test_feature_store_integration():
    """Test that Feature Store loads correctly."""
    df = pd.read_parquet(config.FEATURE_STORE)
    assert len(df) > 0, "Feature store is empty"
    assert config.TARGET in df.columns, f"Target '{config.TARGET}' missing"
    print("  ✓ Feature Store integration")


def test_models_saved():
    """Test that trained models exist on disk."""
    model_files = [f for f in os.listdir(config.MODELS_DIR) if f.endswith(".joblib")]
    assert len(model_files) >= 5, f"Expected ≥5 models, found {len(model_files)}"
    print(f"  ✓ {len(model_files)} model files saved")


def test_model_loading():
    """Test that models can be loaded."""
    for f in os.listdir(config.MODELS_DIR):
        if f.endswith(".joblib"):
            model = joblib.load(os.path.join(config.MODELS_DIR, f))
            assert model is not None, f"Failed to load {f}"
    print("  ✓ All models load successfully")


def test_prediction_consistency():
    """Test that predictions are deterministic."""
    df = pd.read_parquet(config.FEATURE_STORE)
    drop = [
        c
        for c in config.DROP_COLS
        + ["fraud_case_count", "total_fraud_loss", config.TARGET]
        if c in df.columns
    ]
    X = df.drop(columns=drop).select_dtypes(include=[np.number]).fillna(0).head(100)

    model_files = [
        f.replace(".joblib", "")
        for f in os.listdir(config.MODELS_DIR)
        if f.endswith(".joblib") and "isolation" not in f and "dummy" not in f
    ]
    if model_files:
        pipe = FraudInferencePipeline(model_files[0])
        p1, _ = pipe.predict(X)
        p2, _ = pipe.predict(X)
        assert np.array_equal(p1, p2), "Predictions are not deterministic"
    print("  ✓ Prediction consistency")


def test_inference_pipeline():
    """Test the inference pipeline class."""
    model_files = [
        f.replace(".joblib", "")
        for f in os.listdir(config.MODELS_DIR)
        if f.endswith(".joblib") and "isolation" not in f and "dummy" not in f
    ]
    if not model_files:
        print("  ⚠ No models for inference test")
        return

    pipe = FraudInferencePipeline(model_files[0])
    df = pd.read_parquet(config.FEATURE_STORE)
    drop = [
        c
        for c in config.DROP_COLS
        + ["fraud_case_count", "total_fraud_loss", config.TARGET]
        if c in df.columns
    ]
    X = df.drop(columns=drop).select_dtypes(include=[np.number]).fillna(0).head(10)

    preds, probas = pipe.predict(X)
    assert len(preds) == 10
    assert all(p in [0, 1] for p in preds)

    decisions = pipe.decide(X)
    assert "risk_band" in decisions.columns
    assert "recommended_action" in decisions.columns
    print("  ✓ Inference pipeline")


def test_risk_scores():
    """Test risk score output exists."""
    risk_path = os.path.join(config.DATA_DIR, "risk_scores.csv")
    if os.path.exists(risk_path):
        df = pd.read_csv(risk_path)
        assert "risk_score" in df.columns
        assert "risk_band" in df.columns
        assert df["risk_score"].between(0, 100).all()
        print("  ✓ Risk scores validated")
    else:
        print("  ⚠ Risk scores not yet generated")


def test_decision_engine():
    """Test decision engine output."""
    dec_path = os.path.join(config.DATA_DIR, "decisions.csv")
    if os.path.exists(dec_path):
        df = pd.read_csv(dec_path)
        assert "recommended_action" in df.columns
        assert "explanation" in df.columns
        assert len(df) > 0
        print("  ✓ Decision engine validated")
    else:
        print("  ⚠ Decisions not yet generated")


def test_reports_exist():
    """Test that reports were generated."""
    expected = ["model_comparison.md", "business_impact.md", "executive_summary.md"]
    for fname in expected:
        path = os.path.join(config.REPORTS_DIR, fname)
        assert os.path.exists(path), f"Missing report: {fname}"
    print("  ✓ All reports generated")


def run_all_tests():
    """Run the full test suite."""
    print("\n" + "=" * 70)
    print("  FRAUD DETECTION PLATFORM — TEST SUITE")
    print("=" * 70 + "\n")

    tests = [
        test_feature_store_integration,
        test_models_saved,
        test_model_loading,
        test_prediction_consistency,
        test_inference_pipeline,
        test_risk_scores,
        test_decision_engine,
        test_reports_exist,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test_fn.__name__}: {e}")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
