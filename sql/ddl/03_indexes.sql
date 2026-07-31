-- Indexes for fact.fact_transactions
CREATE INDEX idx_fact_transactions_account_id ON fact.fact_transactions(account_id);
CREATE INDEX idx_fact_transactions_merchant_id ON fact.fact_transactions(merchant_id);
CREATE INDEX idx_fact_transactions_transaction_date ON fact.fact_transactions(transaction_date);
CREATE INDEX idx_fact_transactions_status ON fact.fact_transactions(status);

-- Indexes for fact.fact_loans
CREATE INDEX idx_fact_loans_customer_id ON fact.fact_loans(customer_id);
CREATE INDEX idx_fact_loans_funding_account_id ON fact.fact_loans(funding_account_id);
CREATE INDEX idx_fact_loans_loan_id ON fact.fact_loans(loan_id);
CREATE INDEX idx_fact_loans_start_date ON fact.fact_loans(start_date);
CREATE INDEX idx_fact_loans_status ON fact.fact_loans(status);

-- Indexes for fact.fact_fraud
CREATE INDEX idx_fact_fraud_transaction_id ON fact.fact_fraud(transaction_id);
CREATE INDEX idx_fact_fraud_customer_id ON fact.fact_fraud(customer_id);
CREATE INDEX idx_fact_fraud_report_date ON fact.fact_fraud(report_date);
CREATE INDEX idx_fact_fraud_status ON fact.fact_fraud(status);

-- Indexes for fact.fact_loan_payments
CREATE INDEX idx_fact_loan_payments_loan_id ON fact.fact_loan_payments(loan_id);
CREATE INDEX idx_fact_loan_payments_payment_date ON fact.fact_loan_payments(payment_date);
CREATE INDEX idx_fact_loan_payments_status ON fact.fact_loan_payments(status);

-- Indexes for fact.fact_marketing_responses
CREATE INDEX idx_fact_marketing_responses_campaign_id ON fact.fact_marketing_responses(campaign_id);
CREATE INDEX idx_fact_marketing_responses_customer_id ON fact.fact_marketing_responses(customer_id);
CREATE INDEX idx_fact_marketing_responses_response_date ON fact.fact_marketing_responses(response_date);

-- Indexes for fact.fact_support_tickets
CREATE INDEX idx_fact_support_tickets_customer_id ON fact.fact_support_tickets(customer_id);
CREATE INDEX idx_fact_support_tickets_assigned_to_employee_id ON fact.fact_support_tickets(assigned_to_employee_id);
CREATE INDEX idx_fact_support_tickets_created_at ON fact.fact_support_tickets(created_at);
CREATE INDEX idx_fact_support_tickets_status ON fact.fact_support_tickets(status);

-- Indexes for fact.fact_customer_activity
CREATE INDEX idx_fact_customer_activity_customer_id ON fact.fact_customer_activity(customer_id);
CREATE INDEX idx_fact_customer_activity_login_timestamp ON fact.fact_customer_activity(login_timestamp);
CREATE INDEX idx_fact_customer_activity_status ON fact.fact_customer_activity(status);

-- Dimension indexes (for natural keys and common lookup columns)
CREATE INDEX idx_dim_customer_customer_id ON dim.dim_customer(customer_id);
CREATE INDEX idx_dim_customer_join_date ON dim.dim_customer(join_date);
CREATE INDEX idx_dim_customer_is_active ON dim.dim_customer(is_active);

CREATE INDEX idx_dim_account_account_id ON dim.dim_account(account_id);
CREATE INDEX idx_dim_account_customer_id ON dim.dim_account(customer_id);
CREATE INDEX idx_dim_account_branch_id ON dim.dim_account(branch_id);
CREATE INDEX idx_dim_account_status ON dim.dim_account(status);

CREATE INDEX idx_dim_loan_loan_id ON dim.dim_loan(loan_id);
CREATE INDEX idx_dim_loan_customer_id ON dim.dim_loan(customer_id);

CREATE INDEX idx_dim_risk_customer_id ON dim.dim_risk(customer_id);
CREATE INDEX idx_dim_risk_assessment_date ON dim.dim_risk(assessment_date);

CREATE INDEX idx_dim_merchant_merchant_id ON dim.dim_merchant(merchant_id);
CREATE INDEX idx_dim_campaign_campaign_id ON dim.dim_campaign(campaign_id);
CREATE INDEX idx_dim_campaign_start_date ON dim.dim_campaign(start_date);
CREATE INDEX idx_dim_campaign_status ON dim.dim_campaign(status);
