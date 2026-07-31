# Power BI Data Model Architecture

This document defines the Star Schema layout imported into Power BI from the `enterprise_dw.db` Data Warehouse.

## Fact Tables

1. **fact_transactions**: Central fact table storing all financial movements.
   - Granularity: One row per transaction.
2. **fact_loans**: Loan originations.
   - Granularity: One row per loan.
3. **fact_fraud**: Fraud cases.
   - Granularity: One row per confirmed/suspected fraud case.
4. **fact_marketing_responses**: Campaign interactions.
   - Granularity: One row per customer interaction.

## Dimension Tables

1. **dim_customer**: Core demographic data, risk ratings, and ML segmentation outputs.
2. **dim_account**: Account mapping to branches and products.
3. **dim_branch**: Geographical and structural bank hierarchies.
4. **dim_calendar**: Generated Date table (essential for Time Intelligence DAX).

## Relationships & Filtering Directions

Strict enforcement of standard Star Schema relationships to maximize the VertiPaq engine compression and query speed.

| From Table | From Column | To Table | To Column | Cardinality | Cross-Filter Direction |
|------------|-------------|----------|-----------|-------------|------------------------|
| dim_calendar | Date | fact_transactions | transaction_date | 1 : * | Single |
| dim_customer | customer_id | fact_transactions | customer_id | 1 : * | Single |
| dim_account | account_id | fact_transactions | account_id | 1 : * | Single |
| dim_customer | customer_id | fact_loans | customer_id | 1 : * | Single |
| dim_branch | branch_id | dim_account | branch_id | 1 : * | Single |
| dim_customer | customer_id | fact_fraud | customer_id | 1 : * | Single |
| dim_calendar | Date | fact_marketing_responses | response_date | 1 : * | Single |

*Note: For scenarios requiring branch managers to see total loans, `dim_branch` filters `dim_account`, which filters `fact_loans` via `account_id`.*

## Refresh Strategy
- **Mode**: Import Mode (for max DAX speed and full feature support).
- **Incremental Refresh**: 
  - `RangeStart` and `RangeEnd` parameters defined.
  - Policy: Store past 5 years of `fact_transactions`, refresh the last 30 days daily.
