/*
=============================================================================
Business Question: When do most transactions occur during the day?
Business Interpretation: Discovering peak usage hours by transaction type to optimize system availability.
Decision Supported: System maintenance scheduling and IT resource scaling.
Recommended Business Action: Schedule system downtime during the lowest-ranked transaction hours.
SQL Techniques Used: RANK() OVER(), EXTRACT(), CTEs
=============================================================================
*/

WITH HourlyVolumes AS (
    SELECT 
        f.transaction_type_id,
        CAST(strftime('%H', f.transaction_timestamp) AS INTEGER) AS hour_of_day,
        COUNT(f.transaction_id) AS transaction_count,
        SUM(f.amount) AS total_amount
    FROM fact_transactions f
    WHERE f.status = 'Success'
    GROUP BY 
        f.transaction_type_id,
        CAST(strftime('%H', f.transaction_timestamp) AS INTEGER)
)
SELECT 
    transaction_type_id,
    hour_of_day,
    transaction_count,
    total_amount,
    RANK() OVER(PARTITION BY transaction_type_id ORDER BY transaction_count DESC) AS peak_hour_rank
FROM HourlyVolumes
ORDER BY transaction_type_id, peak_hour_rank;
