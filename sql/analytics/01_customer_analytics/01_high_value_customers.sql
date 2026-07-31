/*
=============================================================================
Business Question: Who are our highest-value customers based on their total balances?
Business Interpretation: Identifying top customers allows for targeted premium services and retention efforts.
Decision Supported: Allocation of priority relationship managers and exclusive offers.
Recommended Business Action: Enroll top decile customers in the premium banking tier.
SQL Techniques Used: CTEs, Aggregation, DENSE_RANK(), NTILE(10), JOINs
=============================================================================
*/

WITH CustomerBalances AS (
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.customer_type,
        SUM(a.current_balance) AS total_balance
    FROM dim_customer c
    JOIN dim_account a ON c.customer_id = a.customer_id
    WHERE a.account_status = 'Active'
    GROUP BY 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.customer_type
)
SELECT 
    customer_id,
    first_name,
    last_name,
    customer_type,
    total_balance,
    DENSE_RANK() OVER(ORDER BY total_balance DESC) AS balance_rank,
    NTILE(10) OVER(ORDER BY total_balance DESC) AS wealth_decile
FROM CustomerBalances
ORDER BY total_balance DESC;
