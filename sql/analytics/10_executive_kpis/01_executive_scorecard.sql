/*
=============================================================================
Business Question: What are the key performance indicators (KPIs) for the executive team?
Business Interpretation: Provides a high-level overview of business health across customers, deposits, risk, and fraud.
Decision Supported: Strategic planning, company-wide goal setting, and performance tracking.
Recommended Business Action: Focus on areas underperforming against targets (e.g., high fraud rate or low deposit growth).
SQL Techniques Used: CTEs, Aggregation, UNION ALL
=============================================================================
*/

WITH MonthlyCustomers AS (
    SELECT
        strftime('%Y-%m', join_date) AS report_month,
        'Total Customers' AS metric_name,
        COUNT(DISTINCT customer_id) AS metric_value
    FROM
        dim_customer
    GROUP BY
        strftime('%Y-%m', join_date)
),
MonthlyDeposits AS (
    SELECT
        strftime('%Y-%m', transaction_date) AS report_month,
        'Total Deposits' AS metric_name,
        SUM(amount) AS metric_value
    FROM
        fact_transactions
    WHERE
        transaction_type_id = 'Deposit'
    GROUP BY
        strftime('%Y-%m', transaction_date)
),
MonthlyDefaults AS (
    SELECT
        strftime('%Y-%m', end_date) AS report_month,
        'Loan Default Rate' AS metric_name,
        CAST(COUNT(DISTINCT loan_id) AS DECIMAL) / NULLIF((SELECT COUNT(DISTINCT loan_id) FROM fact_loans), 0) * 100 AS metric_value
    FROM
        fact_loans
    WHERE
        status = 'Defaulted'
    GROUP BY
        strftime('%Y-%m', end_date)
),
MonthlyFraud AS (
    SELECT
        strftime('%Y-%m', transaction_date) AS report_month,
        'Fraud Rate' AS metric_name,
        CAST(SUM(CASE WHEN (transaction_id IN (SELECT transaction_id FROM fact_fraud)) = TRUE THEN 1 ELSE 0 END) AS DECIMAL) / COUNT(transaction_id) * 100 AS metric_value
    FROM
        fact_transactions
    GROUP BY
        strftime('%Y-%m', transaction_date)
)
SELECT * FROM MonthlyCustomers
UNION ALL
SELECT * FROM MonthlyDeposits
UNION ALL
SELECT * FROM MonthlyDefaults
UNION ALL
SELECT * FROM MonthlyFraud
ORDER BY
    report_month DESC,
    metric_name;
