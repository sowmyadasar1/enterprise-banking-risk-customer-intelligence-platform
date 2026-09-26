"""
API Security — API Key authentication dependency.
"""

import logging
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from ..config import API_KEY

logger = logging.getLogger("api.security")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency that validates the X-API-Key header.
    Returns the validated key on success, raises 401 on failure.
    """
    if api_key is None:
        logger.warning("Request received without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Provide it via the 'X-API-Key' header.",
        )
    if api_key != API_KEY:
        logger.warning("Invalid API key attempted: %s...", api_key[:8])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.",
        )
    return api_key
