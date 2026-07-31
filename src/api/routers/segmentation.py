"""
Customer Segmentation Router
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from ..schemas.requests import SegmentationRequest
from ..schemas.responses import (
    SegmentationResponse,
    SegmentationResult,
    APIMetadata,
)
from ..services.segment_service import predict_segment
from ..core.security import verify_api_key

router = APIRouter(prefix="/predict", tags=["Customer Segmentation"], dependencies=[Depends(verify_api_key)])


@router.post("/segmentation", response_model=SegmentationResponse, summary="Assign Customer Segment")
async def assign_segment(request: SegmentationRequest):
    """
    Assigns a customer to a behavioral segment using the K-Means model from Phase 7C.

    Returns the cluster ID, the business persona label, and a brief persona description.
    """
    start = time.perf_counter()
    result = predict_segment(request.model_dump())
    elapsed = (time.perf_counter() - start) * 1000

    return SegmentationResponse(
        prediction=SegmentationResult(**result),
        metadata=APIMetadata(
            model_name="kmeans_segmentation",
            model_version="1.0.0",
            timestamp=datetime.utcnow(),
            latency_ms=round(elapsed, 2),
        ),
    )
