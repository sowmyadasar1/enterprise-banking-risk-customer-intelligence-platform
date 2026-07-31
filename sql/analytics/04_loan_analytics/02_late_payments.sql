/*
=============================================================================
Business Question: Which loans are at risk due to late payments?
Business Interpretation: Identifies loans exhibiting early warning signs of delinquency.
Decision Supported: Prioritizing collections and early intervention strategies.
Recommended Business Action: Trigger automated payment reminders or assign to collections team.
SQL Techniques Used: Window functions (ROW_NUMBER), CTEs, Date arithmetic.
=============================================================================
*/

-- Identify At-Risk Loans Based on Late Payments
WITH RankedPayments AS (
    SELECT
        f.loan_id,
        f.payment_date,
        f.amount_paid,
        ROW_NUMBER() OVER (PARTITION BY f.loan_id ORDER BY f.payment_date DESC) as recent_payment_rank
    FROM fact_loan_payments f
)
SELECT
    loan_id,
    payment_date,
    amount_paid
FROM RankedPayments
WHERE recent_payment_rank <= 3;