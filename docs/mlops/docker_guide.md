# Enterprise Docker Deployment Guide

The Enterprise Banking Platform is fully containerized for scalable, reproducible deployments.

## Services Stack (`docker-compose.yml`)

1. **`api`**
   - **Image**: Multi-stage `Dockerfile` (Debian-based Python 3.10-slim).
   - **Ports**: Exposes `8000`.
   - **Security**: Runs as a non-root `apiuser` to prevent privilege escalation.
   - **Role**: Serves the FastAPI endpoints and executes ML models.

2. **`mlflow`**
   - **Image**: Standard `python:3.10-slim`.
   - **Ports**: Exposes `5000`.
   - **Role**: Serves the MLflow UI and Tracking API for the Model Registry.
   - **Volumes**: Maps `./mlflow_artifacts` for binary model storage.

3. **`postgres`**
   - **Image**: `postgres:15-alpine`.
   - **Ports**: Exposes `5432`.
   - **Role**: Relational backend for MLflow (stores metrics, parameters, and metadata).
   - **Volumes**: Maps `postgres_data` to ensure data persistence across restarts.

## Local Development Workflow

1. Clone the repository and configure your `.env` (copy `.env.example`).
2. Run the `Makefile` command to build and launch:
   ```bash
   make build
   make up
   ```
3. Access the services:
   - FastAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - MLflow UI: [http://localhost:5000](http://localhost:5000)

## Production Recommendations
- **Reverse Proxy**: Place an NGINX or Traefik reverse proxy in front of the API to handle SSL/TLS termination.
- **Container Registry**: Push the built image (`enterprise-api:latest`) to an AWS ECR or Azure ACR for deployment to Kubernetes (EKS/AKS).
