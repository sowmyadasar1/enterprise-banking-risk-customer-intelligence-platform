# Enterprise Banking Risk & Customer Intelligence Platform - Data Dictionary

This document outlines the data dictionary for all 29 datasets in the Enterprise Banking Risk & Customer Intelligence Platform.

## 1. Customers
- **Business Purpose**: Core entity representing the bank's clients.
- **Description**: Contains demographic and profile information of customers.
- **Expected Row Count**: 10M
- **Primary Key**: `customer_id`
- **Foreign Keys**: `branch_id`, `geo_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| customer_id | VARCHAR(50) | No | Unique identifier for the customer | CUST-10001 | UNIQUE |
| first_name | VARCHAR(100) | No | Customer's first name | John | |
| last_name | VARCHAR(100) | No | Customer's last name | Doe | |
| date_of_birth | DATE | No | Date of birth | 1980-05-12 | < Current Date |
| email | VARCHAR(255) | Yes | Email address | john.doe@example.com | Valid Email format |
| phone_number | VARCHAR(20) | Yes | Contact number | +1-555-0198 | |
| income_bracket | VARCHAR(50) | Yes | Annual income range | $50k-$100k | |
| branch_id | VARCHAR(50) | Yes | Primary branch | BR-101 | FK to Branches |
| geo_id | VARCHAR(50) | Yes | Geography ID | GEO-US-NY | FK to Geographies |
| created_at | TIMESTAMP | No | Record creation time | 2020-01-01 10:00:00 | |

## 2. Accounts
- **Business Purpose**: Core banking accounts held by customers.
- **Description**: Information about savings, checking, and fixed deposit accounts.
- **Expected Row Count**: 25M
- **Primary Key**: `account_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| account_id | VARCHAR(50) | No | Unique identifier for account | ACC-50001 | UNIQUE |
| customer_id | VARCHAR(50) | No | Owner of the account | CUST-10001 | FK to Customers |
| account_type | VARCHAR(50) | No | Type of account | Checking | Checking, Savings, FD |
| balance | DECIMAL(15,2)| No | Current balance | 5432.10 | >= 0 (usually) |
| currency | VARCHAR(3) | No | Currency of account | USD | Valid ISO Code |
| status | VARCHAR(20) | No | Account status | Active | Active, Closed, Frozen |
| opened_date | DATE | No | Date account opened | 2020-01-05 | |

## 3. Transactions
- **Business Purpose**: Record of all money movements.
- **Description**: Debits, credits, transfers across accounts.
- **Expected Row Count**: 1B+
- **Primary Key**: `transaction_id`
- **Foreign Keys**: `account_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| transaction_id | VARCHAR(50) | No | Unique transaction ID | TXN-99901 | UNIQUE |
| account_id | VARCHAR(50) | No | Account involved | ACC-50001 | FK to Accounts |
| transaction_type | VARCHAR(50) | No | Type of transaction | Withdrawal | Deposit, Withdrawal, Transfer |
| amount | DECIMAL(15,2)| No | Transaction amount | 150.00 | > 0 |
| transaction_date | TIMESTAMP | No | Time of transaction | 2023-10-12 14:32:00 | |
| description | VARCHAR(255) | Yes | Txn details | ATM Withdrawal | |
| merchant_category| VARCHAR(100) | Yes | MCC if applicable | Groceries | |

## 4. Branches
- **Business Purpose**: Physical and virtual bank branches.
- **Description**: Details about bank branches.
- **Expected Row Count**: 5,000
- **Primary Key**: `branch_id`
- **Foreign Keys**: `geo_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| branch_id | VARCHAR(50) | No | Unique branch ID | BR-101 | UNIQUE |
| branch_name | VARCHAR(100) | No | Name of branch | Downtown NY | |
| geo_id | VARCHAR(50) | No | Geography ID | GEO-US-NY | FK to Geographies |
| manager_id | VARCHAR(50) | Yes | Employee ID of manager | EMP-001 | FK to Employees |

