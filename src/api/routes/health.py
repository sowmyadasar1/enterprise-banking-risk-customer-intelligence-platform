"""Health check API endpoints."""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Return API health status."""
    raise NotImplementedError("Implemented in Phase N")
