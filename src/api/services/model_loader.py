"""
Model Loader — Lazy-loading Singleton registry for all ML model artifacts.
Models are loaded on first access and cached in memory for subsequent requests.
"""

import json
import logging
import joblib
from pathlib import Path
from typing import Optional, Dict, Any
from ..config import (
    FRAUD_MODEL_DIR,
    LOAN_MODEL_DIR,
    SEGMENT_MODEL_DIR,
    FORECAST_MODEL_DIR,
    PERSONA_PATH,
)

logger = logging.getLogger("api.model_loader")


class ModelManager:
    """
    Thread-safe singleton that lazily loads and caches ML artifacts.

    Usage:
        manager = ModelManager()
        fraud_model = manager.get_fraud_model()
    """

    _instance: Optional["ModelManager"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if ModelManager._initialized:
            return
        ModelManager._initialized = True
        self._cache: Dict[str, Any] = {}
        self._status: Dict[str, bool] = {
            "fraud": False,
            "loan_default": False,
            "segmentation": False,
            "forecasting": False,
        }
        logger.info("ModelManager initialized (lazy loading mode)")

    # ─── Private Loader ─────────────────────────────────────────────
    def _load(self, key: str, path: Path, loader: str = "joblib") -> Any:
        """Load an artifact from disk, cache it, and return it."""
        if key in self._cache:
            return self._cache[key]

        if not path.exists():
            logger.error("Artifact not found: %s", path)
            return None

        try:
            if loader == "joblib":
                obj = joblib.load(path)
            elif loader == "statsmodels":
                from statsmodels.tsa.arima.model import ARIMAResultsWrapper
                import pickle

                with open(path, "rb") as f:
                    obj = pickle.load(f)
            elif loader == "json":
                with open(path, "r") as f:
                    obj = json.load(f)
            else:
                raise ValueError(f"Unknown loader: {loader}")

            self._cache[key] = obj
            logger.info("Loaded artifact: %s from %s", key, path.name)
            return obj
        except Exception as e:
            logger.error("Failed to load %s: %s", key, str(e))
            return None

    # ─── Fraud Detection ────────────────────────────────────────────
    def get_fraud_model(self):
        model = self._load("fraud_model", FRAUD_MODEL_DIR / "xgboost.joblib")
        if model is not None:
            self._status["fraud"] = True
        return model

    def get_fraud_features(self):
        return self._load(
            "fraud_features", FRAUD_MODEL_DIR / "selected_features.joblib"
        )

    # ─── Loan Default ───────────────────────────────────────────────
    def get_loan_model(self):
        model = self._load("loan_model", LOAN_MODEL_DIR / "xgboost.joblib")
        if model is not None:
            self._status["loan_default"] = True
        return model

    def get_loan_features(self):
        return self._load("loan_features", LOAN_MODEL_DIR / "selected_features.joblib")

    # ─── Customer Segmentation ──────────────────────────────────────
    def get_segmentation_model(self):
        model = self._load("kmeans_model", SEGMENT_MODEL_DIR / "kmeans_model.joblib")
        if model is not None:
            self._status["segmentation"] = True
        return model

    def get_segmentation_scaler(self):
        return self._load("seg_scaler", SEGMENT_MODEL_DIR / "scaler.joblib")

    def get_segmentation_transformer(self):
        return self._load(
            "seg_transformer", SEGMENT_MODEL_DIR / "power_transformer.joblib"
        )

    def get_segmentation_pca(self):
        return self._load("seg_pca", SEGMENT_MODEL_DIR / "pca_2d.joblib")

    def get_personas(self) -> dict:
        return self._load("personas", PERSONA_PATH, loader="json") or {}

    # ─── Forecasting ────────────────────────────────────────────────
    def get_forecast_model(self, target: str):
        key = f"arima_{target}"
        path = FORECAST_MODEL_DIR / f"arima_{target}.pkl"
        model = self._load(key, path, loader="statsmodels")
        if model is not None:
            self._status["forecasting"] = True
        return model

    # ─── Status ─────────────────────────────────────────────────────
    def get_status(self) -> Dict[str, bool]:
        return dict(self._status)

    def preload_all(self):
        """Eagerly load all models (useful for startup validation)."""
        logger.info("Preloading all models...")
        self.get_fraud_model()
        self.get_fraud_features()
        self.get_loan_model()
        self.get_loan_features()
        self.get_segmentation_model()
        self.get_segmentation_scaler()
        self.get_segmentation_transformer()
        self.get_personas()
        for target in ["transaction_volume", "revenue", "loan_demand", "new_customers"]:
            self.get_forecast_model(target)
        logger.info("All models preloaded. Status: %s", self._status)
