# Feature Dictionary — Enterprise Banking Platform

This document catalogs every feature engineered in the Feature Store (Phase 6B).

---

## Customer Features (`customer_features.parquet`)

| # | Feature Name | Description | Formula / Source | Data Type | Business Meaning |
|---|---|---|---|---|---|
| 1 | `customer_id` | Unique customer identifier | `dim_customer.customer_id` | TEXT | Primary key |
| 2 | `customer_age` | Age of customer in years | `(today - date_of_birth) / 365.25` | INT | Demographics segmentation |
| 3 | `customer_tenure_days` | Days since joining | `dim_customer.tenure_days` | INT | Loyalty indicator |
| 4 | `customer_tenure_years` | Years since joining | `dim_customer.tenure_years` | FLOAT | Loyalty indicator |
| 5 | `customer_type` | Customer category (Individual/Business) | `dim_customer.customer_type` | TEXT | Segmentation |
| 6 | `risk_rating` | Assigned risk rating | `dim_customer.risk_rating` | TEXT | Risk classification |
| 7 | `is_active` | Whether the customer is active | `dim_customer.is_active` | BOOL | Churn indicator |
| 8 | `account_count` | Number of accounts held | `COUNT(DISTINCT account_id)` | INT | Product penetration |
| 9 | `avg_balance` | Average balance across accounts | `MEAN(current_balance)` | FLOAT | Wealth indicator |
| 10 | `total_balance` | Sum of all account balances | `SUM(current_balance)` | FLOAT | AUM indicator |
| 11 | `max_balance` | Highest account balance | `MAX(current_balance)` | FLOAT | Peak wealth |
| 12 | `min_balance` | Lowest account balance | `MIN(current_balance)` | FLOAT | Minimum threshold |
| 13 | `products_owned` | Distinct account types held | `COUNT(DISTINCT account_type)` | INT | Cross-sell opportunity |
| 14 | `balance_range` | Spread between max and min balance | `max_balance - min_balance` | FLOAT | Balance volatility |
| 15 | `support_ticket_count` | Number of support tickets filed | `COUNT(ticket_id)` | INT | Service quality proxy |
| 16 | `marketing_responses` | Number of campaign responses | `COUNT(response_id)` | INT | Engagement level |
| 17 | `marketing_engagement_score` | Conversion rate from marketing | `conversions / responses` | FLOAT | Marketing ROI indicator |
| 18 | `customer_lifetime_value` | Estimated CLV | `total_balance * tenure_years` | FLOAT | Revenue potential |
| 19 | `income_band` | Income tier based on total balance | Categorical binning | TEXT | Wealth segmentation |

---

## Transaction Features (`transaction_features.parquet`)

| # | Feature Name | Description | Formula / Source | Data Type | Business Meaning |
|---|---|---|---|---|---|
| 1 | `avg_transaction_amount` | Mean absolute transaction amount | `MEAN(amount_abs)` per customer | FLOAT | Spending pattern |
| 2 | `median_transaction_amount` | Median transaction amount | `MEDIAN(amount_abs)` per customer | FLOAT | Robust spending center |
| 3 | `max_transaction_amount` | Largest single transaction | `MAX(amount_abs)` per customer | FLOAT | Outlier detection |
| 4 | `min_transaction_amount` | Smallest single transaction | `MIN(amount_abs)` per customer | FLOAT | Micro-transaction flag |
| 5 | `std_transaction_amount` | Standard deviation of amounts | `STD(amount_abs)` per customer | FLOAT | Spending volatility |
| 6 | `total_transaction_count` | Total number of transactions | `COUNT(transaction_id)` | INT | Activity level |
| 7 | `total_spend` | Sum of all transaction amounts | `SUM(amount_abs)` | FLOAT | Total expenditure |
| 8 | `avg_daily_txn_count` | Average transactions per day | Daily groupby mean | FLOAT | Daily activity |
| 9 | `avg_weekly_txn_count` | Average transactions per week | Weekly groupby mean | FLOAT | Weekly activity |
| 10 | `avg_monthly_txn_count` | Average transactions per month | Monthly groupby mean | FLOAT | Monthly activity |
| 11 | `rolling_7d_spend` | Spend in last 7 days | `SUM(amount_abs) WHERE date >= max-7` | FLOAT | Recent spending velocity |
| 12 | `rolling_30d_spend` | Spend in last 30 days | `SUM(amount_abs) WHERE date >= max-30` | FLOAT | Monthly spending velocity |
| 13 | `transaction_velocity` | Transactions per active day | `n_txns / active_days` | FLOAT | Engagement intensity |
| 14 | `weekend_spending_ratio` | Proportion of weekend transactions | `weekend_txns / total_txns` | FLOAT | Lifestyle indicator |
| 15 | `night_transaction_ratio` | Proportion of night transactions | `night_txns / total_txns` | FLOAT | Fraud risk signal |
| 16 | `large_transaction_ratio` | Proportion of large transactions | `large_txns / total_txns` | FLOAT | High-value indicator |
| 17 | `merchant_diversity` | Unique merchants transacted with | `COUNT(DISTINCT merchant_id)` | INT | Spending diversity |

---

## Loan Features (`loan_features.parquet`)

