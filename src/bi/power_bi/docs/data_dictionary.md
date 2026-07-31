# Data Dictionary & KPI Definitions

This dictionary defines the exact business logic implemented in the Power BI DAX layer, ensuring consistency across all enterprise reporting.

## Core Financials
| KPI Name | DAX Definition | Description |
|---|---|---|
| Total Revenue | `SUM(fact_transactions[amount])` | Total gross volume of all processed transactions. |
| Average Transaction Value | `AVERAGE(fact_transactions[amount])` | The average size of a transaction across the filtered context. |
| Total Profit | `[Total Revenue] * 0.02` | Simulated margin based on an enterprise assumption of a 2% net yield on transaction volumes. |

## Customer Metrics
| KPI Name | DAX Definition | Description |
|---|---|---|
| Total Customers | `DISTINCTCOUNT(dim_customer[customer_id])` | Total unique individuals banking with the enterprise. |
| Active Customers | `DISTINCTCOUNT(fact_transactions[customer_id])` where Date >= (TODAY-30) | Customers who have conducted at least one transaction in the last 30 days. |
| Customer Lifetime Value (CLV) | `AVERAGE(view_kpi_clv[annualized_clv])` | The annualized predicted lifetime value (driven by ML outputs from Phase 7C). |

## Risk & Loans
| KPI Name | DAX Definition | Description |
|---|---|---|
| Total Outstanding Loans | `SUM(fact_loans[loan_amount])` where Status = "Active" | The sum total of principal for all currently active loans. |
| Loan Default Rate | `Count(Defaulted) / Count(All)` | Percentage of loans that have entered default status. |
| Average Risk Score | `AVERAGE(dim_risk[credit_score])` | The average credit score of the customer base. |

## Fraud
| KPI Name | DAX Definition | Description |
|---|---|---|
| Fraud Rate | `(Count(Fraud Cases) / Count(Transactions)) * 1000` | The number of fraud cases detected per 1,000 legitimate transactions. |
| Total Fraud Loss | `SUM(fact_fraud[financial_loss])` | The total dollar amount lost to unrecoverable fraudulent activity. |
