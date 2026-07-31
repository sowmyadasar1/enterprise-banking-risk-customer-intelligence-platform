# Fraud Detection — Risk Scoring Guide

## Threshold Configuration
- **Optimal Threshold (Max F1):** 0.5362
- **High-Recall Threshold:** 0.4369

## Risk Bands

| Score Range | Risk Band | Recommended Action |
|-------------|-----------|--------------------|
| 0 - 24 | Low Risk | Approve Transaction |
| 25 - 49 | Medium Risk | Manual Investigation |
| 50 - 74 | High Risk | Temporary Hold |
| 75 - 100 | Critical Risk | Block / Escalate |
