/*
=============================================================================
Business Question: What is the health of the loan portfolio (approval, default rates, and outstanding balances)?
Business Interpretation: Provides a macro view of lending risk and portfolio growth.
Decision Supported: Adjusting underwriting criteria and capital allocation for loan products.
Recommended Business Action: Tighten lending for high-default loan types and promote low-risk products.
SQL Techniques Used: Aggregation (SUM, AVG), conditional aggregation, JOINs.
=============================================================================
*/

-- Loan Portfolio Analysis
SELECT
    l.loan_type,
    COUNT(f.loan_id) AS total_applications,
    SUM(CASE WHEN l.status = 'Approved' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.loan_id), 0) AS approval_rate_pct,
    SUM(CASE WHEN l.status = 'Default' THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN l.status IN ('Approved', 'Default', 'Active') THEN 1 ELSE 0 END), 0) AS default_rate_pct,
    SUM(f.loan_amount) AS total_loan_amount,
    AVG(f.interest_rate) AS avg_interest_rate
FROM fact_loans f
JOIN dim_loan l ON f.loan_id = l.loan_id
GROUP BY l.loan_type
ORDER BY total_loan_amount DESC;
