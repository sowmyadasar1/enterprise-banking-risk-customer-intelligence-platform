# CI/CD Pipeline Guide

The Enterprise Platform utilizes GitHub Actions (`.github/workflows/main.yml`) for Continuous Integration and Continuous Deployment (CI/CD).

## Pipeline Architecture

The pipeline executes automatically on every `push` or `pull_request` to the `main` or `develop` branches. It consists of two sequential jobs:

### 1. `test` Job
- **Linting (`flake8`)**: Ensures PEP-8 compliance. Fails the build immediately if there are syntax errors or undefined names.
- **Unit Testing (`pytest`)**: Boots the FastAPI application locally using `TestClient` and executes the full validation test suite (`test_api.py`).

### 2. `docker-build` Job (Requires `test` to pass)
- **Image Build**: Rebuilds the `enterprise-api:latest` Docker image. This guarantees that any changes to `requirements.txt` or `Dockerfile` compile successfully without breaking the runtime environment.
- **Compose Validation**: Runs `docker-compose config` to statically validate the YAML orchestration file for errors.

## Security Best Practices
- **Dependabot**: We recommend enabling GitHub Dependabot to automatically scan `requirements.txt` for CVEs and outdated packages.
- **Secret Management**: Do NOT commit API Keys or Database passwords. They must be injected into the CI pipeline using GitHub Secrets (`${{ secrets.API_KEY }}`).
