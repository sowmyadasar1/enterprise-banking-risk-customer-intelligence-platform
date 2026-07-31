# Recommended Feature Sets — Enterprise Banking Platform

This document provides curated feature recommendations for each ML task based on the automated feature selection pipeline (Variance Threshold, Correlation Filtering, and Mutual Information).

---

## Feature Selection Pipeline Results

### Step 1: Variance Threshold (threshold = 0.01)
- **Kept**: 41 features
- **Dropped**: 18 low-variance features (e.g., `avg_balance`, `total_balance`, `customer_lifetime_value`)
- These features had near-zero variance because the majority of customers without loans/accounts had values filled with 0.

### Step 2: Correlation Filtering (threshold = 0.95)
- **Kept**: 31 features
- **Dropped**: 10 highly-correlated features (e.g., `customer_tenure_years` ≈ `customer_tenure_days`, `total_spend` ≈ `total_transaction_count`)
- Redundant signals removed to reduce multicollinearity.

### Step 3: Mutual Information Ranking
- Ranked features by their predictive power for each target variable.

---

## Fraud Detection Model

**Target Variable**: `fraud_risk_indicator` (binary: 1 = customer has fraud cases)

### Recommended Features (Top 20)

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | `risk_score` | Strongest predictive signal for fraud |
| 2 | `night_transaction_ratio` | Fraud tends to occur during off-hours |
| 3 | `weekend_spending_ratio` | Unusual weekend activity patterns |
| 4 | `max_transaction_amount` | Fraudulent transactions tend to be larger |
| 5 | `avg_transaction_amount` | Elevated average spend indicates compromise |
| 6 | `transaction_velocity` | Rapid transaction bursts indicate card-not-present fraud |
| 7 | `merchant_diversity` | Low diversity may indicate targeted merchant fraud |
| 8 | `rolling_7d_spend` | Spike in recent spending |
| 9 | `rolling_30d_spend` | Sustained anomalous spending window |
| 10 | `days_since_last_transaction` | Dormant accounts suddenly active |
| 11 | `customer_age` | Age demographics correlate with fraud type |
| 12 | `total_transaction_count` | High volume may indicate synthetic fraud |
| 13 | `account_count` | Multiple accounts increase attack surface |
| 14 | `support_ticket_count` | Fraud victims file more support tickets |
| 15 | `credit_score` | Lower credit scores correlate with higher fraud |
| 16 | `avg_daily_txn_count` | Micro-transaction fraud detection |
| 17 | `summer_txn_ratio` | Seasonal fraud patterns |
| 18 | `winter_txn_ratio` | Holiday fraud spike indicator |
| 19 | `preferred_day_of_week` | Day-of-week behavioral anomaly |
| 20 | `customer_tenure_days` | New customers are higher fraud risk |

### Feature Engineering Notes
- Consider creating interaction features: `night_transaction_ratio * max_transaction_amount`
- Time-window features (7d, 30d) are critical for real-time fraud scoring

---

## Loan Default Prediction Model

**Target Variable**: `loan_risk_indicator` (binary: 1 = risk_score > 70)

### Recommended Features (Top 20)

| Priority | Feature | MI Score | Rationale |
|----------|---------|----------|-----------|
| 1 | `risk_score` | 0.6546 | Direct risk assessment — strongest signal |
| 2 | `min_transaction_amount` | 0.0114 | Low-value transactions may indicate distress |
| 3 | `median_transaction_amount` | 0.0101 | Robust spending center measure |
| 4 | `total_remaining_balance` | 0.0087 | Outstanding debt exposure |
| 5 | `avg_loan_age_days` | 0.0078 | Older loans have more payment history |
| 6 | `avg_loan_utilization` | 0.0069 | High utilization = stressed borrower |
| 7 | `merchant_diversity` | 0.0069 | Spending diversity correlates with stability |
| 8 | `preferred_month` | 0.0063 | Seasonal borrowing patterns |
| 9 | `avg_installment` | 0.0061 | Monthly obligation burden |
| 10 | `avg_weekly_txn_count` | 0.0054 | Activity level indicator |
| 11 | `preferred_quarter` | 0.0051 | Quarterly patterns |
| 12 | `avg_missed_payment_ratio` | 0.0049 | Direct default signal |
| 13 | `customer_tenure_years` | 0.0048 | Long-tenured = lower default risk |
| 14 | `is_active` | 0.0042 | Inactive customers default more |
| 15 | `total_late_payments` | — | Late payments are a strong default predictor |
| 16 | `avg_repayment_rate` | — | Low repayment = higher default probability |
| 17 | `avg_interest_burden` | — | High interest burden increases stress |
| 18 | `total_loans` | — | Over-leveraged customers |
| 19 | `avg_interest_rate` | — | Higher rate = subprime borrower |
| 20 | `credit_score` | — | Traditional creditworthiness measure |

