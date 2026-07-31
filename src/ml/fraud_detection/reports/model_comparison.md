# Fraud Detection — Model Comparison Report

## Model Performance Summary

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | MCC |
|-------|----------|-----------|--------|----|---------|---------|----- |
| DecisionTree | 0.7920 | 0.5159 | 0.7927 | 0.6250 | 0.8602 | 0.5127 | 0.5115 |
| XGBoost | 0.7927 | 0.5177 | 0.7591 | 0.6156 | 0.8681 | 0.5789 | 0.4970 |
| RandomForest | 0.8060 | 0.5450 | 0.6829 | 0.6062 | 0.8710 | 0.5530 | 0.4850 |
| CatBoost | 0.8120 | 0.5747 | 0.5396 | 0.5566 | 0.8722 | 0.6048 | 0.4378 |
| GradientBoosting | 0.8020 | 0.5495 | 0.5244 | 0.5367 | 0.8644 | 0.5620 | 0.4110 |
| LightGBM | 0.7973 | 0.5377 | 0.5213 | 0.5294 | 0.8669 | 0.5767 | 0.4004 |
| LogisticRegression | 0.6333 | 0.3445 | 0.7500 | 0.4722 | 0.7508 | 0.4300 | 0.2902 |
| Dummy | 0.4913 | 0.2065 | 0.4665 | 0.2862 | 0.4824 | 0.2130 | -0.0291 |
| IsolationForest | 0.5780 | 0.0845 | 0.0945 | 0.0892 | 0.0000 | 0.0000 | -0.1848 |

**Best Model (by F1):** DecisionTree

**Production Model:** DecisionTree
