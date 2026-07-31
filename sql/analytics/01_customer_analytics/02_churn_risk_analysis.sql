/*
=============================================================================
Business Question: Which customers are showing signs of becoming inactive or churning?
Business Interpretation: Customers with recent account closures or inactive statuses represent revenue at risk.
Decision Supported: Identifying target lists for customer win-back campaigns.
Recommended Business Action: Trigger automated engagement emails and promotional offers to high-risk customers.
SQL Techniques Used: Window functions, COUNT() OVER(), Aggregation, JOINs
=============================================================================
*/

WITH AccountStatus AS (
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        a.account_id,
        a.account_status,
        a.close_date
    FROM dim_customer c
    JOIN dim_account a ON c.customer_id = a.customer_id
),
CustomerRisk AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        COUNT(account_id) AS total_accounts,
        SUM(CASE WHEN account_status = 'Closed' THEN 1 ELSE 0 END) AS closed_accounts,
        MAX(close_date) AS most_recent_closure
    FROM AccountStatus
    GROUP BY 
        customer_id,
        first_name,
        last_name
)
SELECT 
    customer_id,
    first_name,
    last_name,
    total_accounts,
    closed_accounts,
    most_recent_closure,
    CASE 
        WHEN closed_accounts > 0 AND closed_accounts = total_accounts THEN 'High Risk - Fully Churned'
        WHEN closed_accounts > 0 AND closed_accounts < total_accounts THEN 'Medium Risk - Partial Churn'
        ELSE 'Low Risk - Active'
    END AS churn_risk_level
FROM CustomerRisk
ORDER BY closed_accounts DESC, most_recent_closure DESC NULLS LAST;
