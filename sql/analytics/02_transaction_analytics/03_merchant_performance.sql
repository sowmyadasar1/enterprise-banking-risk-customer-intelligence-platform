/*
=============================================================================
Business Question: Which merchants process the largest transactions and highest volumes?
Business Interpretation: High-volume merchants are critical B2B clients that require strong relationship management.
Decision Supported: B2B fee negotiation and dedicated support allocation.
Recommended Business Action: Offer volume-based discount tiers to top 10 ranked merchants to encourage exclusivity.
SQL Techniques Used: Aggregation, RANK() OVER(), JOINs
=============================================================================
*/

WITH MerchantStats AS (
    SELECT 
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        COUNT(f.transaction_id) AS total_transactions,
        SUM(f.amount) AS total_volume,
        MAX(f.amount) AS max_single_transaction
    FROM fact_transactions f
    JOIN dim_merchant m ON f.merchant_id = m.merchant_id
    WHERE f.status = 'Success'
    GROUP BY 
        m.merchant_id,
        m.merchant_name,
        m.merchant_category
)
SELECT 
    merchant_id,
    merchant_name,
    merchant_category,
    total_transactions,
    total_volume,
    max_single_transaction,
    RANK() OVER(ORDER BY total_volume DESC) AS volume_rank
FROM MerchantStats
ORDER BY volume_rank;