| # | Feature Name | Description | Formula / Source | Data Type | Business Meaning |
|---|---|---|---|---|---|
| 1 | `total_loan_amount` | Sum of all loan principal amounts | `SUM(loan_amount)` | FLOAT | Total debt exposure |
| 2 | `total_loans` | Number of distinct loans | `COUNT(DISTINCT loan_id)` | INT | Debt diversification |
| 3 | `avg_loan_amount` | Average loan size | `MEAN(loan_amount)` | FLOAT | Borrowing pattern |
| 4 | `avg_interest_rate` | Average interest rate across loans | `MEAN(interest_rate)` | FLOAT | Cost of borrowing |
| 5 | `avg_loan_age_days` | Average age of loans in days | `MEAN(today - start_date)` | FLOAT | Portfolio maturity |
| 6 | `total_remaining_balance` | Outstanding loan balance | `SUM(loan_amount - total_paid)` | FLOAT | Current debt |
| 7 | `avg_repayment_rate` | Average proportion repaid | `MEAN(total_paid / loan_amount)` | FLOAT | Repayment discipline |
| 8 | `avg_loan_utilization` | Average remaining / original ratio | `MEAN(remaining / original)` | FLOAT | Draw-down indicator |
| 9 | `total_late_payments` | Count of late payments across loans | `SUM(late_payment_count)` | INT | Credit risk signal |
| 10 | `total_missed_payments` | Count of missed payments | `SUM(missed_payment_count)` | INT | Default risk signal |
| 11 | `total_payments` | Total number of payments made | `SUM(payment_count)` | INT | Payment activity |
| 12 | `avg_interest_burden` | Interest paid as % of total paid | `MEAN(interest_paid / total_paid)` | FLOAT | Cost burden |
| 13 | `avg_missed_payment_ratio` | Average missed payment proportion | `MEAN(missed / total_payments)` | FLOAT | Default probability proxy |
| 14 | `avg_installment` | Average loan installment size | `total_loan_amount / total_loans` | FLOAT | Monthly obligation |

---

## Risk & Credit Features (`risk_features.parquet`)

| # | Feature Name | Description | Formula / Source | Data Type | Business Meaning |
|---|---|---|---|---|---|
| 1 | `risk_score` | Numeric risk assessment (0-100) | `dim_risk.risk_score` | INT | Quantitative risk measure |
| 2 | `risk_category` | Categorical risk level | `dim_risk.risk_category` | TEXT | Risk bucket classification |
| 3 | `credit_score` | Customer credit score | `dim_risk.credit_score` | INT | Creditworthiness |
| 4 | `credit_score_band` | Credit score tier | Categorical binning | TEXT | Credit tier |
| 5 | `fraud_case_count` | Number of fraud cases | `COUNT(fraud_case_id)` | INT | Fraud exposure |
| 6 | `total_fraud_loss` | Total financial loss from fraud | `SUM(financial_loss)` | FLOAT | Monetary fraud impact |
| 7 | `fraud_risk_indicator` | Binary fraud flag (1=has fraud) | `1 if fraud_case_count > 0` | INT | **Target variable for fraud ML** |
| 8 | `loan_risk_indicator` | Binary high-risk flag | `1 if risk_score > 70` | INT | **Target variable for default ML** |

---

## Temporal Features (`temporal_features.parquet`)

| # | Feature Name | Description | Formula / Source | Data Type | Business Meaning |
|---|---|---|---|---|---|
| 1 | `days_since_last_transaction` | Recency of last transaction | `today - MAX(transaction_date)` | INT | Churn risk indicator |
| 2 | `preferred_day_of_week` | Most common transaction day | `MODE(day_of_week)` | INT | Behavioral pattern |
| 3 | `preferred_month` | Most common transaction month | `MODE(month)` | INT | Seasonal preference |
| 4 | `preferred_quarter` | Most common transaction quarter | `MODE(quarter)` | INT | Quarterly pattern |
| 5 | `summer_txn_ratio` | Proportion of summer transactions | `summer_txns / total_txns` | FLOAT | Seasonality signal |
| 6 | `winter_txn_ratio` | Proportion of winter transactions | `winter_txns / total_txns` | FLOAT | Seasonality signal |
| 7 | `days_since_last_loan_payment` | Recency of last loan payment | `today - MAX(payment_date)` | INT | Payment recency |

---

## Aggregated Features

### Merchant Aggregations (`merchant_aggregations.parquet`)
| Feature | Description |
|---|---|
| `merchant_txn_count` | Total transactions per merchant |
| `merchant_total_spend` | Total spend per merchant |
| `merchant_avg_spend` | Average transaction size per merchant |
| `merchant_max_spend` | Largest transaction per merchant |

### Branch Aggregations (`branch_aggregations.parquet`)
| Feature | Description |
|---|---|
| `branch_account_count` | Total accounts per branch |
| `branch_total_balance` | Total AUM per branch |
| `branch_avg_balance` | Average AUM per account per branch |

### Region Aggregations (`region_aggregations.parquet`)
| Feature | Description |
|---|---|
| `region_branch_count` | Branches per region |
| `region_account_count` | Accounts per region |
| `region_total_balance` | Total AUM per region |
| `region_avg_balance` | Average AUM per region |

---

## Feature Store Summary

| Store File | Entity | Rows | Key |
|---|---|---|---|
| `customer_features.parquet` | Customer | 10,000 | `customer_id` |
| `transaction_features.parquet` | Customer | 7,779 | `customer_id` |
| `loan_features.parquet` | Customer | 3,916 | `customer_id` |
| `risk_features.parquet` | Customer | 6,380 | `customer_id` |
| `temporal_features.parquet` | Customer | 7,779 | `customer_id` |
| `branch_aggregations.parquet` | Branch | 500 | `branch_id` |
| `region_aggregations.parquet` | Region | 9 | `region_id` |
| `feature_metadata.parquet` | Metadata | 65 | `feature_name` |
