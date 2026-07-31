# Power BI Refresh & Performance Strategy

This document outlines the optimization parameters designed to keep the Enterprise Banking BI model performant and robust.

## 1. Data Refresh Architecture

Given the large volume of transactions in `fact_transactions`, a full refresh on every schedule is highly inefficient. 

**Solution: Incremental Refresh**
- **Parameters**: `RangeStart` (DateTime) and `RangeEnd` (DateTime) must be configured in Power Query.
- **Archive Policy**: Store the last **5 Years** of data in the Power BI Service.
- **Refresh Policy**: Only refresh the last **30 Days** of data on each schedule execution.
- **Detect Data Changes**: Enable "Detect Data Changes" based on the `transaction_timestamp` column to only update rows that have been modified (useful for retroactive fraud flagging).

## 2. Gateway Configuration
- Ensure an On-Premises Data Gateway (Enterprise Mode) is installed on the server hosting `enterprise_dw.db`.
- Scheduled refresh should be set to **8 times a day** (every 3 hours) during business hours for Pro licenses, or up to **48 times a day** for Premium capacity.

## 3. Performance Optimizations

To maintain a fast user experience (sub-second visual rendering):
1. **Remove Unused Columns**: Only columns required for DAX measures or visualizations have been imported. High-cardinality metadata (like JSON blobs or free-text descriptions) should be dropped in Power Query.
2. **Auto Date/Time**: Disable "Auto Date/Time" in Power BI options to prevent the creation of hidden date tables. Rely strictly on `dim_calendar`.
3. **Integer Surrogate Keys**: All joins between facts and dimensions must use Integer or fixed-length string IDs. 
4. **Bi-Directional Filtering**: Avoided completely. All relationships are 1-to-Many, Single Direction.
5. **DAX Optimization**: Measures like `DIVIDE()` are used natively to handle blank/zero division without complex `IF()` error handling, ensuring optimal VertiPaq performance.
