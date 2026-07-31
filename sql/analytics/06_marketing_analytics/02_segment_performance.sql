/*
=============================================================================
Business Question: How do different customer risk segments respond to marketing offers?
Business Interpretation: Assesses the alignment between marketing targeting and customer risk profiles.
Decision Supported: Optimizing audience targeting for specialized financial products.
Recommended Business Action: Tailor premium credit offers to low-risk segments showing high acceptance rates.
SQL Techniques Used: Aggregation, multiple JOINs, Group By.
=============================================================================
*/

-- Offer Acceptance by Customer Risk Rating
SELECT
    c.risk_rating,
    c.customer_type,
    COUNT(m.response_id) AS offers_sent,
    SUM(CASE WHEN m.converted = 1 THEN 1 ELSE 0 END) AS offers_accepted,
    (SUM(CASE WHEN m.converted = 1 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(m.response_id), 0) AS acceptance_rate_pct
FROM fact_marketing_responses m
JOIN dim_customer c ON m.customer_id = c.customer_id
JOIN dim_risk r ON c.customer_id = r.customer_id
GROUP BY c.risk_rating, c.customer_type
ORDER BY acceptance_rate_pct DESC;