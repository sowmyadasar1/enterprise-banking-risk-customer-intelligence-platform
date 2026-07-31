/*
=============================================================================
Business Question: What is the ROI and conversion rate of marketing campaigns?
Business Interpretation: Evaluates the financial effectiveness of marketing initiatives.
Decision Supported: Budget allocation for future marketing campaigns.
Recommended Business Action: Scale up high-ROI campaigns and pause underperforming ones.
SQL Techniques Used: Aggregation, JOINs, Arithmetic calculations.
=============================================================================
*/

-- Campaign Conversion and ROI
SELECT
    c.campaign_name,
    r.channel,
    c.budget,
    COUNT(r.response_id) AS total_responses,
    SUM(CASE WHEN r.converted = 1 THEN 1 ELSE 0 END) AS total_conversions,
    (SUM(CASE WHEN r.converted = 1 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(r.response_id), 0) AS conversion_rate_pct,
    SUM((CAST(r.converted AS INTEGER) * 100)) AS total_revenue,
    (SUM((CAST(r.converted AS INTEGER) * 100)) - c.budget) / NULLIF(c.budget, 0) AS return_on_investment
FROM fact_marketing_responses r
JOIN dim_campaign c ON r.campaign_id = c.campaign_id
GROUP BY c.campaign_name, r.channel, c.budget
ORDER BY return_on_investment DESC;
