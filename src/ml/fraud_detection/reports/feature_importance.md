# Fraud Detection — Feature Importance Report

## SHAP Global Feature Importance

| Rank | Feature | Mean |SHAP| |
|------|---------|---------------|
| 1 | risk_score | 0.2376 |
| 2 | avg_daily_txn_count | 0.1368 |
| 3 | rolling_7d_spend | 0.0586 |
| 4 | avg_weekly_txn_count | 0.0562 |
| 5 | preferred_day_of_week | 0.0329 |
| 6 | products_owned | 0.0054 |
| 7 | days_since_last_transaction | 0.0035 |
| 8 | weekend_spending_ratio | 0.0032 |
| 9 | account_count | 0.0000 |
| 10 | summer_txn_ratio | 0.0000 |
| 11 | rolling_30d_spend | 0.0000 |
| 12 | preferred_quarter | 0.0000 |
| 13 | min_transaction_amount | 0.0000 |
| 14 | night_transaction_ratio | 0.0000 |
| 15 | median_transaction_amount | 0.0000 |
| 16 | max_transaction_amount | 0.0000 |
| 17 | loan_risk_indicator | 0.0000 |
| 18 | customer_tenure_days | 0.0000 |
| 19 | avg_transaction_amount | 0.0000 |
| 20 | avg_loan_amount | 0.0000 |

## Mutual Information Scores

| Feature | MI Score |
|---------|----------|
| risk_score | 0.1232 |
| loan_risk_indicator | 0.1054 |
| account_count | 0.0841 |
| transaction_velocity | 0.0837 |
| avg_weekly_txn_count | 0.0826 |
| merchant_diversity | 0.0821 |
| total_spend | 0.0818 |
| winter_txn_ratio | 0.0816 |
| total_transaction_count | 0.0806 |
| avg_daily_txn_count | 0.0781 |
| avg_monthly_txn_count | 0.0769 |
| night_transaction_ratio | 0.0766 |
| summer_txn_ratio | 0.0737 |
| products_owned | 0.0724 |
| weekend_spending_ratio | 0.0699 |
