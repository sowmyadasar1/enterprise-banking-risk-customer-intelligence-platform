CREATE SCHEMA IF NOT EXISTS rpt;

-- View: Customer 360 Overview
CREATE OR REPLACE VIEW rpt.vw_customer_overview AS
SELECT
    c.customer_id, c.full_name, c.customer_type, c.risk_rating,
    c.is_active, c.tenure_years,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COALESCE(SUM(a.balance), 0) AS total_balance,
    COUNT(DISTINCT l.loan_id) AS total_loans,
    COALESCE(SUM(l.loan_amount), 0) AS total_loan_amount,
    COUNT(DISTINCT ft.transaction_id) AS total_transactions,
    COALESCE(SUM(ft.amount), 0) AS total_transaction_volume,
    COUNT(DISTINCT ff.case_id) AS fraud_cases_count
FROM dim.dim_customer c
LEFT JOIN dim.dim_account a ON c.customer_id = a.customer_id
LEFT JOIN dim.dim_loan l ON c.customer_id = l.customer_id
LEFT JOIN fact.fact_transactions ft ON a.account_id = ft.account_id
LEFT JOIN fact.fact_fraud ff ON c.customer_id = ff.customer_id
GROUP BY c.customer_id, c.full_name, c.customer_type, c.risk_rating,
         c.is_active, c.tenure_years;

-- View: Executive KPI
CREATE OR REPLACE VIEW rpt.vw_executive_kpi AS
SELECT
    (SELECT COUNT(*) FROM dim.dim_customer WHERE is_active = TRUE) AS total_customers,
    (SELECT COALESCE(SUM(balance), 0) FROM dim.dim_account WHERE account_type = 'Deposit') AS total_deposits,
    (SELECT COALESCE(SUM(loan_amount), 0) FROM dim.dim_loan) AS total_loans,
    (SELECT COUNT(*) FROM fact.fact_fraud WHERE status = 'Confirmed') * 100.0 / NULLIF((SELECT COUNT(*) FROM fact.fact_transactions), 0) AS fraud_rate,
    (SELECT AVG(satisfaction_score) FROM dim.dim_customer) AS avg_satisfaction,
    (SELECT COUNT(*) FROM dim.dim_account WHERE status = 'Active') AS active_accounts;

-- View: Revenue Summary
CREATE OR REPLACE VIEW rpt.vw_revenue_summary AS
SELECT
    b.branch_name,
    p.product_type,
    d.year,
    d.month,
    COALESCE(SUM(ft.fee_amount), 0) AS total_revenue
FROM fact.fact_transactions ft
JOIN dim.dim_branch b ON ft.branch_id = b.branch_id
JOIN dim.dim_product p ON ft.product_id = p.product_id
JOIN dim.dim_date d ON ft.transaction_date_id = d.date_id
GROUP BY b.branch_name, p.product_type, d.year, d.month;

-- View: Fraud Summary
CREATE OR REPLACE VIEW rpt.vw_fraud_summary AS
SELECT
    ff.fraud_type,
    ff.status,
    c.customer_type,
    COUNT(ff.case_id) AS case_count,
    COALESCE(SUM(ff.loss_amount), 0) AS total_loss_amount
FROM fact.fact_fraud ff
JOIN dim.dim_customer c ON ff.customer_id = c.customer_id
GROUP BY ff.fraud_type, ff.status, c.customer_type;

-- View: Loan Portfolio
CREATE OR REPLACE VIEW rpt.vw_loan_portfolio AS
SELECT
    l.loan_type,
    l.status,
    COUNT(l.loan_id) AS total_loans,
    COALESCE(SUM(l.loan_amount), 0) AS total_principal,
    COALESCE(SUM(l.outstanding_balance), 0) AS total_outstanding,
    COALESCE(SUM(CASE WHEN l.is_default = TRUE THEN 1 ELSE 0 END), 0) * 100.0 / COUNT(l.loan_id) AS default_rate
FROM dim.dim_loan l
GROUP BY l.loan_type, l.status;

-- View: Customer Lifetime Value
CREATE OR REPLACE VIEW rpt.vw_customer_lifetime_value AS
SELECT
    c.customer_id,
    c.full_name,
    c.tenure_years,
    COALESCE(SUM(a.balance), 0) AS total_deposits,
    COUNT(ft.transaction_id) AS total_transactions,
    (c.tenure_years * COALESCE(SUM(ft.fee_amount), 0)) AS estimated_clv
FROM dim.dim_customer c
LEFT JOIN dim.dim_account a ON c.customer_id = a.customer_id
LEFT JOIN fact.fact_transactions ft ON a.account_id = ft.account_id
GROUP BY c.customer_id, c.full_name, c.tenure_years;

-- View: Branch Performance
CREATE OR REPLACE VIEW rpt.vw_branch_performance AS
SELECT
    b.branch_id,
    b.branch_name,
    b.region,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COALESCE(SUM(a.balance), 0) AS total_deposits,
    COUNT(DISTINCT ft.transaction_id) AS total_transactions,
    COUNT(DISTINCT l.loan_id) AS total_loans
FROM dim.dim_branch b
LEFT JOIN dim.dim_account a ON b.branch_id = a.branch_id
LEFT JOIN fact.fact_transactions ft ON b.branch_id = ft.branch_id
LEFT JOIN dim.dim_loan l ON b.branch_id = l.branch_id
GROUP BY b.branch_id, b.branch_name, b.region;

-- View: Risk Overview
CREATE OR REPLACE VIEW rpt.vw_risk_overview AS
SELECT
    c.risk_rating,
    COUNT(c.customer_id) AS customer_count,
    AVG(c.credit_score) AS avg_credit_score,
    COALESCE(SUM(a.balance), 0) AS total_exposure
FROM dim.dim_customer c
LEFT JOIN dim.dim_account a ON c.customer_id = a.customer_id
GROUP BY c.risk_rating;
