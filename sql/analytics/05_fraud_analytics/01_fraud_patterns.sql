/*
=============================================================================
Business Question: Are there suspicious transaction patterns indicating potential fraud?
Business Interpretation: Detects rapid succession of transactions which is a common fraud indicator (e.g. velocity attacks).
Decision Supported: Tuning real-time fraud detection rules and blocking suspicious accounts.
Recommended Business Action: Temporarily freeze accounts with high-velocity transactions and flag for review.
SQL Techniques Used: Window functions (LAG), Time difference calculations, CTEs.
=============================================================================
*/

-- Detect Suspicious Transaction Velocity
WITH TransactionVelocity AS (
    SELECT
        account_id,
        transaction_id,
        amount,
        transaction_timestamp,
        LAG(transaction_timestamp) OVER (PARTITION BY account_id ORDER BY transaction_timestamp) AS prev_transaction_time
    FROM fact_transactions
)
SELECT
    account_id,
    transaction_id,
    amount,
    transaction_timestamp,
    prev_transaction_time,
    (strftime('%s', transaction_timestamp) - strftime('%s', prev_transaction_time)) / 60 AS minutes_since_last_txn
FROM TransactionVelocity
WHERE (strftime('%s', transaction_timestamp) - strftime('%s', prev_transaction_time)) / 60 < 5
  AND amount > 1000
ORDER BY minutes_since_last_txn ASC;
