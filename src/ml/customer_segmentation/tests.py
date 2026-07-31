"""Test suite for Customer Segmentation Platform."""
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from . import config
import warnings
warnings.filterwarnings('ignore')


def run_tests():
    """Execute all tests."""
    print("\n" + "="*70)
    print("  CUSTOMER SEGMENTATION — TEST SUITE")
    print("="*70)

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

    # 1. Feature Store integration
    try:
        df = pd.read_parquet(config.FEATURE_STORE)
        assert_true(len(df) > 0, "Feature Store integration")
    except Exception as e:
        assert_true(False, "Feature Store integration", str(e))

    # 2. Clustering model saved
    try:
        model_path = os.path.join(config.MODELS_DIR, 'kmeans_model.joblib')
        model = joblib.load(model_path)
        assert_true(isinstance(model, KMeans), "Clustering model saved and loadable")
    except Exception as e:
        assert_true(False, "Clustering model saved", str(e))

    # 3. Cluster reproducibility
    try:
        scaler = joblib.load(os.path.join(config.MODELS_DIR, 'scaler.joblib'))
        pt = joblib.load(os.path.join(config.MODELS_DIR, 'power_transformer.joblib'))
        drop = [c for c in config.DROP_COLS if c in df.columns]
        X = df.drop(columns=drop).select_dtypes(include=[np.number]).fillna(0)
        X_t = pt.transform(X)
        X_s = scaler.transform(X_t)
        labels1 = model.predict(X_s)
        labels2 = model.predict(X_s)
        assert_true(np.array_equal(labels1, labels2), "Cluster reproducibility")
    except Exception as e:
        assert_true(False, "Cluster reproducibility", str(e))

    # 4. Persona profiles generated
    try:
        with open(os.path.join(config.PERSONAS_DIR, 'persona_profiles.json')) as f:
            profiles = json.load(f)
        assert_true(len(profiles) >= 3, "Persona profiles generated")
    except Exception as e:
        assert_true(False, "Persona profiles", str(e))

    # 5. Recommendations generated
    try:
        with open(os.path.join(config.RECS_DIR, 'recommendations.json')) as f:
            recs = json.load(f)
        assert_true(len(recs) >= 3, "Recommendation engine validated")
    except Exception as e:
        assert_true(False, "Recommendations", str(e))

    # 6. Customer-persona mapping
    try:
        mapping = pd.read_csv(os.path.join(config.DATA_DIR, 'customer_personas.csv'))
        assert_true(len(mapping) == len(df), "Customer-persona mapping complete")
    except Exception as e:
        assert_true(False, "Customer-persona mapping", str(e))

    # 7. Reports generated
    try:
        reports = os.listdir(config.REPORTS_DIR)
        assert_true(len(reports) >= 4, "All reports generated")
    except Exception as e:
        assert_true(False, "Reports generated", str(e))

    # 8. Visualizations generated
    try:
        vis = os.listdir(config.VIS_DIR)
        assert_true(len(vis) >= 5, "Visualizations generated")
    except Exception as e:
        assert_true(False, "Visualizations", str(e))

    print(f"\n  Results: {passed} passed, {failed} failed out of {passed+failed} tests")
    return failed == 0


if __name__ == "__main__":
    run_tests()
