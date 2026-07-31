# Loan Default Prediction — Model Comparison Report

## Performance & Calibration Summary

| Model | F1 Score | ROC-AUC | PR-AUC | Brier Score (Calibration) |
|-------|----------|---------|--------|-------------|
| LogisticRegression | 0.7788 | 0.5060 | 0.6475 | 0.2305 |
| GradientBoosting | 0.7758 | 0.5146 | 0.6475 | 0.2322 |
| XGBoost | 0.7791 | 0.5112 | 0.6424 | 0.2313 |
| RandomForest | 0.7771 | 0.5093 | 0.6401 | 0.2317 |
| LightGBM | 0.7791 | 0.5063 | 0.6378 | 0.2313 |
| Dummy | 0.6287 | 0.4880 | 0.6325 | 0.4733 |
| CatBoost | 0.7793 | 0.5028 | 0.6316 | 0.2319 |
| DecisionTree | 0.7790 | 0.4849 | 0.6257 | 0.2315 |

**Best Model (by PR-AUC):** LogisticRegression
