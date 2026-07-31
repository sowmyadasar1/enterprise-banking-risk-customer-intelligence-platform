# ─── Builder Stage ──────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ─── Final Stage ────────────────────────────────────────────────────
FROM python:3.10-slim

# Create non-root user for security
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

WORKDIR /app

# Install runtime dependencies (e.g., for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python packages from wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code and ML models
# (Note: In a true production environment, ML models might be pulled from MLflow at runtime.
# For this architecture, we bundle the latest Joblib artifacts).
COPY src/ src/
COPY data/ data/

# Set ownership
RUN chown -R apiuser:apiuser /app

# Switch to non-root user
USER apiuser

# Environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start FastAPI using Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
