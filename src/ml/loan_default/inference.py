"""Inference pipeline for production use (Loan Default)."""
import joblib
import pandas as pd
import numpy as np
import os
from . import config


class LoanInferencePipeline:
    """Production inference pipeline for loan default prediction."""

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
        self.auto_approve_thresh = 0.2
        self.auto_reject_thresh = 0.8

    def set_thresholds(self, auto_approve, auto_reject):
        self.auto_approve_thresh = auto_approve
        self.auto_reject_thresh = auto_reject

    def _prepare_data(self, X):
        X_clean = X.select_dtypes(include=[np.number]).fillna(0)
        if self.selected_features:
            for col in self.selected_features:
                if col not in X_clean.columns:
                    X_clean[col] = 0
            X_clean = X_clean[self.selected_features]
        return X_clean

    def predict_proba(self, X):
        """Return calibrated probabilities of default."""
        X_clean = self._prepare_data(X)
        return self.model.predict_proba(X_clean)[:, 1]

    def score(self, X):
        """Return credit risk scores (0-100) for each row."""
        probas = self.predict_proba(X)
        return (probas * 100).round(2)

    def decide(self, X):
        """Return full decision output: prediction, score, band, action."""
        probas = self.predict_proba(X)
        scores = (probas * 100).round(2)

        results = []
        for i in range(len(X)):
            prob = probas[i]
            score = scores[i]
            
            if score < 10:
                band = 'Very Low Risk'
            elif score < 25:
                band = 'Low Risk'
            elif score < 50:
                band = 'Medium Risk'
            elif score < 80:
                band = 'High Risk'
            else:
                band = 'Very High Risk'

            if prob < self.auto_approve_thresh:
                action, tier = 'Approve Loan', 'Auto-Approve'
            elif prob >= self.auto_reject_thresh:
                action, tier = 'Reject Loan', 'Auto-Reject'
            elif prob < (self.auto_approve_thresh + self.auto_reject_thresh)/2:
                action, tier = 'Approve with Conditions', 'Manual Review'
            else:
                action, tier = 'Request Additional Documents', 'Manual Review'

            results.append({
                'default_probability': prob,
                'credit_risk_score': score,
                'risk_category': band,
                'recommended_action': action,
                'decision_tier': tier
            })

        return pd.DataFrame(results)
