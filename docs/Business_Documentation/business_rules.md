# Business Rules & Data Quality Rules

This document contains over 50 comprehensive business rules and data quality constraints governing the data within the Enterprise Banking Risk & Customer Intelligence Platform.

## Data Quality & Integrity Rules (1-15)
1.  **Unique Primary Keys**: Every table must have a unique identifier (e.g., `customer_id`, `account_id`) with no duplicates.
2.  **Foreign Key Integrity**: A record cannot reference a non-existent parent entity. (e.g., An `account_id` in `Transactions` must exist in `Accounts`).
3.  **No Orphan Records**: A `Transaction` cannot exist without a valid `account_id`.
4.  **Email Format Validation**: `email` fields must conform to standard regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`.
5.  **Phone Number Standardization**: `phone_number` must include country code and contain 10-15 digits.
6.  **No Impossible Ages**: Customers must be at least 18 years old to open a primary account (i.e., `date_of_birth` implies age >= 18 and < 120).
7.  **Future Dates Check**: `date_of_birth`, `transaction_date`, and `account_opened_date` cannot be in the future.
8.  **Status Enumerations**: `account_status` must strictly be one of: 'Active', 'Closed', 'Frozen'.
9.  **Currency Codes**: Must follow standard 3-letter ISO 4217 format (e.g., 'USD', 'EUR', 'GBP').
10. **Non-Negative Balances**: Standard checking and savings accounts cannot have negative balances unless overdraft is explicitly enabled.
11. **Transaction Amount Validity**: `amount` in `Transactions` must always be strictly > 0. (Direction is indicated by `transaction_type`).
12. **Valid Credit Scores**: `credit_score` must fall within the realistic range of 300 to 850.
13. **Timestamp Sequencing**: In `Interactions`, a 'Logout' event timestamp must be strictly greater than its corresponding 'Login' event.
14. **Date Consistency**: `end_date` for a `Campaign` must be greater than or equal to the `start_date`.
15. **Not Null Constraints**: Critical financial fields like `balance`, `amount`, and `interest_rate` cannot be NULL.

## Core Banking & Customer Behavior Rules (16-30)
16. **Wealth Correlation**: Customers in higher `income_bracket` segments generally maintain higher average account balances.
17. **Account Limits**: A single customer typically holds between 1 and 5 active accounts.
18. **Dormant Accounts**: Accounts with no `Transactions` for > 365 days should have their status flagged as 'Dormant'.
19. **Overdraft Rules**: A `Withdrawal` transaction that exceeds `balance` is rejected unless the linked account has an overdraft limit.
20. **Age & Loans**: Customers under 21 or over 75 have a lower probability of being approved for a 30-year Mortgage.
21. **High Net Worth Individuals (HNWI)**: Customers with total balances across all accounts > $1M are flagged for premium support routing.
22. **Branch Affinity**: Over 80% of ATM/Branch transactions occur at a branch within the same `geo_id` as the customer's residence.
23. **Employee Branch Assignment**: An `Employee` can only be assigned to one primary `branch_id` at a time.
24. **Card Issuance**: A `Credit Card` can only be issued if the customer's `credit_score` > 600.
25. **Card Limits**: Credit card `credit_limit` strongly correlates with `income_bracket` and `credit_score`.
26. **Debit Card Linking**: A `Debit Card` must be linked to at least one active Checking account.
27. **Card Expiry**: A `Card` automatically changes status to 'Expired' on the first day of the month following its expiry date.
28. **Salary Crediting**: Regular large deposits on the last day of the month are flagged as 'Salary' via `description` categorization.
29. **Weekend Spending**: Transaction volumes for `merchant_category` 'Dining' and 'Entertainment' are 40% higher on weekends.
30. **Digital Adoption**: Customers aged 18-35 have 90% of their `Interactions` via 'Mobile App', whereas customers 65+ lean towards 'Branch' or 'Call'.

## Risk, Fraud, and Compliance Rules (31-42)
31. **Velocity Rules**: > 3 card transactions in under 5 minutes from different geographic locations triggers a `Fraud_Alert`.
32. **Unusual Hours**: ATM withdrawals between 1:00 AM and 5:00 AM have a 3x higher baseline probability of generating a `Fraud_Alert`.
33. **Structuring (Smurfing)**: Multiple deposits just under the $10,000 reporting threshold within a 7-day period triggers a `Suspicious_Activity` (SAR).
34. **KYC Verification**: Accounts cannot process international wire transfers if `KYC_Documents` status is 'Pending' or 'Rejected'.
35. **Sanction Blocking**: Any transaction involving a `target_name` found on the `Sanctions` list is immediately frozen.
36. **PEP Monitoring**: Customers matched on `Watchlists` as Politically Exposed Persons (PEPs) require enhanced due diligence and manual approval for large loans.
37. **First-Party Fraud**: A loan default (`Delinquencies` > 90 days) within the first 3 months of loan origination is highly scrutinized for first-party fraud.
38. **Card Testing**: Numerous small transactions ($0.50 - $2.00) in rapid succession on an e-commerce site indicate card testing and trigger a block.
39. **New Device Login**: A `Web_Analytics` event showing a login from an unrecognized device or IP triggers multi-factor authentication.
40. **AML Alerts**: A sudden 500% spike in monthly transaction volume for an account historically maintaining low balances triggers an AML review.
41. **Delinquency Escalation**: A loan moves to 'Defaulted' status when `days_past_due` exceeds 120 days.
42. **Collateral Valuation**: A Mortgage cannot be approved if the `principal_amount` exceeds 95% of the `estimated_value` of the `Collateral` (LTV > 95%).

## Marketing & Customer Intelligence Rules (43-50)
43. **Campaign Fatigue**: A customer should not receive more than 3 marketing `Campaigns` via 'Email' in a single month.
44. **Targeting Relevance**: Auto loan campaigns are heavily targeted at customers whose `Web_Analytics` show page views on auto loan rate calculators.
45. **Conversion Tracking**: A `Campaign_Response` is flagged as 'Converted' if a related product (e.g., new Loan) is opened within 30 days of a 'Clicked' event.
46. **NPS Sentiment**: A `Feedback` score of 9-10 (Promoter) generally correlates with high account balances and long tenure.
47. **Churn Prediction**: Customers who change their direct deposit away from the bank have a 70% probability of account closure within 90 days.
48. **Support Ticket SLAs**: 'Dispute' category `Support_Tickets` must be responded to within 24 hours.
49. **Cross-Sell Potential**: Customers holding a Checking account but no Savings account or Credit Card are the primary cohort for cross-sell campaigns.
50. **Investment Propensity**: Customers who maintain > $50,000 in a Checking account for > 6 months are highly likely to respond positively to Wealth Management `Portfolios` outreach.
