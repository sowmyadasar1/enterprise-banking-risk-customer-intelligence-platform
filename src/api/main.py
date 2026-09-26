"""
Enterprise Banking Risk & Customer Intelligence Platform — FastAPI Application

Production-grade REST API serving four machine learning systems:
  • Fraud Detection (XGBoost)
  • Loan Default Prediction (XGBoost)
  • Customer Segmentation (K-Means)
  • Revenue Forecasting (ARIMA)
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX, LOG_LEVEL
from .core.exceptions import register_exception_handlers
from .services.model_loader import ModelManager
from .routers import health, fraud, loan, segmentation, forecasting

# ─── Logging Configuration ──────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(name)-28s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api.main")


# ─── Application Lifespan ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: preload models. Shutdown: cleanup."""
    logger.info("=" * 60)
    logger.info("  Starting Enterprise Banking API v%s", API_VERSION)
    logger.info("=" * 60)

    manager = ModelManager()
    manager.preload_all()

    logger.info("Model registry status: %s", manager.get_status())
    logger.info("API ready to serve requests")
    yield
    logger.info("Shutting down Enterprise Banking API")


# ─── FastAPI Application ────────────────────────────────────────────
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── CORS Middleware ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Logging Middleware ──────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s — %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


# ─── Exception Handlers ─────────────────────────────────────────────
register_exception_handlers(app)

# ─── Route Registration ─────────────────────────────────────────────
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(fraud.router, prefix=API_PREFIX)
app.include_router(loan.router, prefix=API_PREFIX)
app.include_router(segmentation.router, prefix=API_PREFIX)
app.include_router(forecasting.router, prefix=API_PREFIX)


# ─── Root Redirect ──────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Enterprise Banking Risk & Customer Intelligence Platform API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
