# Data Dictionary

Comprehensive schema definitions for all core tables in the Enterprise Data Warehouse.

---

## Core Tables

### `customers`
| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | INTEGER (PK) | Unique customer identifier |
| `first_name` | TEXT | Customer first name |
| `last_name` | TEXT | Customer last name |
| `email` | TEXT | Email address |
| `date_of_birth` | DATE | Birth date |
| `gender` | TEXT | Male / Female / Other |
| `join_date` | DATE | Account opening date |
| `credit_score` | INTEGER | Bureau credit score (300-900) |

### `accounts`
| Column | Type | Description |
|--------|------|-------------|
| `account_id` | INTEGER (PK) | Unique account identifier |
| `customer_id` | INTEGER (FK) | Links to `customers` |
| `account_type` | TEXT | Savings / Checking / Credit |
| `balance` | REAL | Current balance |
| `open_date` | DATE | Account opening date |
| `status` | TEXT | Active / Closed / Frozen |

### `transactions`
| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | INTEGER (PK) | Unique transaction identifier |
| `account_id` | INTEGER (FK) | Links to `accounts` |
| `transaction_type` | TEXT | Deposit / Withdrawal / Transfer / Payment |
| `amount` | REAL | Transaction amount (USD) |
| `transaction_date` | DATETIME | Timestamp of transaction |
| `merchant_id` | INTEGER (FK) | Links to `merchants` |

### `loans`
| Column | Type | Description |
|--------|------|-------------|
| `loan_id` | INTEGER (PK) | Unique loan identifier |
| `customer_id` | INTEGER (FK) | Links to `customers` |
| `loan_amount` | REAL | Principal amount |
| `interest_rate` | REAL | Annual interest rate (%) |
| `loan_term_months` | INTEGER | Repayment period |
| `status` | TEXT | Active / Paid Off / Defaulted |

### `loan_payments`
| Column | Type | Description |
|--------|------|-------------|
| `payment_id` | INTEGER (PK) | Unique payment identifier |
| `loan_id` | INTEGER (FK) | Links to `loans` |
| `payment_date` | DATE | Date of payment |
| `amount` | REAL | Payment amount |
| `payment_status` | TEXT | On-Time / Late / Missed |

---

## Reference Tables

### `regions`
`region_id` (PK), `region_name`, `country`

### `branches`
`branch_id` (PK), `branch_name`, `region_id` (FK), `city`, `state`

### `products`
`product_id` (PK), `product_name`, `product_category`, `interest_rate`

### `transaction_types`
`type_id` (PK), `type_name`, `description`

### `merchants`
`merchant_id` (PK), `merchant_name`, `category`, `location`

### `calendar`
`date_key` (PK), `full_date`, `year`, `quarter`, `month`, `day_of_week`, `is_weekend`, `is_holiday`

---

## Risk & ML Tables

### `customer_risk_scores`
`customer_id` (FK), `risk_score`, `risk_category`, `assessment_date`

### `fraud_cases`
`case_id` (PK), `transaction_id` (FK), `fraud_type`, `fraud_amount`, `detection_date`, `status`

### `fraud_investigations`
`investigation_id` (PK), `case_id` (FK), `investigator`, `outcome`, `resolution_date`

### `loan_default_labels`
`loan_id` (FK), `is_default` (BOOLEAN), `default_date`
