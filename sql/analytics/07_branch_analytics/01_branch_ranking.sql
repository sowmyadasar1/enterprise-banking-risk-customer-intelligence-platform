/*
=============================================================================
Business Question: Which branches are performing best in terms of transaction volume and active customers?
Business Interpretation: Identifies top-performing branches to understand drivers of success and allocate resources.
Decision Supported: Resource allocation, branch expansion, or consolidation strategies.
Recommended Business Action: Reward high-performing branches and investigate best practices to share with lower-performing branches.
SQL Techniques Used: CTEs, RANK() Window Function, Aggregation, JOINs
=============================================================================
*/

WITH BranchMetrics AS (
    SELECT
        b.branch_id,
        b.branch_name,
        b.region_id,
        COUNT(DISTINCT a.customer_id) AS active_customers,
        SUM(t.amount) AS total_transaction_volume,
        COUNT(t.transaction_id) AS total_transactions
    FROM
        dim_branch b
    JOIN
        dim_account a ON b.branch_id = a.branch_id
    JOIN
        fact_transactions t ON a.account_id = t.account_id
    WHERE
        t.transaction_date >= date('now', '-1 year')
    GROUP BY
        b.branch_id,
        b.branch_name,
        b.region_id
)
SELECT
    branch_id,
    branch_name,
    region_id,
    active_customers,
    total_transaction_volume,
    RANK() OVER(ORDER BY total_transaction_volume DESC) AS volume_rank,
    RANK() OVER(ORDER BY active_customers DESC) AS customer_rank
FROM
    BranchMetrics
ORDER BY
    volume_rank ASC;
