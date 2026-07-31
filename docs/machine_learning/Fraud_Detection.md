# Fraud Detection Machine Learning Pipeline

Fraud Detection was the first ML system implemented (Phase 7A) to mitigate direct financial losses from unauthorized transactions.

## Business Context
Traditional rule-based fraud systems (e.g., "Block transactions over $10,000") suffer from massive False Positive rates, severely impacting customer experience. By leveraging Machine Learning, we can identify complex, non-linear patterns (e.g., a $45 transaction at a gas station, followed by a $200 electronics purchase in a foreign country) with high precision.

## Feature Engineering Highlights
The model consumes 12 specific features from the Feature Store, including:
*   `amount_std_30d`: The standard deviation of the user's transaction amounts over the last 30 days. Sudden spikes heavily indicate account takeover.
*   `transaction_count_30d`: High velocity of small transactions is a classic card-testing pattern.
*   `distance_from_home`: Geospatial anomaly detection.

## Model Selection & Training
We evaluated 8 different algorithms using 5-Fold Cross Validation:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosting
5. XGBoost
6. LightGBM
7. CatBoost
8. Isolation Forest

**Winner: XGBoost**
XGBoost achieved the highest **F1-Score (0.98+)** and **AUC-ROC (0.99+)**. It expertly handled the severe class imbalance inherent in fraud data without requiring heavy synthetic oversampling (SMOTE).

## Serving Architecture
The XGBoost model is serialized via Joblib, registered in MLflow, and served via the `/api/v1/predict/fraud` endpoint. The API responds with:
- A probability score (e.g. `0.92`).
- A boolean flag (`is_fraud: true`).
- A risk band (`Critical`).
