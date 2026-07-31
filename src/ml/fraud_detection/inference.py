"""Inference pipeline for production use."""
import joblib
import pandas as pd
import numpy as np
import os
from . import config


class FraudInferencePipeline:
    """Production inference pipeline for fraud detection."""

    def __init__(self, model_name='xgboost'):
        model_path = os.path.join(config.MODELS_DIR, f'{model_name}.joblib')
        feats_path = os.path.join(config.MODELS_DIR, 'selected_features.joblib')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        self.model = joblib.load(model_path)
        if os.path.exists(feats_path):
            self.selected_features = joblib.load(feats_path)
        else:
            self.selected_features = None
        self.model_name = model_name
        self.threshold = 0.5

    def set_threshold(self, threshold):
        self.threshold = threshold

    def _prepare_data(self, X):
        X_clean = X.select_dtypes(include=[np.number]).fillna(0)
        if self.selected_features:
            for col in self.selected_features:
                if col not in X_clean.columns:
                    X_clean[col] = 0
            X_clean = X_clean[self.selected_features]
        return X_clean

    def predict(self, X):
        """Return predictions using the configured threshold."""
        X_clean = self._prepare_data(X)
        probas = self.model.predict_proba(X_clean)[:, 1]
        preds = (probas >= self.threshold).astype(int)
        return preds, probas

    def score(self, X):
        """Return risk scores (0-100) for each row."""
        X_clean = self._prepare_data(X)
        probas = self.model.predict_proba(X_clean)[:, 1]
        return (probas * 100).round(2)

    def decide(self, X):
        """Return full decision output: prediction, score, band, action."""
        preds, probas = self.predict(X)
        scores = (probas * 100).round(2)

        results = []
        for i in range(len(X)):
            score = scores[i]
            if score < 10:
                band, action = 'Low Risk', 'Approve Transaction'
            elif score < 25:
                band, action = 'Low Risk', 'Approve with Monitoring'
            elif score < 50:
                band, action = 'Medium Risk', 'Manual Investigation'
            elif score < 75:
                band, action = 'High Risk', 'Temporary Hold'
            elif score < 90:
                band, action = 'Critical Risk', 'Block Transaction'
            else:
                band, action = 'Critical Risk', 'Escalate to Fraud Team'

            results.append({
                'fraud_prediction': preds[i],
                'fraud_probability': probas[i],
                'risk_score': score,
                'risk_band': band,
                'recommended_action': action,
            })

        return pd.DataFrame(results)