## 5. Employees
- **Business Purpose**: Bank staff.
- **Description**: Details about employees working in branches and HQ.
- **Expected Row Count**: 50,000
- **Primary Key**: `employee_id`
- **Foreign Keys**: `branch_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| employee_id | VARCHAR(50) | No | Unique employee ID | EMP-001 | UNIQUE |
| first_name | VARCHAR(100) | No | First name | Alice | |
| last_name | VARCHAR(100) | No | Last name | Smith | |
| role | VARCHAR(100) | No | Job title | Branch Manager | |
| branch_id | VARCHAR(50) | Yes | Assigned branch | BR-101 | FK to Branches |

## 6. Cards
- **Business Purpose**: Credit and debit cards issued to customers.
- **Description**: Card details, status, and limits.
- **Expected Row Count**: 15M
- **Primary Key**: `card_id`
- **Foreign Keys**: `account_id`, `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| card_id | VARCHAR(50) | No | Unique card ID | CARD-881 | UNIQUE |
| customer_id | VARCHAR(50) | No | Cardholder | CUST-10001 | FK to Customers |
| account_id | VARCHAR(50) | Yes | Linked account | ACC-50001 | FK to Accounts |
| card_type | VARCHAR(50) | No | Credit or Debit | Credit | Credit, Debit |
| credit_limit | DECIMAL(15,2)| Yes | Limit (if credit) | 10000.00 | >= 0 |
| status | VARCHAR(20) | No | Card status | Active | Active, Blocked, Expired |

## 7. Loans
- **Business Purpose**: Master record of loans.
- **Description**: Details on disbursed loans.
- **Expected Row Count**: 5M
- **Primary Key**: `loan_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| loan_id | VARCHAR(50) | No | Unique loan ID | LN-5543 | UNIQUE |
| customer_id | VARCHAR(50) | No | Borrower | CUST-10001 | FK to Customers |
| loan_type | VARCHAR(50) | No | Type of loan | Mortgage | Mortgage, Auto, Personal |
| principal_amount | DECIMAL(15,2)| No | Original amount | 350000.00 | > 0 |
| interest_rate | DECIMAL(5,4) | No | Annual interest rate | 0.0525 | >= 0 |
| term_months | INT | No | Duration in months | 360 | > 0 |
| status | VARCHAR(20) | No | Loan status | Active | Active, Paid, Defaulted |

## 8. Loan_Applications
- **Business Purpose**: Tracking loan application process.
- **Description**: Submissions, approvals, and rejections of loan requests.
- **Expected Row Count**: 15M
- **Primary Key**: `application_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| application_id | VARCHAR(50) | No | Unique app ID | LAPP-112 | UNIQUE |
| customer_id | VARCHAR(50) | No | Applicant | CUST-10001 | FK to Customers |
| requested_amount | DECIMAL(15,2)| No | Amount requested | 350000.00 | > 0 |
| status | VARCHAR(20) | No | App status | Approved | Pending, Approved, Rejected |
| application_date | DATE | No | Date submitted | 2022-05-10 | |

## 9. Collateral
- **Business Purpose**: Assets pledged for loans.
- **Description**: Valuation and details of collateral.
- **Expected Row Count**: 4M
- **Primary Key**: `collateral_id`
- **Foreign Keys**: `loan_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| collateral_id | VARCHAR(50) | No | Unique collateral ID | COL-992 | UNIQUE |
| loan_id | VARCHAR(50) | No | Associated loan | LN-5543 | FK to Loans |
| collateral_type | VARCHAR(50) | No | Asset type | Real Estate | Real Estate, Vehicle |
| estimated_value| DECIMAL(15,2)| No | Value of asset | 400000.00 | > 0 |
| valuation_date | DATE | No | Date of valuation | 2022-05-01 | |

## 10. Credit_Scores
- **Business Purpose**: Customer credit risk assessment.
- **Description**: Periodic credit scores for customers.
- **Expected Row Count**: 120M (Historical)
- **Primary Key**: `score_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| score_id | VARCHAR(50) | No | Unique score record ID| CS-0012 | UNIQUE |
| customer_id | VARCHAR(50) | No | Subject customer | CUST-10001 | FK to Customers |
| credit_score | INT | No | Numeric score | 720 | 300 to 850 |
| agency | VARCHAR(50) | No | Credit agency | Equifax | |
| score_date | DATE | No | Date scored | 2023-01-01 | |

