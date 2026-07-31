-- Fact_Transactions (from transactions.parquet)
CREATE TABLE fact.fact_transactions (
    transaction_key   SERIAL PRIMARY KEY,
    transaction_id    VARCHAR(20) NOT NULL UNIQUE,
    account_id        VARCHAR(20),     -- FK dim_account
    merchant_id       VARCHAR(20),     -- FK dim_merchant
    transaction_type_id VARCHAR(20),
    amount            NUMERIC(15,2) NOT NULL,
    currency          VARCHAR(3),
    transaction_date  DATE,
    transaction_timestamp TIMESTAMP,
    channel           VARCHAR(20),
    status            VARCHAR(20),
    transaction_hour  INTEGER,
    transaction_day_of_week INTEGER,
    transaction_month INTEGER,
    transaction_quarter INTEGER,
    is_weekend        BOOLEAN DEFAULT FALSE,
    is_night_transaction BOOLEAN DEFAULT FALSE,
    amount_abs        NUMERIC(15,2),
    is_large_transaction BOOLEAN DEFAULT FALSE,
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_transactions.transaction_key IS 'Surrogate key for the transaction';
COMMENT ON COLUMN fact.fact_transactions.transaction_id IS 'Natural key for the transaction';

-- Fact_Loans (snapshot: from loans.parquet)
CREATE TABLE fact.fact_loans (
    loan_fact_key     SERIAL PRIMARY KEY,
    loan_id           VARCHAR(20) NOT NULL,
    customer_id       VARCHAR(20),
    funding_account_id VARCHAR(20),
    loan_type         VARCHAR(50),
    loan_amount       NUMERIC(15,2),
    principal_balance NUMERIC(15,2),
    interest_rate     NUMERIC(6,4),
    start_date        DATE,
    term_months       INTEGER,
    status            VARCHAR(20),
    end_date          DATE,
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_loans.loan_fact_key IS 'Surrogate key for the loan fact';
COMMENT ON COLUMN fact.fact_loans.loan_id IS 'Natural key for the loan';

-- Fact_Fraud (from fraud_cases.parquet + fraud_investigations.parquet)
CREATE TABLE fact.fact_fraud (
    fraud_fact_key    SERIAL PRIMARY KEY,
    case_id           VARCHAR(20) NOT NULL UNIQUE,
    transaction_id    VARCHAR(20),
    customer_id       VARCHAR(20),
    report_date       DATE,
    fraud_type        VARCHAR(50),
    amount_involved   NUMERIC(15,2),
    status            VARCHAR(20),
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_fraud.fraud_fact_key IS 'Surrogate key for the fraud case fact';
COMMENT ON COLUMN fact.fact_fraud.case_id IS 'Natural key for the fraud case';

-- Fact_LoanPayments (from loan_payments.parquet)
CREATE TABLE fact.fact_loan_payments (
    payment_key       SERIAL PRIMARY KEY,
    payment_id        VARCHAR(20) NOT NULL UNIQUE,
    loan_id           VARCHAR(20),
    payment_date      DATE,
    total_amount      NUMERIC(15,2),
    principal_amount  NUMERIC(15,2),
    interest_amount   NUMERIC(15,2),
    status            VARCHAR(20),
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_loan_payments.payment_key IS 'Surrogate key for the loan payment';
COMMENT ON COLUMN fact.fact_loan_payments.payment_id IS 'Natural key for the loan payment';

-- Fact_MarketingResponses (from campaign_responses.parquet)
CREATE TABLE fact.fact_marketing_responses (
    response_key      SERIAL PRIMARY KEY,
    response_id       VARCHAR(20) NOT NULL UNIQUE,
    campaign_id       VARCHAR(20),
    customer_id       VARCHAR(20),
    response_type     VARCHAR(50),
    response_date     DATE,
    channel           VARCHAR(20),
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_marketing_responses.response_key IS 'Surrogate key for the marketing response';
COMMENT ON COLUMN fact.fact_marketing_responses.response_id IS 'Natural key for the marketing response';

-- Fact_SupportTickets (from support_tickets.parquet)
CREATE TABLE fact.fact_support_tickets (
    ticket_key        SERIAL PRIMARY KEY,
    ticket_id         VARCHAR(20) NOT NULL UNIQUE,
    customer_id       VARCHAR(20),
    issue_category    VARCHAR(50),
    priority          VARCHAR(20),
    status            VARCHAR(20),
    created_at        TIMESTAMP,
    resolved_at       TIMESTAMP,
    assigned_to_employee_id VARCHAR(20),
    satisfaction_score NUMERIC(3,1),
    resolution_hours  NUMERIC(10,2),  -- derived: hours between created and resolved
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_support_tickets.ticket_key IS 'Surrogate key for the support ticket';
COMMENT ON COLUMN fact.fact_support_tickets.ticket_id IS 'Natural key for the support ticket';

-- Fact_CustomerActivity (aggregated from login_history.parquet)
CREATE TABLE fact.fact_customer_activity (
    activity_key      SERIAL PRIMARY KEY,
    login_id          VARCHAR(20) NOT NULL UNIQUE,
    customer_id       VARCHAR(20),
    device_id         VARCHAR(20),
    login_timestamp   TIMESTAMP,
    ip_address        VARCHAR(50),
    location          VARCHAR(100),
    status            VARCHAR(20),
    etl_loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN fact.fact_customer_activity.activity_key IS 'Surrogate key for the customer activity';
COMMENT ON COLUMN fact.fact_customer_activity.login_id IS 'Natural key for the login event';
