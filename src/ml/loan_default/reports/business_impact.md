# Loan Default Prediction — Portfolio Impact Report

## Portfolio Assumptions
- Avg Loan Value: $15,000
- Profit Margin (Good Loan): 10.0%
- Recovery Rate (Default): 20.0%
- Manual Review Cost: $100

## Impact by Model (Test Set Simulation)

| Model | Auto-Approve | Manual Review | Auto-Reject | Review Cost | Value Added vs Baseline |
|-------|--------------|---------------|-------------|-------------|-------------------------|
| DecisionTree | 0.0% | 100.0% | 0.0% | $150,000 | $11,334,000 |
| CatBoost | 0.0% | 99.5% | 0.5% | $149,300 | $11,328,700 |
| XGBoost | 0.0% | 99.3% | 0.7% | $148,900 | $11,327,600 |
| LogisticRegression | 0.1% | 99.4% | 0.5% | $149,100 | $11,322,900 |
| LightGBM | 0.1% | 99.7% | 0.3% | $149,500 | $11,321,000 |
| RandomForest | 0.1% | 99.9% | 0.1% | $149,800 | $11,320,700 |
| GradientBoosting | 0.1% | 99.1% | 0.9% | $148,600 | $11,315,900 |
| Dummy | 36.3% | 0.0% | 63.7% | $0 | $6,681,000 |