## 11. Repayments
- **Business Purpose**: Tracking loan payments.
- **Description**: Installments paid towards loans.
- **Expected Row Count**: 150M
- **Primary Key**: `repayment_id`
- **Foreign Keys**: `loan_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| repayment_id | VARCHAR(50) | No | Unique repayment ID | REP-332 | UNIQUE |
| loan_id | VARCHAR(50) | No | Loan being paid | LN-5543 | FK to Loans |
| amount_paid | DECIMAL(15,2)| No | Amount paid | 1500.00 | > 0 |
| payment_date | DATE | No | Date of payment | 2023-06-01 | |
| principal_portion| DECIMAL(15,2)| Yes | Principal paid | 900.00 | |
| interest_portion | DECIMAL(15,2)| Yes | Interest paid | 600.00 | |

## 12. Delinquencies
- **Business Purpose**: Risk tracking for late payments.
- **Description**: Records of missed loan payments and aging.
- **Expected Row Count**: 5M
- **Primary Key**: `delinquency_id`
- **Foreign Keys**: `loan_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| delinquency_id | VARCHAR(50) | No | Unique delinquency ID | DEL-112 | UNIQUE |
| loan_id | VARCHAR(50) | No | Delinquent loan | LN-5543 | FK to Loans |
| days_past_due | INT | No | DPD | 30 | > 0 |
| report_date | DATE | No | Date reported | 2023-07-01 | |

## 13. Portfolios
- **Business Purpose**: Wealth management portfolios.
- **Description**: Groups of investment assets for a customer.
- **Expected Row Count**: 2M
- **Primary Key**: `portfolio_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| portfolio_id | VARCHAR(50) | No | Unique portfolio ID | PORT-11 | UNIQUE |
| customer_id | VARCHAR(50) | No | Owner | CUST-10001 | FK to Customers |
| risk_profile | VARCHAR(50) | No | Target risk level | Aggressive | |
| total_value | DECIMAL(15,2)| No | Current total value | 150000.00 | >= 0 |

## 14. Holdings
- **Business Purpose**: Specific assets within a portfolio.
- **Description**: Equities, bonds, mutual funds held.
- **Expected Row Count**: 20M
- **Primary Key**: `holding_id`
- **Foreign Keys**: `portfolio_id`, `asset_id` (Market_Data)

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| holding_id | VARCHAR(50) | No | Unique holding ID | HOLD-22 | UNIQUE |
| portfolio_id | VARCHAR(50) | No | Portfolio containing it | PORT-11 | FK to Portfolios |
| asset_id | VARCHAR(50) | No | Asset identifier | AAPL | FK to Market_Data |
| quantity | DECIMAL(15,4)| No | Number of units held | 100.5 | > 0 |
| average_cost | DECIMAL(15,2)| No | Cost basis | 150.25 | > 0 |

## 15. Trades
- **Business Purpose**: Investment transactions.
- **Description**: Buy and sell orders for investments.
- **Expected Row Count**: 50M
- **Primary Key**: `trade_id`
- **Foreign Keys**: `portfolio_id`, `asset_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| trade_id | VARCHAR(50) | No | Unique trade ID | TRD-88 | UNIQUE |
| portfolio_id | VARCHAR(50) | No | Portfolio traded for | PORT-11 | FK to Portfolios |
| asset_id | VARCHAR(50) | No | Asset traded | AAPL | FK to Market_Data |
| trade_type | VARCHAR(10) | No | Buy or Sell | Buy | Buy, Sell |
| quantity | DECIMAL(15,4)| No | Units traded | 50.0 | > 0 |
| execution_price| DECIMAL(15,2)| No | Price per unit | 155.00 | > 0 |
| trade_date | TIMESTAMP | No | Time of trade | 2023-11-01 10:30:00| |

## 16. Market_Data
- **Business Purpose**: Reference for investment assets.
- **Description**: Tickers, names, and current prices.
- **Expected Row Count**: 100,000
- **Primary Key**: `asset_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| asset_id | VARCHAR(50) | No | Ticker or ISIN | AAPL | UNIQUE |
| asset_name | VARCHAR(255) | No | Name of asset | Apple Inc. | |
| asset_class | VARCHAR(50) | No | Equity, Bond, etc. | Equity | |
| current_price | DECIMAL(15,2)| Yes | Latest market price | 175.50 | > 0 |

## 17. Fraud_Alerts
- **Business Purpose**: Tracking suspected fraudulent activity.
- **Description**: Alerts generated by ML models or rule engines.
- **Expected Row Count**: 500,000
- **Primary Key**: `alert_id`
- **Foreign Keys**: `transaction_id`, `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| alert_id | VARCHAR(50) | No | Unique alert ID | ALT-099 | UNIQUE |
| transaction_id | VARCHAR(50) | Yes | Suspicious transaction| TXN-99901 | FK to Transactions |
| customer_id | VARCHAR(50) | Yes | Suspicious customer | CUST-10001 | FK to Customers |
| risk_score | DECIMAL(5,2) | No | Model fraud score | 0.89 | 0.0 to 1.0 |
| alert_status | VARCHAR(20) | No | Status of investigation| Open | Open, Closed-True Positive, Closed-False Positive |
| created_at | TIMESTAMP | No | Alert generation time | 2023-10-12 14:35:00| |

