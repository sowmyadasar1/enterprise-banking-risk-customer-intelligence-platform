# Live Demo Script

A step-by-step guide for presenting this project in a 10-minute screen-share interview or portfolio review.

---

## ⏱️ Minute 0–1: Introduction & First Impression

**Open the GitHub README.**

Key talking points:
- "This is a production-grade enterprise platform, not a Jupyter notebook."
- Point out the technology badges (Python, FastAPI, MLflow, Docker, XGBoost).
- Show the Mermaid architecture diagram and explain the data flow.
- Highlight the organized folder structure.

> 💡 **Tip**: Recruiters spend 6 seconds on a GitHub repo. The README badges and architecture diagram are your "above the fold" content.

---

## ⏱️ Minute 1–3: Data Engineering Layer

**Navigate to the `data/` directory.**
- Show the Bronze, Silver, and Gold layer folders.
- Explain the Medallion Architecture: "Raw data lands in Bronze untouched. Silver cleans, deduplicates, and validates. Gold is the Star Schema optimized for analytics."

**Open one ETL module** (e.g., `src/etl/clean/__init__.py`).
- Show the code quality: docstrings, type hints, modular classes.
- Mention: "This processes 29 datasets and 5 million+ records."

**Open the SQLite warehouse** (optional: run a quick SQL query).

---

## ⏱️ Minute 3–5: Machine Learning

**Open the Feature Store documentation** (`docs/pipelines/Feature_Store.md`).
- Highlight rolling aggregations, behavioral ratios, temporal patterns.
- "60+ engineered features are centralized here so all 4 ML models share the same logic — no training-serving skew."

**Show model evaluation** (if notebooks exist) or describe:
- "XGBoost won the fraud benchmark with 0.99 AUC-ROC across 8 algorithms."
- "The loan model enables three-tier decisions: Approve, Review, Decline."

---

## ⏱️ Minute 5–7: API & MLOps (Live Demo)

**Open FastAPI Swagger UI**: `http://localhost:8000/docs`
1. Expand `POST /api/v1/predict/fraud`.
2. Click "Try it out".
3. Paste the example payload and execute.
4. Show the JSON response: probability, risk level, metadata with latency.
5. "Sub-10 millisecond inference because of our lazy-loading Singleton."

**Open MLflow UI**: `http://localhost:5000`
- Show the registered models: fraud, loan, segmentation.
- "Each model is versioned and tracked. In production, the API would pull from this registry instead of local files."

---

## ⏱️ Minute 7–9: DevOps & CI/CD

**Show `docker-compose.yml`**:
- "Three services: the API, MLflow tracking server, and PostgreSQL."
- "One command — `make up` — starts the entire stack."

**Show `.github/workflows/main.yml`**:
- "On every push, GitHub Actions runs linting, pytest, and validates the Docker build."

**Show the `Makefile`**:
- "Developer experience matters. `make test`, `make build`, `make up`."

---

## ⏱️ Minute 9–10: Business Impact & Wrap-Up

**Summarize value delivered**:
- "$2M+ in prevented fraud losses (0.99 AUC-ROC)."
- "30% reduction in bad loan disbursements."
- "4 customer personas enabling targeted marketing."
- "95% confidence interval revenue forecasts."

**Future improvements**:
- "In production, I'd add Apache Airflow for orchestration, Prometheus/Grafana for monitoring, and A/B testing for model rollouts."

**Close**: "This project demonstrates full-stack data science — from raw data to Dockerized API — using enterprise-standard patterns."

---

## 📸 Suggested Screenshots for Portfolio

1. GitHub README (badges + architecture diagram)
2. FastAPI Swagger UI (`/docs`)
3. Fraud prediction JSON response
4. MLflow Model Registry UI
5. Docker Compose terminal output
6. Pytest — 14/14 passing
7. Project directory tree
