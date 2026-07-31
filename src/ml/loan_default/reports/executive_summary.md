# Enterprise Loan Default Platform — Executive Summary

## Overview
The platform evaluated **8 calibrated models** on a loan applicant dataset to predict default probabilities.

## Technical Results
- **Production Model:** LogisticRegression
- **PR-AUC:** 0.6475
- **ROC-AUC:** 0.5060
- **Brier Score (Calibration Error):** 0.2305

## Business Impact
- **Value Added (vs Approve-All Baseline):** $11,334,000
- **Automation Rate:** 0.0% (Auto-Approve + Auto-Reject)
- **Manual Review Rate:** 100.0%

## Recommendations
1. Deploy **LogisticRegression** with probability calibration for credit scoring.
2. Implement multi-tier threshold routing to reduce underwriter workload.
3. Use SHAP global importance insights to update credit policies.