## 18. KYC_Documents
- **Business Purpose**: Compliance and identity verification.
- **Description**: Tracking uploaded ID documents.
- **Expected Row Count**: 15M
- **Primary Key**: `document_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| document_id | VARCHAR(50) | No | Unique doc ID | DOC-441 | UNIQUE |
| customer_id | VARCHAR(50) | No | Owner of document | CUST-10001 | FK to Customers |
| document_type | VARCHAR(50) | No | Passport, License | Passport | |
| verification_status| VARCHAR(20) | No | Verified or Pending | Verified | Pending, Verified, Rejected |
| expiry_date | DATE | Yes | Expiration of doc | 2030-05-12 | |

## 19. Watchlists
- **Business Purpose**: Risk and AML compliance.
- **Description**: Lists of high-risk individuals (PEPs).
- **Expected Row Count**: 500,000
- **Primary Key**: `watchlist_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| watchlist_id | VARCHAR(50) | No | Unique ID | WL-881 | UNIQUE |
| entity_name | VARCHAR(255) | No | Name of person/org | John Corrupt | |
| list_type | VARCHAR(50) | No | PEP, Sanction, etc. | PEP | |
| country | VARCHAR(50) | Yes | Associated country | CountryX | |

## 20. Sanctions
- **Business Purpose**: Legal compliance.
- **Description**: Specific economic sanctions data.
- **Expected Row Count**: 50,000
- **Primary Key**: `sanction_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| sanction_id | VARCHAR(50) | No | Unique ID | SANC-12 | UNIQUE |
| target_name | VARCHAR(255) | No | Sanctioned entity | BadCorp Ltd | |
| issuing_body | VARCHAR(100) | No | OFAC, UN, EU | OFAC | |
| start_date | DATE | No | Sanction start date | 2021-01-01 | |

## 21. Suspicious_Activities
- **Business Purpose**: AML reporting (SARs).
- **Description**: Filed reports for suspicious activities.
- **Expected Row Count**: 100,000
- **Primary Key**: `sar_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| sar_id | VARCHAR(50) | No | Unique SAR ID | SAR-009 | UNIQUE |
| customer_id | VARCHAR(50) | No | Subject of SAR | CUST-10001 | FK to Customers |
| activity_type | VARCHAR(100) | No | Structuring, etc. | Structuring | |
| report_date | DATE | No | Date SAR filed | 2023-11-15 | |

## 22. Interactions
- **Business Purpose**: Customer intelligence.
- **Description**: Logs of customer touchpoints (Call, Branch, App).
- **Expected Row Count**: 2B+
- **Primary Key**: `interaction_id`
- **Foreign Keys**: `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| interaction_id | VARCHAR(50) | No | Unique interaction ID| INT-443 | UNIQUE |
| customer_id | VARCHAR(50) | No | Customer involved | CUST-10001 | FK to Customers |
| channel | VARCHAR(50) | No | Mobile, Web, Call | Mobile App | |
| interaction_type| VARCHAR(100) | No | Login, Transfer View | Login | |
| timestamp | TIMESTAMP | No | Time of interaction | 2023-10-12 10:00:00| |

## 23. Campaigns
- **Business Purpose**: Marketing operations.
- **Description**: Details of marketing campaigns.
- **Expected Row Count**: 5,000
- **Primary Key**: `campaign_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| campaign_id | VARCHAR(50) | No | Unique campaign ID | CAMP-21 | UNIQUE |
| campaign_name | VARCHAR(255) | No | Name of campaign | Summer Auto Loan | |
| channel | VARCHAR(50) | No | Email, SMS, Push | Email | |
| start_date | DATE | No | Launch date | 2023-06-01 | |
| end_date | DATE | Yes | End date | 2023-08-31 | > start_date |

