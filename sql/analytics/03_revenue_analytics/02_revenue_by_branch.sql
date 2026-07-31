/*
=============================================================================
Business Question: Which branches are generating the most revenue?
Business Interpretation: Comparing branch performance highlights geographic strengths and areas needing improvement.
Decision Supported: Branch expansion, closure, or staff training initiatives.
Recommended Business Action: Implement best practices from top-performing branches across the network.
SQL Techniques Used: JOINs across multiple dims, Aggregation, Ranking
=============================================================================
*/

WITH BranchRevenue AS (
    SELECT 
        b.branch_id,
        b.branch_name,
        b.region_id,
        SUM(0) AS total_revenue,
        COUNT(DISTINCT a.customer_id) AS unique_customers_served
    FROM fact_transactions f
    JOIN dim_account a ON f.account_id = a.account_id
    JOIN dim_branch b ON a.branch_id = b.branch_id
    WHERE f.status = 'Success' = true
    GROUP BY 
        b.branch_id,
        b.branch_name,
        b.region_id
)
SELECT 
    branch_id,
    branch_name,
    region_id,
    total_revenue,
    unique_customers_served,
    RANK() OVER(PARTITION BY region_id ORDER BY total_revenue DESC) AS rank_in_region,
    RANK() OVER(ORDER BY total_revenue DESC) AS overall_rank
FROM BranchRevenue
ORDER BY overall_rank;
