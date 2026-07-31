# MLflow Model Registry Guide

The Enterprise Platform uses MLflow to transition machine learning models from local `.joblib`/`.pkl` artifacts into a managed, version-controlled Model Registry.

## MLflow Architecture
1. **Tracking Server**: A Python service (running on port `5000`) that exposes REST APIs for logging metrics, parameters, and models.
2. **Backend Store**: PostgreSQL is used to store all relational metadata (Run IDs, Model Versions, Parameters). This is required for Model Registry support.
3. **Artifact Store**: A local named Docker volume (`mlflow_artifacts`) that physically stores the serialized ML models.

## Registering Models

Once the Docker stack is running, you can ingest the trained models from Phase 7 into the MLflow registry using the tracking script:

```bash
make register-models
# or
python3 src/mlops/mlflow_tracker.py
```

This script will:
1. Load `fraud_detection/models/xgboost.joblib`.
2. Connect to MLflow (`http://localhost:5000`).
3. Log the model under the `fraud_detection_model` registered name.
4. Repeat for the Loan Default and Customer Segmentation models.

## Production Roadmap
In a full production scenario (Phase 11 and beyond), the FastAPI `ModelManager` (in `src/api/services/model_loader.py`) should be modified to pull models dynamically from MLflow instead of local files using:
```python
import mlflow
model = mlflow.sklearn.load_model("models:/fraud_detection_model/Production")
```
