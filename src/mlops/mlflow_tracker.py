"""
MLOps: MLflow Tracking & Model Registry Integration
"""

import os
import time
import logging
import joblib
import mlflow
import mlflow.xgboost
import mlflow.sklearn
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("mlflow_tracker")

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def wait_for_mlflow():
    """Wait for MLflow to be available before trying to log models."""
    logger.info("Connecting to MLflow Tracking Server at %s", MLFLOW_URI)
    mlflow.set_tracking_uri(MLFLOW_URI)

    retries = 30
    while retries > 0:
        try:
            mlflow.search_experiments()
            logger.info("Successfully connected to MLflow.")
            return True
        except Exception:
            logger.warning("Waiting for MLflow server...")
            time.sleep(2)
            retries -= 1

    logger.error("Could not connect to MLflow server.")
    return False


def register_xgboost(run_name, model_path, registered_name):
    """Log and register an XGBoost model."""
    if not model_path.exists():
        logger.error("Model not found: %s", model_path)
        return

    logger.info("Registering %s from %s", registered_name, model_path.name)
    with mlflow.start_run(run_name=run_name):
        model = joblib.load(model_path)
        mlflow.log_param("model_type", "XGBoost")
        mlflow.log_param("deployment_phase", run_name)

        # Log to MLflow
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=registered_name,
        )
        logger.info("Successfully registered %s", registered_name)


def register_kmeans(run_name, model_path, registered_name):
    """Log and register a Scikit-Learn K-Means model."""
    if not model_path.exists():
        logger.error("Model not found: %s", model_path)
        return

    logger.info("Registering %s from %s", registered_name, model_path.name)
    with mlflow.start_run(run_name=run_name):
        model = joblib.load(model_path)
        mlflow.log_param("model_type", "K-Means")
        mlflow.log_param("deployment_phase", run_name)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=registered_name,
        )
        logger.info("Successfully registered %s", registered_name)


def run_tracker():
    print("\n" + "=" * 70)
    print("  ENTERPRISE MLOPS — MLFLOW MODEL REGISTRY")
    print("=" * 70)

    if not wait_for_mlflow():
        return

    # Set up experiment
    mlflow.set_experiment("Enterprise_Banking_Models")

    # 1. Fraud Detection (Phase 7A)
    fraud_path = (
        PROJECT_ROOT / "src" / "ml" / "fraud_detection" / "models" / "xgboost.joblib"
    )
    register_xgboost("Phase_7A_Fraud", fraud_path, "fraud_detection_model")

    # 2. Loan Default (Phase 7B)
    loan_path = (
        PROJECT_ROOT / "src" / "ml" / "loan_default" / "models" / "xgboost.joblib"
    )
    register_xgboost("Phase_7B_Loan", loan_path, "loan_default_model")

    # 3. Customer Segmentation (Phase 7C)
    seg_path = (
        PROJECT_ROOT
        / "src"
        / "ml"
        / "customer_segmentation"
        / "models"
        / "kmeans_model.joblib"
    )
    register_kmeans("Phase_7C_Segmentation", seg_path, "customer_segmentation_model")

    print("\n  Models successfully ingested into MLflow Registry.")
    print("=" * 70)


if __name__ == "__main__":
    run_tracker()
