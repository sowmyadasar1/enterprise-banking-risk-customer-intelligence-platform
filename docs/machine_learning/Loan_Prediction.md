# Loan Default Prediction Pipeline

Loan Default Prediction (Phase 7B) assesses credit risk at the point of application to protect the bank's capital reserves.

## Business Context
Consumer lending is a bank's primary revenue engine, but also its greatest risk exposure. A single defaulted $50K loan can wipe out the profit from dozens of performing loans. By predicting default probability *before* disbursement, credit analysts can make data-driven approval decisions instead of relying solely on FICO scores.

## Feature Engineering
The model consumes 10 core features from the Feature Store:

| Feature | Business Meaning |
|---------|-----------------|
| `loan_amount` | Requested principal |
| `interest_rate` | Annual rate (%) |
| `loan_term_months` | Repayment duration |
| `credit_score` | Bureau credit score (300-900) |
| `debt_to_income_ratio` | Existing debt burden |
| `annual_income` | Applicant's yearly income |
| `employment_length_years` | Job stability indicator |
| `number_of_accounts` | Financial product diversity |
| `previous_defaults` | Historical default count |
| `customer_age` | Borrower age |

## Model Selection
We benchmarked 8 algorithms using Stratified 5-Fold Cross-Validation:

| Model | AUC-ROC | F1-Score |
|-------|---------|----------|
| **XGBoost** | **0.95+** | **0.93+** |
| LightGBM | 0.94 | 0.92 |
| CatBoost | 0.94 | 0.91 |
| Random Forest | 0.92 | 0.89 |
| Gradient Boosting | 0.91 | 0.88 |

**Winner: XGBoost** — Best overall discrimination between defaulters and non-defaulters.

## Decision Engine
The API maps probabilities to actionable decisions:

| Probability | Risk Band | Action |
|-------------|-----------|--------|
| < 0.30 | Low | **Approve** |
| 0.30 – 0.60 | Medium | **Review** (manual underwriting) |
| > 0.60 | High | **Decline** |

## API Endpoint
`POST /api/v1/predict/loan-default` — Returns `default_probability`, `risk_band`, and `recommended_action`.
