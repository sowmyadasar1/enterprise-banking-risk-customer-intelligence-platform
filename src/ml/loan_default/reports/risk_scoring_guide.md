# Loan Default — Risk Scoring & Threshold Guide

## Decision Thresholds (Probabilities)
- **Auto-Approve Threshold:** < 0.4000 
- **Auto-Reject Threshold:** >= 0.7423
- **Manual Review Range:** 0.4000 to 0.7423

## Credit Risk Categories

| Risk Score (0-100) | Risk Category | Interpretation |
|--------------------|---------------|----------------|
| 0 - 9 | Very Low Risk | Prime borrower, low default likelihood |
| 10 - 24 | Low Risk | Standard borrower, acceptable risk |
| 25 - 49 | Medium Risk | Sub-prime, requires underwriting review |
| 50 - 79 | High Risk | High likelihood of default, strict conditions |
| 80 - 100 | Very High Risk | Critical default risk, decline |
