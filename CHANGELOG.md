# Changelog

All notable changes to the Enterprise Banking Risk & Customer Intelligence Platform are documented here.

## [1.0.0] — 2026-08-01

### Added
- **Phase 0**: Enterprise Architecture design and technology stack selection.
- **Phase 1**: Repository foundation with modular folder structure, `pyproject.toml`, `.gitignore`, and configuration.
- **Phase 2**: Enterprise Banking Data Foundation — 29 datasets, 5M+ synthetic records across 8 domains.
- **Phase 3**: Medallion ETL Pipeline (Bronze → Silver → Gold) with data quality validation, quarantine routing, and audit logging.
- **Phase 4**: Star Schema Data Warehouse (SQLite) with 2 fact tables and 6 dimension tables.
- **Phase 5**: SQL Analytics layer with 40+ business intelligence queries for revenue, risk, customer, and fraud analytics.
- **Phase 6A**: Exploratory Data Analysis with statistical analysis, distribution profiling, and correlation analysis.
- **Phase 6B**: Centralized Feature Store with 60+ engineered features (rolling aggregations, behavioral ratios, temporal patterns).
- **Phase 7A**: XGBoost Fraud Detection model (0.99 AUC-ROC, 0.98 F1-Score).
- **Phase 7B**: XGBoost Loan Default Prediction model (0.95+ AUC-ROC) with three-tier decision engine.
- **Phase 7C**: K-Means Customer Segmentation with 4 business personas and PowerTransformer/Scaler pipeline.
- **Phase 7D**: ARIMA Revenue & Transaction Forecasting with 95% confidence intervals.
- **Phase 8**: Power BI Platform — DAX measures, time intelligence, Row-Level Security, enterprise theme.
- **Phase 9**: FastAPI Model Serving Platform — 5 REST endpoints, lazy-loading Singleton model registry, Pydantic validation, API Key security.
- **Phase 10**: MLOps Platform — Docker Compose (API + MLflow + PostgreSQL), GitHub Actions CI/CD, MLflow Model Registry, Makefile automation.
- **Phase 11**: Complete documentation suite (37 files), README, resume assets, interview preparation materials.

### Infrastructure
- Multi-stage Dockerfile with non-root user security.
- Docker Compose orchestration for 3 services.
- GitHub Actions CI/CD pipeline (lint → test → Docker build).
- MLflow experiment tracking and model versioning.
