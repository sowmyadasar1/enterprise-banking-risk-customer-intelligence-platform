"""Training loop with hyperparameter tuning and probability calibration."""
import time
import joblib
import os
import numpy as np
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from . import config
import warnings
warnings.filterwarnings('ignore')


def train_all_models(models_dict, X_train, y_train):
    """Train all models with hyperparameter tuning and calibration."""
    print("\n" + "="*70)
    print("  STEP 4: MODEL TRAINING, TUNING & CALIBRATION")
    print("="*70)

    trained = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)

    for name, (model, param_grid) in models_dict.items():
        print(f"\n  --- {name} ---")
        start = time.time()

        # Tuning
        if param_grid:
            n_iter = min(10, np.prod([len(v) for v in param_grid.values()]))
            search = RandomizedSearchCV(
                model, param_grid, n_iter=int(n_iter), cv=cv,
                scoring='f1', random_state=config.RANDOM_STATE, n_jobs=-1, verbose=0
            )
            search.fit(X_train.fillna(0), y_train)
            best_estimator = search.best_estimator_
            print(f"    Best params: {search.best_params_}")
            print(f"    Best CV F1:  {search.best_score_:.4f}")
        else:
            best_estimator = model
            best_estimator.fit(X_train.fillna(0), y_train)
            print(f"    Baseline model (no tuning)")

        # Probability Calibration
        # We calibrate using isotonic regression since we have enough data (7000 rows)
        if name != 'Dummy':
            print("    Calibrating probabilities (Isotonic, 5-fold CV)...")
            calibrated_model = CalibratedClassifierCV(
                estimator=best_estimator, method='isotonic', cv=5
            )
            calibrated_model.fit(X_train.fillna(0), y_train)
        else:
            calibrated_model = best_estimator

        elapsed = time.time() - start
        print(f"    Training & Calibration time: {elapsed:.1f}s")

        # Save model
        model_path = os.path.join(config.MODELS_DIR, f'{name.lower()}.joblib')
        joblib.dump(calibrated_model, model_path)
        print(f"    Saved: {model_path}")

        trained[name] = calibrated_model

    return trained
