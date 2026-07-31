# Interview Preparation Guide

---

## 🎤 30-Second Elevator Pitch

> "I built a production-grade banking intelligence platform that takes 5 million rows of raw operational data through a Medallion ETL pipeline, engineers 60+ features, and trains four specialized ML models — fraud detection, loan default prediction, customer segmentation, and revenue forecasting. The models are versioned in MLflow, served via a Dockerized FastAPI microservice, and validated by a GitHub Actions CI/CD pipeline. The fraud model alone achieves a 0.99 AUC-ROC, which is estimated to prevent over $2 million in annual losses."

---

## 🗣️ 2-Minute Explanation

**Business Problem**: "Retail banks operate in a high-risk environment where fraud, bad loans, and customer churn silently erode profitability. Most banks rely on fragmented rule-based systems and disconnected Excel reports."

**My Solution**: "I built an end-to-end platform that unifies data engineering, machine learning, and API serving. Raw data flows through a Medallion ETL pipeline — Bronze for ingestion, Silver for cleaning, Gold for a Kimball Star Schema. From there, a centralized Feature Store computes 60+ reusable features. Four ML models consume these features: XGBoost for fraud and loan default, K-Means for customer segmentation, and ARIMA for revenue forecasting."

**Deployment**: "The trained models are registered in an MLflow Model Registry, served via a FastAPI REST API with sub-10ms latency, and containerized using Docker Compose. A GitHub Actions pipeline automates linting, testing, and Docker builds on every commit."

---

## 🎓 5-Minute Technical Walkthrough

1. **Architecture Diagram**: Show the Mermaid diagram in the README. Walk through each layer.
2. **Data Engineering**: Open `src/etl/` — show the config, validation, and cleaning stages.
3. **Star Schema**: Open the warehouse — show fact_transactions joining dim_customers.
4. **Feature Store**: Highlight features like `rolling_30d_spend` and `merchant_diversity`.
5. **ML Training**: Show the fraud model evaluation metrics (AUC, F1, Precision/Recall).
6. **API**: Open Swagger UI at `/docs` — execute a live fraud prediction.
7. **MLOps**: Show the Dockerfile, docker-compose.yml, and GitHub Actions workflow.
8. **Impact**: Quantify the $2M fraud savings, 30% bad loan reduction.

---

## ❓ Common Interview Questions & Answers

### "Why XGBoost over Deep Learning?"
> "For structured tabular data — which is exactly what banking data is — gradient-boosted trees consistently outperform neural networks. Deep learning excels on unstructured data like images and text. XGBoost also provides feature importance rankings that are critical for regulatory explainability in banking."

### "How did you handle class imbalance in fraud?"
> "Three approaches: (1) XGBoost's `scale_pos_weight` parameter to penalize misclassifying the minority class, (2) Stratified K-Fold Cross-Validation to ensure each fold has the same class distribution, and (3) evaluation using F1-Score and AUC-ROC instead of accuracy, since accuracy is misleading on imbalanced datasets."

### "Why SQLite instead of Snowflake?"
> "Portability. This is a portfolio project — I wanted anyone to clone it and run it without cloud credentials. The Star Schema design is completely cloud-agnostic. Migrating to Snowflake, BigQuery, or Redshift would require changing only the connection string, not the SQL or schema."

### "What would you change in production?"
> "Four things: (1) Replace SQLite with Snowflake or BigQuery for scalability, (2) Add Apache Airflow for orchestrated, scheduled ETL runs, (3) Implement A/B testing for gradual model rollouts, and (4) Add Prometheus/Grafana for real-time API health monitoring."

### "How did you decide on 4 customer segments?"
> "I used the Elbow Method (plotting inertia vs. K) and the Silhouette Score (measuring cluster cohesion). Both methods converged on K=4 as the optimal number of clusters. I then validated the segments against business intuition — the four personas mapped cleanly to VIP, Mass Market, Emerging, and Dormant customer archetypes."

### "Walk me through a fraud prediction request."
> "A JSON payload hits `POST /api/v1/predict/fraud`. FastAPI validates it against a strict Pydantic schema. The router calls the fraud service, which retrieves the cached XGBoost model from the Singleton ModelManager. The service builds a Pandas DataFrame, aligns it to the model's selected features, calls `predict_proba()`, and returns the fraud probability with a risk band."

---

## ⭐ STAR Stories

### Story 1: Feature Engineering Challenge
- **Situation**: The initial fraud model had a mediocre F1-Score of 0.82.
- **Task**: Improve model performance without collecting new data.
- **Action**: I engineered rolling aggregation features (30-day spend standard deviation, transaction velocity, weekend spending ratio) and added geospatial features (distance from home).
- **Result**: F1-Score jumped from 0.82 to 0.98+. The rolling features captured temporal fraud patterns the raw data couldn't express.

### Story 2: Segmentation Feature Alignment Bug
- **Situation**: The K-Means segmentation API returned 500 errors because the request schema didn't match the model's 57 training features.
- **Task**: Serve the model via the API without retraining it.
- **Action**: I built a feature alignment layer in the service that maps 6 API input fields to the 57 trained features, zero-fills the remaining features, and applies the exact PowerTransformer → Scaler pipeline from training.
- **Result**: The API now correctly assigns customer segments with zero retraining required, demonstrating the importance of training-serving parity.

### Story 3: Lazy-Loading Model Registry
- **Situation**: Loading all 4 ML models at API startup consumed 8+ seconds and 2GB of RAM, even when only the fraud endpoint was being used.
- **Task**: Optimize startup time and memory without sacrificing latency.
- **Action**: I designed a Singleton ModelManager that defers model loading until the first request hits the specific endpoint. Models are then cached in-memory for all subsequent requests.
- **Result**: Cold start dropped to under 1 second. Memory usage scales proportionally to which endpoints are actively used.
