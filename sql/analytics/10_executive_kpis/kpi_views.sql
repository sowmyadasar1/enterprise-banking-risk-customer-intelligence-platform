/*
=============================================================================
Business Question: How do we track advanced metrics like CLV, ARPU, CAC, and Retention?
Business Interpretation: Standardizes the definitions and calculations of critical business metrics for consistent reporting.
Decision Supported: Marketing ROI analysis, customer success strategies, and long-term profitability forecasting.
Recommended Business Action: Use these views as the foundation for executive dashboards and advanced analytics models.
SQL Techniques Used: CREATE VIEW, Complex Aggregations, Date Functions
=============================================================================
*/

-- 1. Customer Lifetime Value (CLV) View
DROP VIEW IF EXISTS view_kpi_clv;
CREATE VIEW view_kpi_clv AS
SELECT
    c.customer_id,
    c.customer_type,
    SUM(t.amount * 0.02) AS estimated_revenue,
    MIN(t.transaction_date) AS first_transaction,
    MAX(t.transaction_date) AS last_transaction,
    (julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date))) AS customer_tenure_days,
    SUM(t.amount * 0.02) * (365.0 / NULLIF((julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date))), 0)) AS annualized_clv
FROM
    dim_customer c
JOIN
    dim_account a ON c.customer_id = a.customer_id
JOIN
    fact_transactions t ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.customer_type;

-- 2. Average Revenue Per User (ARPU) View
DROP VIEW IF EXISTS view_kpi_arpu;
CREATE VIEW view_kpi_arpu AS
SELECT
    strftime('%Y-%m', t.transaction_date) AS report_month,
    SUM(t.amount * 0.02) / COUNT(DISTINCT c.customer_id) AS monthly_arpu
FROM
    dim_customer c
JOIN
    dim_account a ON c.customer_id = a.customer_id
JOIN
    fact_transactions t ON a.account_id = t.account_id
GROUP BY
    strftime('%Y-%m', t.transaction_date);

-- 3. Customer Acquisition Cost (CAC) Proxy View
DROP VIEW IF EXISTS view_kpi_cac;
CREATE VIEW view_kpi_cac AS
SELECT
    strftime('%Y-%m', c.join_date) AS acquisition_month,
    m.budget,
    COUNT(DISTINCT c.customer_id) AS new_customers,
    m.budget / NULLIF(COUNT(DISTINCT c.customer_id), 0) AS cac_proxy
FROM
    dim_customer c
LEFT JOIN
    dim_campaign m ON strftime('%Y-%m', c.join_date) = strftime('%Y-%m', m.start_date)
GROUP BY
    strftime('%Y-%m', c.join_date),
    m.budget;

-- 4. Retention Rate View
DROP VIEW IF EXISTS view_kpi_retention;
CREATE VIEW view_kpi_retention AS
WITH MonthlyActive AS (
    SELECT
        strftime('%Y-%m', transaction_date) AS activity_month,
        customer_id
    FROM
        fact_transactions t
    JOIN
        dim_account a ON t.account_id = a.account_id
    GROUP BY
        strftime('%Y-%m', transaction_date),
        customer_id
)
SELECT
    m1.activity_month AS current_month,
    COUNT(DISTINCT m1.customer_id) AS active_customers,
    COUNT(DISTINCT m2.customer_id) AS retained_customers,
    CAST(COUNT(DISTINCT m2.customer_id) AS DECIMAL) / COUNT(DISTINCT m1.customer_id) * 100 AS retention_rate_pct
FROM
    MonthlyActive m1
LEFT JOIN
    MonthlyActive m2 ON m1.customer_id = m2.customer_id 
    AND m2.activity_month = m1.activity_month + '+1 month'
GROUP BY
    m1.activity_month;
