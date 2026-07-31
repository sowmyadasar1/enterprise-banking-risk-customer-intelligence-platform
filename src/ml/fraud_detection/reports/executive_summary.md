# Fraud Detection Platform — Executive Summary

## Overview
The Enterprise Fraud Detection Platform evaluated **9 models** on the banking customer dataset of **10,000 customers**.

## Key Results
- **Best Model:** DecisionTree
- **F1 Score:** 0.6250
- **ROC-AUC:** 0.8602
- **Precision:** 0.5159 | **Recall:** 0.7927

## Business Impact
- **Net Savings:** $947,800
- **Fraud Prevented:** $1,300,000
- **Review Workload:** 504 cases

## Recommendations
1. Deploy **DecisionTree** as the production fraud detection model.
2. Use the optimized threshold for decision-making.
3. Monitor model drift monthly and retrain quarterly.
4. Integrate SHAP explanations into analyst dashboards.
