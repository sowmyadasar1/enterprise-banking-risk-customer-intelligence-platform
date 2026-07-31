-- Dim_Date (from calendar.parquet: date_id, full_date, year, month, day, quarter, day_of_week, day_name, is_weekend, is_holiday)
CREATE TABLE dim.dim_date (
    date_key        INTEGER PRIMARY KEY,  -- surrogate key = date_id
    full_date       DATE NOT NULL,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    day             INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
    quarter         INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    day_of_week     INTEGER NOT NULL,
    day_name        VARCHAR(10) NOT NULL,
    is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
    is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
    month_name      VARCHAR(10),
    fiscal_year     INTEGER,
    fiscal_quarter  INTEGER,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_date.date_key IS 'Surrogate key for the date, typically YYYYMMDD';
COMMENT ON COLUMN dim.dim_date.full_date IS 'The actual date value';

-- Dim_Customer (from customers.parquet: customer_id, first_name, last_name, date_of_birth, gender, email, phone_number, join_date, customer_type, risk_rating, is_active, tenure_days, tenure_years, is_long_tenured)
CREATE TABLE dim.dim_customer (
    customer_key    SERIAL PRIMARY KEY,   -- surrogate key
    customer_id     VARCHAR(20) NOT NULL UNIQUE,  -- natural key
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    full_name       VARCHAR(200),  -- derived: first_name || ' ' || last_name
    date_of_birth   DATE,
    gender          VARCHAR(10),
    email           VARCHAR(200),
    phone_number    VARCHAR(20),
    join_date       DATE,
    customer_type   VARCHAR(20),
    risk_rating     VARCHAR(20),
    is_active       BOOLEAN DEFAULT TRUE,
    tenure_days     INTEGER,
    tenure_years    NUMERIC(6,2),
    is_long_tenured BOOLEAN DEFAULT FALSE,
    effective_from  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to    TIMESTAMP,
    is_current      BOOLEAN DEFAULT TRUE,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_customer.customer_key IS 'Surrogate key for the customer';
COMMENT ON COLUMN dim.dim_customer.customer_id IS 'Natural key from the source system';

-- Dim_Branch (from branches.parquet: branch_id, branch_name, region_id, address, city, state, zip_code, phone_number, open_date)
CREATE TABLE dim.dim_branch (
    branch_key      SERIAL PRIMARY KEY,
    branch_id       VARCHAR(20) NOT NULL UNIQUE,
    branch_name     VARCHAR(200),
    region_id       VARCHAR(20),
    address         VARCHAR(300),
    city            VARCHAR(100),
    state           VARCHAR(50),
    zip_code        VARCHAR(20),
    phone_number    VARCHAR(20),
    open_date       DATE,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_branch.branch_key IS 'Surrogate key for the branch';
COMMENT ON COLUMN dim.dim_branch.branch_id IS 'Natural key for the branch';

-- Dim_Region (from regions.parquet: region_id, region_name, country, regional_manager_id)
CREATE TABLE dim.dim_region (
    region_key      SERIAL PRIMARY KEY,
    region_id       VARCHAR(20) NOT NULL UNIQUE,
    region_name     VARCHAR(100),
    country         VARCHAR(100),
    regional_manager_id VARCHAR(20),
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_region.region_key IS 'Surrogate key for the region';
COMMENT ON COLUMN dim.dim_region.region_id IS 'Natural key for the region';

-- Dim_Product (from products.parquet: product_id, product_name, product_type, interest_rate, minimum_balance, monthly_fee, is_active, launch_date)
CREATE TABLE dim.dim_product (
    product_key     SERIAL PRIMARY KEY,
    product_id      VARCHAR(20) NOT NULL UNIQUE,
    product_name    VARCHAR(200),
    product_type    VARCHAR(50),
    interest_rate   NUMERIC(6,4),
    minimum_balance NUMERIC(15,2),
    monthly_fee     NUMERIC(10,2),
    is_active       BOOLEAN DEFAULT TRUE,
    launch_date     DATE,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_product.product_key IS 'Surrogate key for the product';
COMMENT ON COLUMN dim.dim_product.product_id IS 'Natural key for the product';

-- Dim_Merchant (from merchants.parquet: merchant_id, category_id, merchant_name, country, risk_score, created_at)
CREATE TABLE dim.dim_merchant (
    merchant_key    SERIAL PRIMARY KEY,
    merchant_id     VARCHAR(20) NOT NULL UNIQUE,
    category_id     VARCHAR(20),
    merchant_name   VARCHAR(200),
    country         VARCHAR(100),
    risk_score      NUMERIC(5,2),
    created_at      TIMESTAMP,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_merchant.merchant_key IS 'Surrogate key for the merchant';
COMMENT ON COLUMN dim.dim_merchant.merchant_id IS 'Natural key for the merchant';

-- Dim_Account (from accounts.parquet: account_id, customer_id, branch_id, account_type, balance, currency, open_date, status, interest_rate, is_overdrawn)
CREATE TABLE dim.dim_account (
    account_key     SERIAL PRIMARY KEY,
    account_id      VARCHAR(20) NOT NULL UNIQUE,
    customer_id     VARCHAR(20),
    branch_id       VARCHAR(20),
    account_type    VARCHAR(50),
    balance         NUMERIC(15,2),
    currency        VARCHAR(3),
    open_date       DATE,
    status          VARCHAR(20),
    interest_rate   NUMERIC(6,4),
    is_overdrawn    BOOLEAN DEFAULT FALSE,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_account.account_key IS 'Surrogate key for the account';
COMMENT ON COLUMN dim.dim_account.account_id IS 'Natural key for the account';

-- Dim_Loan (from loans.parquet: loan_id, customer_id, funding_account_id, loan_type, loan_amount, principal_balance, interest_rate, start_date, term_months, status, end_date)
CREATE TABLE dim.dim_loan (
    loan_key        SERIAL PRIMARY KEY,
    loan_id         VARCHAR(20) NOT NULL UNIQUE,
    customer_id     VARCHAR(20),
    funding_account_id VARCHAR(20),
    loan_type       VARCHAR(50),
    loan_amount     NUMERIC(15,2),
    principal_balance NUMERIC(15,2),
    interest_rate   NUMERIC(6,4),
    start_date      DATE,
    term_months     INTEGER,
    status          VARCHAR(20),
    end_date        DATE,
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_loan.loan_key IS 'Surrogate key for the loan';
COMMENT ON COLUMN dim.dim_loan.loan_id IS 'Natural key for the loan';

-- Dim_Risk (from customer_risk_scores.parquet: risk_id, customer_id, risk_score, risk_category, assessment_date, model_version)
CREATE TABLE dim.dim_risk (
    risk_key        SERIAL PRIMARY KEY,
    risk_id         VARCHAR(20) NOT NULL UNIQUE,
    customer_id     VARCHAR(20),
    risk_score      INTEGER,
    risk_category   VARCHAR(50),
    assessment_date DATE,
    model_version   VARCHAR(20),
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_risk.risk_key IS 'Surrogate key for the risk score';
COMMENT ON COLUMN dim.dim_risk.risk_id IS 'Natural key for the risk score';

-- Dim_Campaign (from marketing_campaigns.parquet: campaign_id, campaign_name, campaign_type, target_audience, start_date, end_date, budget, status)
CREATE TABLE dim.dim_campaign (
    campaign_key    SERIAL PRIMARY KEY,
    campaign_id     VARCHAR(20) NOT NULL UNIQUE,
    campaign_name   VARCHAR(200),
    campaign_type   VARCHAR(50),
    target_audience VARCHAR(100),
    start_date      DATE,
    end_date        DATE,
    budget          NUMERIC(15,2),
    status          VARCHAR(20),
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_campaign.campaign_key IS 'Surrogate key for the marketing campaign';
COMMENT ON COLUMN dim.dim_campaign.campaign_id IS 'Natural key for the marketing campaign';

-- Dim_Employee (from employees.parquet: employee_id, first_name, last_name, email, phone, job_title)
CREATE TABLE dim.dim_employee (
    employee_key    SERIAL PRIMARY KEY,
    employee_id     VARCHAR(20) NOT NULL UNIQUE,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    full_name       VARCHAR(200),
    email           VARCHAR(200),
    phone           VARCHAR(20),
    job_title       VARCHAR(100),
    etl_loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN dim.dim_employee.employee_key IS 'Surrogate key for the employee';
COMMENT ON COLUMN dim.dim_employee.employee_id IS 'Natural key for the employee';
