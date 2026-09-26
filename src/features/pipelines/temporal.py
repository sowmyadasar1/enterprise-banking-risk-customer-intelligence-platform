"""
Temporal Features Pipeline
Generates temporal and seasonality features from fact_transactions.
"""

import pandas as pd
import numpy as np


def build_temporal_features(conn):
    """Build temporal features per customer (days since last txn, seasonality)."""
    print("[Temporal] Loading transaction dates...")

    df_txn = pd.read_sql(
        """
        SELECT a.customer_id, t.transaction_date, t.transaction_day_of_week,
               t.transaction_month, t.transaction_quarter
        FROM fact_transactions t
        JOIN dim_account a ON t.account_id = a.account_id
    """,
        conn,
    )

    df_txn["transaction_date"] = pd.to_datetime(
        df_txn["transaction_date"], errors="coerce", utc=True
    ).dt.tz_localize(None)
    for col in ["transaction_day_of_week", "transaction_month", "transaction_quarter"]:
        df_txn[col] = pd.to_numeric(df_txn[col], errors="coerce").fillna(0).astype(int)

    today = pd.Timestamp.now().tz_localize(None)

    # --- Days since last transaction ---
    last_txn = df_txn.groupby("customer_id")["transaction_date"].max().reset_index()
    last_txn["days_since_last_transaction"] = (
        (today - last_txn["transaction_date"]).dt.days.fillna(0).astype(int)
    )
    last_txn = last_txn[["customer_id", "days_since_last_transaction"]]

    # --- Preferred day of week ---
    dow_mode = (
        df_txn.groupby("customer_id")["transaction_day_of_week"]
        .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 0)
        .reset_index(name="preferred_day_of_week")
    )

    # --- Preferred month ---
    month_mode = (
        df_txn.groupby("customer_id")["transaction_month"]
        .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 0)
        .reset_index(name="preferred_month")
    )

    # --- Preferred quarter ---
    qtr_mode = (
        df_txn.groupby("customer_id")["transaction_quarter"]
        .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 0)
        .reset_index(name="preferred_quarter")
    )

    # --- Seasonality: summer (Jun-Aug) and winter (Dec-Feb) transaction ratios ---
    df_txn["is_summer"] = df_txn["transaction_month"].isin([6, 7, 8]).astype(int)
    df_txn["is_winter"] = df_txn["transaction_month"].isin([12, 1, 2]).astype(int)
    season_agg = (
        df_txn.groupby("customer_id")
        .agg(
            summer_txn_ratio=("is_summer", "mean"),
            winter_txn_ratio=("is_winter", "mean"),
        )
        .reset_index()
        .round(4)
    )

    # --- Days since last loan payment ---
    try:
        df_pay = pd.read_sql(
            """
            SELECT l.customer_id, p.payment_date
            FROM fact_loan_payments p
            JOIN dim_loan l ON p.loan_id = l.loan_id
        """,
            conn,
        )
        df_pay["payment_date"] = pd.to_datetime(
            df_pay["payment_date"], errors="coerce", utc=True
        ).dt.tz_localize(None)
        last_pay = df_pay.groupby("customer_id")["payment_date"].max().reset_index()
        last_pay["days_since_last_loan_payment"] = (
            (today - last_pay["payment_date"]).dt.days.fillna(0).astype(int)
        )
        last_pay = last_pay[["customer_id", "days_since_last_loan_payment"]]
    except Exception:
        last_pay = pd.DataFrame(columns=["customer_id", "days_since_last_loan_payment"])

    # --- Merge all ---
    df = last_txn.copy()
    for sub_df in [dow_mode, month_mode, qtr_mode, season_agg, last_pay]:
        df = df.merge(sub_df, on="customer_id", how="left")

    df = df.fillna(0)
    print(f"[Temporal] Generated {len(df)} rows, {len(df.columns)} features.")
    return df
