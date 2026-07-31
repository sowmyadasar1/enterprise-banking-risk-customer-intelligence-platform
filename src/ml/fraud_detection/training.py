"""Training loop with hyperparameter tuning via RandomizedSearchCV."""
import time
import joblib
import os
import numpy as np
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from . import config
import warnings
warnings.filterwarnings('ignore')


def train_all_models(models_dict, X_train, y_train):
    """Train all models with hyperparameter tuning. Returns dict of trained models."""
    print("\n" + "="*70)
    print("  STEP 5: MODEL TRAINING & HYPERPARAMETER TUNING")
    print("="*70)

    trained = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)

    for name, (model, param_grid) in models_dict.items():
        print(f"\n  --- {name} ---")
        start = time.time()

        if param_grid:
            n_iter = min(10, np.prod([len(v) for v in param_grid.values()]))
            search = RandomizedSearchCV(
                model, param_grid, n_iter=int(n_iter), cv=cv,
                scoring='f1', random_state=config.RANDOM_STATE, n_jobs=-1, verbose=0
            )
            search.fit(X_train.fillna(0), y_train)
            best_model = search.best_estimator_
            print(f"    Best params: {search.best_params_}")
            print(f"    Best CV F1:  {search.best_score_:.4f}")
        else:
            best_model = model
            best_model.fit(X_train.fillna(0), y_train)
            print(f"    Baseline model (no tuning)")

        elapsed = time.time() - start
        print(f"    Training time: {elapsed:.1f}s")

        # Save model
        model_path = os.path.join(config.MODELS_DIR, f'{name.lower()}.joblib')
        joblib.dump(best_model, model_path)
        print(f"    Saved: {model_path}")

        trained[name] = best_model

    return trained


def train_isolation_forest(iso_model, X_train):
    """Train isolation forest (unsupervised)."""
    print(f"\n  --- Isolation Forest ---")
    start = time.time()
    iso_model.fit(X_train.fillna(0))
    elapsed = time.time() - start
    print(f"    Training time: {elapsed:.1f}s")

    model_path = os.path.join(config.MODELS_DIR, 'isolation_forest.joblib')
    joblib.dump(iso_model, model_path)
    print(f"    Saved: {model_path}")
    return iso_model