## 24. Campaign_Responses
- **Business Purpose**: Measuring marketing ROI.
- **Description**: How customers reacted to campaigns.
- **Expected Row Count**: 50M
- **Primary Key**: `response_id`
- **Foreign Keys**: `campaign_id`, `customer_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| response_id | VARCHAR(50) | No | Unique response ID | RESP-112 | UNIQUE |
| campaign_id | VARCHAR(50) | No | Campaign sent | CAMP-21 | FK to Campaigns |
| customer_id | VARCHAR(50) | No | Customer targeted | CUST-10001 | FK to Customers |
| response_type | VARCHAR(50) | No | Opened, Clicked, Converted | Clicked | |
| timestamp | TIMESTAMP | No | Time of response | 2023-06-05 09:00:00| |

## 25. Web_Analytics
- **Business Purpose**: Digital channel intelligence.
- **Description**: Page views and session data on bank's website.
- **Expected Row Count**: 5B+
- **Primary Key**: `event_id`
- **Foreign Keys**: `customer_id` (optional)

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| event_id | VARCHAR(50) | No | Unique event ID | WEB-882 | UNIQUE |
| session_id | VARCHAR(100) | No | Browser session ID | SESS-UUID | |
| customer_id | VARCHAR(50) | Yes | Logged in user | CUST-10001 | FK to Customers |
| page_url | VARCHAR(500) | No | URL visited | /mortgage-rates | |
| event_time | TIMESTAMP | No | Time of event | 2023-11-20 08:30:00| |

## 26. Support_Tickets
- **Business Purpose**: Customer service.
- **Description**: Issues raised by customers.
- **Expected Row Count**: 10M
- **Primary Key**: `ticket_id`
- **Foreign Keys**: `customer_id`, `employee_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| ticket_id | VARCHAR(50) | No | Unique ticket ID | TKT-991 | UNIQUE |
| customer_id | VARCHAR(50) | No | Customer raising issue | CUST-10001 | FK to Customers |
| assigned_to | VARCHAR(50) | Yes | Agent handling it | EMP-001 | FK to Employees |
| issue_category | VARCHAR(100) | No | Type of problem | Dispute | |
| status | VARCHAR(20) | No | Ticket status | Resolved | Open, In Progress, Resolved |

## 27. Feedback
- **Business Purpose**: Customer satisfaction.
- **Description**: NPS and surveys.
- **Expected Row Count**: 5M
- **Primary Key**: `feedback_id`
- **Foreign Keys**: `customer_id`, `interaction_id`

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| feedback_id | VARCHAR(50) | No | Unique feedback ID | FB-011 | UNIQUE |
| customer_id | VARCHAR(50) | No | Respondent | CUST-10001 | FK to Customers |
| interaction_id | VARCHAR(50) | Yes | Related interaction | INT-443 | FK to Interactions |
| score | INT | No | Rating | 9 | 1 to 10 |
| comments | TEXT | Yes | Text feedback | Great app! | |

## 28. Currency_Rates
- **Business Purpose**: Reference data for forex.
- **Description**: Daily exchange rates.
- **Expected Row Count**: 500,000
- **Primary Key**: `rate_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| rate_id | VARCHAR(50) | No | Unique rate ID | FX-8812 | UNIQUE |
| base_currency | VARCHAR(3) | No | Base ISO code | USD | |
| target_currency| VARCHAR(3) | No | Target ISO code | EUR | |
| exchange_rate | DECIMAL(15,6)| No | Conversion rate | 0.920000 | > 0 |
| rate_date | DATE | No | Date of rate | 2023-11-20 | |

## 29. Geographies
- **Business Purpose**: Reference data for locations.
- **Description**: Regions, countries, and states for grouping.
- **Expected Row Count**: 5,000
- **Primary Key**: `geo_id`
- **Foreign Keys**: None

| Column Name | Data Type | Nullable | Definition | Example Values | Constraints |
|---|---|---|---|---|---|
| geo_id | VARCHAR(50) | No | Unique Geo ID | GEO-US-NY | UNIQUE |
| region | VARCHAR(100) | No | Continent / Macro region| North America | |
| country | VARCHAR(100) | No | Country name | United States | |
| state_province | VARCHAR(100) | Yes | State or Province | New York | |
