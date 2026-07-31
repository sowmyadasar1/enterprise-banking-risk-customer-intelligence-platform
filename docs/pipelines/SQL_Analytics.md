# SQL Analytics Layer

The SQL Analytics Layer (Phase 5) provides pre-computed business intelligence aggregations optimized for Power BI dashboards and ad-hoc analyst queries.

## Star Schema Design

```mermaid
erDiagram
    fact_transactions ||--o{ dim_customers : customer_id
    fact_transactions ||--o{ dim_accounts : account_id
    fact_transactions ||--o{ dim_products : product_id
    fact_transactions ||--o{ dim_branches : branch_id
    fact_transactions ||--o{ dim_calendar : date_key
    fact_transactions ||--o{ dim_merchants : merchant_id
    fact_loan_payments ||--o{ dim_customers : customer_id
    fact_loan_payments ||--o{ dim_calendar : date_key

    fact_transactions {
        int transaction_id PK
        float amount
        string transaction_type
        date transaction_date
        int customer_id FK
        int account_id FK
    }

    dim_customers {
        int customer_id PK
        string name
        int age
        string segment
        float credit_score
    }

    dim_accounts {
        int account_id PK
        string account_type
        float balance
        date open_date
    }

    dim_calendar {
        int date_key PK
        date full_date
        int year
        int quarter
        int month
        string day_name
    }
```

## Key SQL Aggregations

### Revenue Analytics
- Total revenue by branch, product, and time period.
- Month-over-month growth rates.
- Year-to-date cumulative revenue.

### Risk Analytics
- Average credit score distribution by segment.
- Loan default rates by product and branch.
- Fraud incident counts and total loss amounts.

### Customer Analytics
- Customer acquisition trends over time.
- Average customer lifetime value by segment.
- Product penetration rates.

## Design Rationale
The **Kimball Star Schema** was chosen over a Snowflake Schema because:
1. **Query Performance**: Fewer JOINs required for BI queries.
2. **Power BI Compatibility**: Star schemas map directly to Power BI's data model.
3. **Analyst Friendliness**: Business users can self-serve without needing to understand complex normalization.
