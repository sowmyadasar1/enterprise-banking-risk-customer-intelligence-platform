CREATE SCHEMA IF NOT EXISTS mart;

-- mart.executive_dashboard
CREATE OR REPLACE VIEW mart.executive_dashboard AS
SELECT
    CURRENT_DATE AS report_date,
    total_customers,
    total_deposits,
    total_loans,
    fraud_rate,
    avg_satisfaction,
    active_accounts
FROM rpt.vw_executive_kpi;

-- mart.fraud_analytics
CREATE OR REPLACE VIEW mart.fraud_analytics AS
SELECT
    fraud_type,
    status,
    customer_type,
    case_count,
    total_loss_amount
FROM rpt.vw_fraud_summary;

-- mart.customer_analytics
CREATE OR REPLACE VIEW mart.customer_analytics AS
SELECT
    customer_id,
    customer_type,
    risk_rating,
    is_active,
    tenure_years,
    total_accounts,
    total_balance,
    total_loans,
    total_loan_amount,
    total_transactions,
    total_transaction_volume,
    fraud_cases_count
FROM rpt.vw_customer_overview;

-- mart.loan_analytics
CREATE OR REPLACE VIEW mart.loan_analytics AS
SELECT
    loan_type,
    status,
    total_loans,
    total_principal,
    total_outstanding,
    default_rate
FROM rpt.vw_loan_portfolio;

-- mart.marketing_analytics
CREATE OR REPLACE VIEW mart.marketing_analytics AS
SELECT
    c.customer_type,
    COUNT(c.customer_id) AS targeted_customers,
    AVG(c.tenure_years) AS avg_tenure,
    COALESCE(SUM(clv.estimated_clv), 0) AS potential_clv
FROM dim.dim_customer c
LEFT JOIN rpt.vw_customer_lifetime_value clv ON c.customer_id = clv.customer_id
GROUP BY c.customer_type;

-- mart.operations_dashboard
CREATE OR REPLACE VIEW mart.operations_dashboard AS
SELECT
    b.region,
    COUNT(a.account_id) AS new_accounts,
    SUM(ft.fee_amount) AS total_fees_collected,
    COUNT(ft.transaction_id) AS total_transactions
FROM dim.dim_branch b
LEFT JOIN dim.dim_account a ON b.branch_id = a.branch_id
LEFT JOIN fact.fact_transactions ft ON b.branch_id = ft.branch_id
GROUP BY b.region;
