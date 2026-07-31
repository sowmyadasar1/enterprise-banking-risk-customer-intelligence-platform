-- Constraints for fact.fact_transactions
ALTER TABLE fact.fact_transactions
ADD CONSTRAINT fk_fact_transactions_account
FOREIGN KEY (account_id) REFERENCES dim.dim_account(account_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact.fact_transactions
ADD CONSTRAINT fk_fact_transactions_merchant
FOREIGN KEY (merchant_id) REFERENCES dim.dim_merchant(merchant_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_loans
ALTER TABLE fact.fact_loans
ADD CONSTRAINT fk_fact_loans_customer
FOREIGN KEY (customer_id) REFERENCES dim.dim_customer(customer_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact.fact_loans
ADD CONSTRAINT fk_fact_loans_funding_account
FOREIGN KEY (funding_account_id) REFERENCES dim.dim_account(account_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_fraud
ALTER TABLE fact.fact_fraud
ADD CONSTRAINT fk_fact_fraud_transaction
FOREIGN KEY (transaction_id) REFERENCES fact.fact_transactions(transaction_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact.fact_fraud
ADD CONSTRAINT fk_fact_fraud_customer
FOREIGN KEY (customer_id) REFERENCES dim.dim_customer(customer_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_loan_payments
ALTER TABLE fact.fact_loan_payments
ADD CONSTRAINT fk_fact_loan_payments_loan
FOREIGN KEY (loan_id) REFERENCES dim.dim_loan(loan_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_marketing_responses
ALTER TABLE fact.fact_marketing_responses
ADD CONSTRAINT fk_fact_marketing_responses_campaign
FOREIGN KEY (campaign_id) REFERENCES dim.dim_campaign(campaign_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact.fact_marketing_responses
ADD CONSTRAINT fk_fact_marketing_responses_customer
FOREIGN KEY (customer_id) REFERENCES dim.dim_customer(customer_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_support_tickets
ALTER TABLE fact.fact_support_tickets
ADD CONSTRAINT fk_fact_support_tickets_customer
FOREIGN KEY (customer_id) REFERENCES dim.dim_customer(customer_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact.fact_support_tickets
ADD CONSTRAINT fk_fact_support_tickets_employee
FOREIGN KEY (assigned_to_employee_id) REFERENCES dim.dim_employee(employee_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Constraints for fact.fact_customer_activity
ALTER TABLE fact.fact_customer_activity
ADD CONSTRAINT fk_fact_customer_activity_customer
FOREIGN KEY (customer_id) REFERENCES dim.dim_customer(customer_id)
ON DELETE RESTRICT ON UPDATE CASCADE;
