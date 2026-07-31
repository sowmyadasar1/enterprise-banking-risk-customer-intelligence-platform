"""Data preparation for time series forecasting."""
import os
import sqlite3
import pandas as pd
from . import config


def extract_daily_series():
    """Extract daily aggregated metrics from the Data Warehouse."""
    print("\n" + "="*70)
    print("  STEP 1: DATA PREPARATION (TIME SERIES AGGREGATION)")
    print("="*70)

    if not os.path.exists(config.DB_PATH):
        raise FileNotFoundError(f"Database not found at {config.DB_PATH}")

    conn = sqlite3.connect(config.DB_PATH)

    # 1. Transactions & Revenue
    query_txn = """
        SELECT 
            transaction_date AS date,
            COUNT(transaction_id) AS transaction_volume,
            SUM(amount) AS revenue
        FROM fact_transactions
        GROUP BY transaction_date
        ORDER BY transaction_date
    """
    df_txn = pd.read_sql(query_txn, conn, parse_dates=['date'])
    df_txn['date'] = pd.to_datetime(df_txn['date'], utc=True).dt.tz_localize(None)
    df_txn = df_txn.set_index('date')

    # 2. Loan Demand
    query_loan = """
        SELECT 
            start_date AS date,
            SUM(loan_amount) AS loan_demand
        FROM fact_loans
        GROUP BY start_date
        ORDER BY start_date
    """
    df_loan = pd.read_sql(query_loan, conn, parse_dates=['date'])
    df_loan['date'] = pd.to_datetime(df_loan['date'], utc=True).dt.tz_localize(None)
    df_loan = df_loan.set_index('date')

    # 3. New Customers
    query_cust = """
        SELECT 
            join_date AS date,
            COUNT(customer_id) AS new_customers
        FROM dim_customer
        GROUP BY join_date
        ORDER BY join_date
    """
    df_cust = pd.read_sql(query_cust, conn, parse_dates=['date'])
    df_cust['date'] = pd.to_datetime(df_cust['date'], utc=True).dt.tz_localize(None)
    df_cust = df_cust.set_index('date')

    conn.close()

    # Combine all series
    df = df_txn.join(df_loan, how='outer').join(df_cust, how='outer')
    
    # Resample to ensure continuous daily frequency
    df = df.resample('D').sum().fillna(0)

    print(f"  Loaded Time Series:")
    print(f"    Date Range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    print(f"    Total Days: {len(df)}")
    
    # Validate
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"  [WARN] Found {missing} missing values. Forward filling.")
        df = df.ffill()

    # Outlier Capping (3 Std Dev)
    for col in config.TARGETS:
        mean = df[col].mean()
        std = df[col].std()
        upper_limit = mean + 3 * std
        outliers = (df[col] > upper_limit).sum()
        if outliers > 0:
            print(f"  [WARN] Capped {outliers} outliers in {col}")
            df[col] = df[col].clip(upper=upper_limit)

    # Save prepared dataset
    output_path = os.path.join(config.DATA_DIR, 'daily_time_series.csv')
    df.to_csv(output_path)
    print(f"  Saved aggregated series to {output_path}")

    return df
