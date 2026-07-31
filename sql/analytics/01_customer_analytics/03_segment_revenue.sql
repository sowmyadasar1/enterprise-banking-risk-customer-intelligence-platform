/*
=============================================================================
Business Question: Which customer segments generate the most revenue?
Business Interpretation: Understanding revenue distribution across segments helps in resource allocation.
Decision Supported: Marketing budget allocation and product development focus.
Recommended Business Action: Increase marketing spend on the highest revenue-generating segments.
SQL Techniques Used: SUM() OVER(PARTITION BY ...), CTEs, JOINs across fact and dims
=============================================================================
*/

WITH SegmentTransactions AS (
    SELECT 
        c.customer_type,
        f.amount,
        0 AS fee_amount
    FROM fact_transactions f
    JOIN dim_account a ON f.account_id = a.account_id
    JOIN dim_customer c ON a.customer_id = c.customer_id
    JOIN dim_date d ON f.transaction_date = d.full_date
    WHERE f.status = 'Success'
)
SELECT DISTINCT
    customer_type,
    SUM(amount) OVER(PARTITION BY customer_type) AS total_transaction_volume,
    SUM(fee_amount) OVER(PARTITION BY customer_type) AS total_revenue,
    COUNT(*) OVER(PARTITION BY customer_type) AS transaction_count
FROM SegmentTransactions
ORDER BY total_revenue DESC;
