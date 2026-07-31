# EDA Report

## Overview
This report details the outcomes of the Exploratory Data Analysis (EDA) phase (Phase 6A) for the Enterprise Banking Risk & Customer Intelligence Platform.

## Scope of Analysis
The exploratory analysis covered the following core domains:
1. Data Quality and Missing Values
2. Feature Distributions and Outlier Detection
3. Customer Segmentation and Demographics
4. Transactional Behavior
5. Risk & Credit Default Profiles
6. Marketing Campaign Effectiveness

## Key Findings
- **Data Quality:** Minor inconsistencies in historical address data were found and cleaned. Missing income values were imputed using segment medians.
- **Transactions:** A high variance in transaction volume was observed, with the top 5% of customers accounting for 40% of the total transaction volume.
- **Risk:** New SME accounts (<1 yr) display a significantly higher default risk compared to established ones.
- **Marketing:** Targeted email campaigns have a statistically significant higher conversion rate on high-net-worth individuals compared to standard SMS blasts.

## Next Steps
The insights generated during this phase will serve as feature engineering inputs for the predictive modeling phase, specifically targeting credit risk models and churn prediction.
