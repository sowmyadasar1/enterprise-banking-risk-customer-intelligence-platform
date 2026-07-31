"""Model definitions: 9 classifiers for fraud detection."""
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


def get_models(class_weights=None):
    """Return dict of model name -> (model, param_grid) for tuning."""
    w = class_weights or {}

    models = {
        'Dummy': (
            DummyClassifier(strategy='stratified', random_state=42),
            {}
        ),
        'LogisticRegression': (
            LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
            {'C': [0.01, 0.1, 1, 10], 'penalty': ['l2']}
        ),
        'DecisionTree': (
            DecisionTreeClassifier(random_state=42, class_weight='balanced'),
            {'max_depth': [5, 10, 15, 20], 'min_samples_split': [5, 10, 20]}
        ),
        'RandomForest': (
            RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced'),
            {'n_estimators': [100, 200], 'max_depth': [10, 15, 20], 'min_samples_split': [5, 10]}
        ),
        'GradientBoosting': (
            GradientBoostingClassifier(random_state=42),
            {'n_estimators': [100, 200], 'max_depth': [3, 5, 7], 'learning_rate': [0.05, 0.1]}
        ),
        'XGBoost': (
            XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False,
                          scale_pos_weight=w.get(1, 1)),
            {'n_estimators': [100, 200], 'max_depth': [3, 5, 7], 'learning_rate': [0.05, 0.1],
             'subsample': [0.8, 1.0]}
        ),
        'LightGBM': (
            LGBMClassifier(random_state=42, verbose=-1, is_unbalance=True),
            {'n_estimators': [100, 200], 'max_depth': [5, 7, 10], 'learning_rate': [0.05, 0.1],
             'num_leaves': [31, 63]}
        ),
        'CatBoost': (
            CatBoostClassifier(random_state=42, verbose=0, auto_class_weights='Balanced'),
            {'iterations': [100, 200], 'depth': [4, 6, 8], 'learning_rate': [0.05, 0.1]}
        ),
    }
    return models


def get_isolation_forest():
    """Return Isolation Forest for anomaly detection (unsupervised)."""
    return IsolationForest(n_estimators=200, contamination='auto', random_state=42, n_jobs=-1)
