/*
=============================================================================
Business Question: What is the trend of transaction volume over time?
Business Interpretation: Identifying patterns and smoothing out volatility using moving averages.
Decision Supported: Capacity planning and seasonal staffing adjustments.
Recommended Business Action: Prepare infrastructure scaling before expected seasonal peaks.
SQL Techniques Used: AVG() OVER(ORDER BY ... ROWS BETWEEN ...), Aggregation, Date functions
=============================================================================
*/

WITH MonthlyAggregates AS (
    SELECT 
        d.year || '-' || printf('%02d', d.month) AS year_month,
        SUM(f.amount) AS total_volume,
        COUNT(f.transaction_id) AS transaction_count
    FROM fact_transactions f
    JOIN dim_date d ON f.transaction_date = d.full_date
    WHERE f.status = 'Success'
    GROUP BY d.year || '-' || printf('%02d', d.month)
)
SELECT 
    year_month,
    total_volume,
    transaction_count,
    AVG(total_volume) OVER(
        ORDER BY year_month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS volume_3m_moving_avg,
    AVG(transaction_count) OVER(
        ORDER BY year_month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS count_3m_moving_avg
FROM MonthlyAggregates
ORDER BY year_month;