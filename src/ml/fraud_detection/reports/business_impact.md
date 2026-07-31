# Fraud Detection — Business Impact Report

## Cost Assumptions
- Avg fraud loss per missed case (FN): $5,000
- Operational review cost per false alarm (FP): $50

## Cost Analysis by Model

| Model | Fraud Prevented | Missed Fraud Cost | False Alarm Cost | Net Savings | Review Workload |
|-------|-----------------|-------------------|------------------|-------------|------------------|
| DecisionTree | $1,300,000 | $340,000 | $12,200 | $947,800 | 504 |
| XGBoost | $1,245,000 | $395,000 | $11,600 | $838,400 | 481 |
| LogisticRegression | $1,230,000 | $410,000 | $23,400 | $796,600 | 714 |
| RandomForest | $1,120,000 | $520,000 | $9,350 | $590,650 | 411 |
| CatBoost | $885,000 | $755,000 | $6,550 | $123,450 | 308 |
| GradientBoosting | $860,000 | $780,000 | $7,050 | $72,950 | 313 |
| LightGBM | $855,000 | $785,000 | $7,350 | $62,650 | 318 |
| Dummy | $765,000 | $875,000 | $29,400 | $-139,400 | 741 |
| IsolationForest | $155,000 | $1,485,000 | $16,800 | $-1,346,800 | 367 |

**Recommended Production Model:** DecisionTree
**Estimated Annual Net Savings:** $947,800
