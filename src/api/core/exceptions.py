"""
Global Exception Handlers & Custom Exceptions
Provides consistent JSON error responses across all endpoints.
"""
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("api.exceptions")


# ─── Custom Exceptions ──────────────────────────────────────────────
class ModelNotLoadedError(Exception):
    """Raised when an ML model fails to load from disk."""
    def __init__(self, model_name: str, detail: str = ""):
        self.model_name = model_name
        self.detail = detail
        super().__init__(f"Model '{model_name}' not loaded: {detail}")


class PredictionError(Exception):
    """Raised when a prediction pipeline fails internally."""
    def __init__(self, model_name: str, detail: str = ""):
        self.model_name = model_name
        self.detail = detail
        super().__init__(f"Prediction failed for '{model_name}': {detail}")


class InvalidInputError(Exception):
    """Raised when business-rule input validation fails."""
    def __init__(self, detail: str = ""):
        self.detail = detail
        super().__init__(detail)


# ─── Handler Registration ───────────────────────────────────────────
def register_exception_handlers(app: FastAPI):
    """Attach all custom exception handlers to the FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
        logger.error("Model not loaded: %s — %s", exc.model_name, exc.detail)
        return JSONResponse(
            status_code=503,
            content={
                "error": "Model Unavailable",
                "detail": f"The '{exc.model_name}' model is not available. Please try again later.",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        logger.error("Prediction error: %s — %s", exc.model_name, exc.detail)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Prediction Failed",
                "detail": f"An internal error occurred while generating the prediction for '{exc.model_name}'.",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        logger.warning("Invalid input: %s", exc.detail)
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid Input",
                "detail": exc.detail,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.critical(
            "Unhandled exception on %s: %s\n%s",
            request.url.path,
            str(exc),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please contact the platform team.",
                "path": str(request.url.path),
            },
        )
