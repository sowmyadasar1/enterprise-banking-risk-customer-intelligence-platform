"""
Health & System Information Router
"""
from datetime import datetime
from fastapi import APIRouter
from ..schemas.responses import HealthResponse, ModelInfoResponse
from ..services.model_loader import ModelManager
from ..config import API_VERSION

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """Returns the current health status of the API and model loading states."""
    manager = ModelManager()
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=datetime.utcnow(),
        models_loaded=manager.get_status(),
    )


@router.get("/info", summary="API Information")
async def api_info():
    """Returns version, build, and capability metadata."""
    return {
        "application": "Enterprise Banking Risk & Customer Intelligence Platform",
        "api_version": API_VERSION,
        "capabilities": [
            "fraud_detection",
            "loan_default_prediction",
            "customer_segmentation",
            "revenue_forecasting",
        ],
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/models", summary="List Loaded Models")
async def list_models():
    """Returns information about all registered model artifacts."""
    manager = ModelManager()
    status = manager.get_status()
    models = []
    for name, loaded in status.items():
        models.append(
            ModelInfoResponse(
                model_name=name,
                model_type="XGBoost" if name in ("fraud", "loan_default") else "K-Means" if name == "segmentation" else "ARIMA",
                is_loaded=loaded,
                artifact_path=f"src/ml/{name}/models/",
            )
        )
    return {"models": models}