### Feature Engineering Notes
- `debt_to_income_ratio` can be approximated as `total_loan_amount / total_balance`
- Consider polynomial features for `avg_missed_payment_ratio` and `avg_loan_utilization`

---

## Customer Segmentation Model

**Target**: Unsupervised clustering (no explicit target variable)

### Recommended Features (Top 15)

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | `customer_age` | Age-based cohorts |
| 2 | `customer_tenure_days` | Loyalty tiers |
| 3 | `account_count` | Product penetration |
| 4 | `products_owned` | Cross-sell depth |
| 5 | `total_spend` | Spending power |
| 6 | `avg_transaction_amount` | Spending level |
| 7 | `transaction_velocity` | Engagement intensity |
| 8 | `weekend_spending_ratio` | Lifestyle indicator |
| 9 | `night_transaction_ratio` | Activity pattern |
| 10 | `support_ticket_count` | Service interaction level |
| 11 | `marketing_engagement_score` | Responsiveness to campaigns |
| 12 | `total_balance` | Wealth indicator |
| 13 | `risk_score` | Risk profile |
| 14 | `credit_score` | Financial health |
| 15 | `days_since_last_transaction` | Recency / churn risk |

### Segmentation Strategy
- Use K-Means or DBSCAN clustering
- Standardize (z-score) all features before clustering
- Optimal k via Elbow Method and Silhouette Score

---

## Revenue Forecasting Model

**Target**: `total_spend` or `rolling_30d_spend` (continuous)

### Recommended Features (Top 15)

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | `avg_transaction_amount` | Base spending level |
| 2 | `total_transaction_count` | Volume driver |
| 3 | `transaction_velocity` | Frequency signal |
| 4 | `rolling_7d_spend` | Short-term trend |
| 5 | `account_count` | More accounts = more revenue |
| 6 | `products_owned` | Cross-sell revenue |
| 7 | `customer_tenure_days` | Mature customers spend more |
| 8 | `preferred_quarter` | Seasonal revenue patterns |
| 9 | `summer_txn_ratio` | Summer spending boost |
| 10 | `winter_txn_ratio` | Holiday spending boost |
| 11 | `merchant_diversity` | Diversified spending = more revenue |
| 12 | `customer_age` | Age-spending correlation |
| 13 | `marketing_engagement_score` | Campaign-driven revenue |
| 14 | `avg_daily_txn_count` | Granular activity signal |
| 15 | `credit_score` | Higher scores = higher spending capacity |

### Modeling Strategy
- Use time-series models (ARIMA, Prophet) for trend + seasonality
- Use gradient boosting (XGBoost) for cross-sectional prediction
- Combine both for ensemble forecasting

---

## Data Leakage Checklist

> [!CAUTION]
> The following features must be excluded or carefully handled to prevent data leakage:

| Feature | Risk | Mitigation |
|---------|------|------------|
| `fraud_risk_indicator` | Direct target for fraud model | Exclude from fraud model inputs |
| `loan_risk_indicator` | Direct target for default model | Exclude from default model inputs |
| `risk_score` | May encode future information | Use only if assessment_date < prediction date |
| `credit_score` | May be updated post-event | Snapshot at prediction time only |
