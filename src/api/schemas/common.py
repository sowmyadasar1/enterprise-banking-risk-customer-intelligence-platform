"""Common API schemas."""

from pydantic import BaseModel
from typing import Optional, Any


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    timestamp: str
    version: str


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: int = 1
    size: int = 50


class ErrorResponse(BaseModel):
    """Schema for API error responses."""

    error_code: str
    message: str
    details: Optional[Any] = None
