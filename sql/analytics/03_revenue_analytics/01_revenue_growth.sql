/*
=============================================================================
Business Question: How is revenue growing month over month?
Business Interpretation: Tracking MoM growth helps assess financial health and campaign effectiveness.
Decision Supported: Financial forecasting and executive performance reviews.
Recommended Business Action: Investigate months with negative growth to identify root causes.
SQL Techniques Used: LAG(), CTEs, Percentage calculations
=============================================================================
*/

WITH MonthlyRevenue AS (
    SELECT 
        d.year || '-' || printf('%02d', d.month) AS year_month,
        SUM(f.amount) AS total_revenue
    FROM fact_transactions f
    JOIN dim_date d ON f.transaction_date = d.full_date
    WHERE f.status = 'Success'
    GROUP BY d.year || '-' || printf('%02d', d.month)
),
RevenueWithLag AS (
    SELECT 
        year_month,
        total_revenue,
        LAG(total_revenue, 1) OVER(ORDER BY year_month) AS prev_month_revenue
    FROM MonthlyRevenue
)
SELECT 
    year_month,
    total_revenue,
    prev_month_revenue,
    CASE 
        WHEN prev_month_revenue IS NOT NULL AND prev_month_revenue > 0 
        THEN ROUND(((total_revenue - prev_month_revenue) / prev_month_revenue) * 100, 2)
        ELSE NULL 
    END AS mom_growth_percentage
FROM RevenueWithLag
ORDER BY year_month;