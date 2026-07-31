/*
=============================================================================
Business Question: What is the distribution of high-risk customers across our portfolio?
Business Interpretation: Assesses the overall risk exposure and identifies segments with the highest concentration of high-risk customers.
Decision Supported: Risk mitigation strategies, credit limit adjustments, and targeted interventions.
Recommended Business Action: Implement stricter monitoring for high-risk segments and consider adjusting credit policies.
SQL Techniques Used: CTEs, Aggregation, Window Functions (Percent of Total), JOINs
=============================================================================
*/

WITH CustomerRisk AS (
    SELECT
        r.risk_category,
        r.risk_category,
        COUNT(DISTINCT c.customer_id) AS customer_count,
        SUM(a.current_balance) AS total_exposure
    FROM
        dim_risk r
    JOIN
        dim_customer c ON c.risk_rating = c.risk_rating
    JOIN
        dim_account a ON c.customer_id = a.customer_id
    GROUP BY
        r.risk_category,
        r.risk_category
),
TotalPortfolio AS (
    SELECT
        SUM(customer_count) AS total_customers,
        SUM(total_exposure) AS total_portfolio_exposure
    FROM
        CustomerRisk
)
SELECT
    cr.risk_category,
    cr.risk_category,
    cr.customer_count,
    cr.total_exposure,
    ROUND(CAST(cr.customer_count AS DECIMAL) / tp.total_customers * 100, 2) AS pct_of_total_customers,
    ROUND(cr.total_exposure / tp.total_portfolio_exposure * 100, 2) AS pct_of_portfolio_exposure
FROM
    CustomerRisk cr
CROSS JOIN
    TotalPortfolio tp
ORDER BY
    cr.total_exposure DESC;
