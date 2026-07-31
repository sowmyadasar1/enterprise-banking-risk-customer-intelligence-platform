# Data Lineage & ETL Architecture

This document describes the data flow and transformation logic across the Medallion Architecture (Bronze, Silver, Gold) for the Enterprise Banking Risk & Customer Intelligence Platform.

## High-Level Architecture

Data moves through several stages to ensure quality, reliability, and business value:
`Raw Source -> Ingestion -> Bronze (Raw) -> Silver (Clean/Filtered) -> Gold (Aggregated/Business Level) -> Data Warehouse / BI`

---

## 1. Raw Sources & Ingestion
- **Mainframe Core Banking System**: Emits nightly batch files (CSV) and real-time Kafka events for `Customers`, `Accounts`, `Transactions`.
- **CRM System (Salesforce)**: API ingestion for `Interactions`, `Support_Tickets`, `Campaigns`.
- **Web/Mobile Platforms**: Snowplow/Google Analytics streams dropping JSON events into S3 for `Web_Analytics`.
- **External Providers**: APIs fetching `Credit_Scores`, `Market_Data`, `Watchlists`, `Sanctions`, `Currency_Rates`.

## 2. Bronze Layer (Raw & Immutable)
- **Purpose**: Exact replica of source data. Append-only. Captures data "as-is" for audit and replayability.
- **Format**: Delta Lake / Parquet.
- **Example**: Raw JSON transaction payloads containing nested structures and messy timestamp strings.

## 3. Silver Layer (Cleaned, Filtered, Conformed)
- **Purpose**: Data quality checks, deduplication, schema enforcement, data typing, and PII masking.
- **Transformations**:
  - String to Date/Timestamp parsing.
  - Standardizing `currency` codes to uppercase ISO 4217.
  - Hashing PII (e.g., `email`, `phone_number`).
  - Handling NULLs (e.g., replacing NULL `merchant_category` with 'Unknown').
- **Example**: 
  - *Input (Bronze)*: `{"txn_id": "123", "amt": "150.00", "dt": "12-Oct-2023", "type": "w"}`
  - *Output (Silver)*: `transaction_id=123, amount=150.00, transaction_date=2023-10-12 00:00:00, transaction_type='Withdrawal'`

## 4. Gold Layer (Business-Level Aggregations & Facts)
- **Purpose**: Optimized for read-heavy BI, ML models, and reporting. Star schemas (Facts & Dimensions).
- **Transformations**:
  - Joining dimension tables to fact tables.
  - Calculating rolling averages, customer lifetime value (CLV), and risk scores.
  - Aggregating to Daily/Monthly grains.
- **Example Gold Tables**:
  - `Fact_Daily_Customer_Balances`: Aggregated daily snapshot of all accounts per customer.
  - `Fact_Fraud_Risk`: Joined view of `Transactions`, `Customers`, and ML inference outputs.
  - `Dim_Customer_360`: A wide table summarizing a customer's total loans, total deposits, active campaigns, and recent support tickets.

## Concrete Example: Transformation of Transactions

### Flow: From ATM to Dashboard

1. **Raw Source**: An ATM dispenses $200. A legacy system generates a fixed-width text record.
2. **Ingestion**: Kafka Connect reads the record and drops it into an S3 bucket as raw text.
3. **Bronze (`bronze.raw_transactions`)**: Spark structured streaming reads the text file, wraps it in a Delta table with a load timestamp and metadata column (`source_file`).
4. **Validation/Cleaning -> Silver (`silver.transactions`)**:
   - Parse the fixed-width text into columns: `account_id`, `amount`, `date`.
   - Apply Data Quality Rule: `amount` > 0.
   - Standardize `description` column.
   - Result is strongly-typed, clean rows ready for analysis.
5. **Transformation -> Gold (`gold.fact_transactions`)**:
   - Join `silver.transactions` with `silver.currency_rates` to convert all foreign amounts into `USD_Amount`.
   - Join with `silver.accounts` and `silver.branches` to add geographical dimension keys.
6. **Data Warehouse (`Customer_Spend_Cube`)**:
   - The Gold Fact table is aggregated by month, region, and merchant category to power the Executive Retail Banking Dashboard.
