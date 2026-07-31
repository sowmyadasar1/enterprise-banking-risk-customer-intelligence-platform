# Query Catalog

This catalog serves as an index of all analytical queries available in the `sql/analytics/` directory.

| File Name | Purpose | Key Metrics / Output |
| :--- | :--- | :--- |
| `01_high_value_customers.sql` | Identifies top-tier customers based on balance and transaction volume. | Customer ID, Total Balance, Transaction Count, Segment |
| `02_loan_default_risk.sql` | Calculates the probability of default for active loans based on historical features. | Loan ID, Customer ID, Risk Score, NPL Flag |
| `03_monthly_churn_analysis.sql` | Aggregates monthly churn rates by customer demographic and product type. | Month, Segment, Churn Rate |
| `04_product_cross_sell.sql` | Analyzes product holding patterns to identify cross-selling opportunities. | Product Pair, Support, Confidence, Lift |
| `05_branch_performance.sql` | Evaluates regional branch performance based on account openings and loan originations. | Branch ID, Region, Total Revenue, Operating Cost |

*Note: This catalog should be updated whenever a new analytical query is added or significantly modified.*
