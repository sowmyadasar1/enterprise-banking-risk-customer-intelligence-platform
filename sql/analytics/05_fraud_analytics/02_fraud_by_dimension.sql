/*
=============================================================================
Business Question: Which merchants and regions have the highest fraud rates?
Business Interpretation: Highlights geographic and merchant-specific vulnerabilities to fraud.
Decision Supported: Blacklisting high-risk merchants or adjusting regional security protocols.
Recommended Business Action: Implement step-up authentication for transactions at high-risk merchants.
SQL Techniques Used: Aggregation (SUM, COUNT), JOINs, Group By.
=============================================================================
*/

-- Fraud Rate by Merchant and Region
SELECT
    m.merchant_name,
    m.country,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN (f.transaction_id IN (SELECT transaction_id FROM fact_fraud)) = 1 THEN 1 ELSE 0 END) AS fraud_transactions,
    SUM(CASE WHEN (f.transaction_id IN (SELECT transaction_id FROM fact_fraud)) = 1 THEN t.amount ELSE 0 END) AS total_fraud_amount,
    (SUM(CASE WHEN (f.transaction_id IN (SELECT transaction_id FROM fact_fraud)) = 1 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(t.transaction_id), 0) AS fraud_rate_pct
FROM fact_transactions t
JOIN fact_fraud f ON t.transaction_id = f.transaction_id
JOIN dim_merchant m ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_name, m.country
HAVING COUNT(t.transaction_id) > 100
ORDER BY fraud_rate_pct DESC;
