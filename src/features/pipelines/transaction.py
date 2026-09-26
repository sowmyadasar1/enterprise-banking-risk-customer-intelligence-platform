"""
Transaction Features Pipeline
Generates transaction-level features aggregated per customer from fact_transactions.
"""

import pandas as pd
import numpy as np


def build_transaction_features(conn):
    """Build comprehensive transaction features per customer."""
    print("[Transaction] Loading transactions...")

    # Load transactions with account mapping
    df_txn = pd.read_sql(
        """
        SELECT t.transaction_id, t.account_id, a.customer_id,
               t.amount, t.amount_abs, t.transaction_date, t.transaction_timestamp,
               t.transaction_hour, t.transaction_day_of_week, t.transaction_month,
               t.transaction_quarter, t.is_weekend, t.is_night_transaction,
               t.is_large_transaction, t.merchant_id, t.channel, t.status
        FROM fact_transactions t
        JOIN dim_account a ON t.account_id = a.account_id
    """,
        conn,
    )

    # Coerce numerics
    for col in [
        "amount",
        "amount_abs",
        "transaction_hour",
        "transaction_day_of_week",
        "transaction_month",
        "transaction_quarter",
        "is_weekend",
        "is_night_transaction",
        "is_large_transaction",
    ]:
        df_txn[col] = pd.to_numeric(df_txn[col], errors="coerce").fillna(0)

    df_txn["transaction_date"] = pd.to_datetime(
        df_txn["transaction_date"], errors="coerce", utc=True
    ).dt.tz_localize(None)

    # --- Basic amount aggregations ---
    amt_agg = (
        df_txn.groupby("customer_id")
        .agg(
            avg_transaction_amount=("amount_abs", "mean"),
            median_transaction_amount=("amount_abs", "median"),
            max_transaction_amount=("amount_abs", "max"),
            min_transaction_amount=("amount_abs", "min"),
            std_transaction_amount=("amount_abs", "std"),
            total_transaction_count=("transaction_id", "count"),
            total_spend=("amount_abs", "sum"),
        )
        .reset_index()
    )
    amt_agg["std_transaction_amount"] = amt_agg["std_transaction_amount"].fillna(0)

    # --- Temporal counts ---
    # Daily average
    daily = (
        df_txn.groupby(["customer_id", "transaction_date"])
        .size()
        .reset_index(name="daily_count")
    )
    daily_avg = (
        daily.groupby("customer_id")["daily_count"]
        .mean()
        .reset_index(name="avg_daily_txn_count")
    )

    # Weekly average (use iso week)
    df_txn["iso_week"] = df_txn["transaction_date"].dt.isocalendar().week.astype(int)
    weekly = (
        df_txn.groupby(["customer_id", "iso_week"])
        .size()
        .reset_index(name="weekly_count")
    )
    weekly_avg = (
        weekly.groupby("customer_id")["weekly_count"]
        .mean()
        .reset_index(name="avg_weekly_txn_count")
    )

    # Monthly average
    monthly = (
        df_txn.groupby(["customer_id", "transaction_month"])
        .size()
        .reset_index(name="monthly_count")
    )
    monthly_avg = (
        monthly.groupby("customer_id")["monthly_count"]
        .mean()
        .reset_index(name="avg_monthly_txn_count")
    )

    # --- Rolling spend proxies ---
    # Sort by date, take last 7 and last 30 days worth
    max_date = df_txn["transaction_date"].max()
    last_7 = df_txn[df_txn["transaction_date"] >= (max_date - pd.Timedelta(days=7))]
    last_30 = df_txn[df_txn["transaction_date"] >= (max_date - pd.Timedelta(days=30))]

    roll7 = (
        last_7.groupby("customer_id")["amount_abs"]
        .sum()
        .reset_index(name="rolling_7d_spend")
    )
    roll30 = (
        last_30.groupby("customer_id")["amount_abs"]
        .sum()
        .reset_index(name="rolling_30d_spend")
    )

    # --- Transaction velocity ---
    date_range = (
        df_txn.groupby("customer_id")["transaction_date"]
        .agg(["min", "max"])
        .reset_index()
    )
    date_range["active_days"] = (date_range["max"] - date_range["min"]).dt.days.replace(
        0, 1
    )
    txn_count = df_txn.groupby("customer_id").size().reset_index(name="n_txns")
    velocity = date_range.merge(txn_count, on="customer_id")
    velocity["transaction_velocity"] = (
        velocity["n_txns"] / velocity["active_days"]
    ).round(4)
    velocity = velocity[["customer_id", "transaction_velocity"]]

    # --- Behavioral ratios ---
    ratio_agg = (
        df_txn.groupby("customer_id")
        .agg(
            weekend_txns=("is_weekend", "sum"),
            night_txns=("is_night_transaction", "sum"),
            large_txns=("is_large_transaction", "sum"),
            total_for_ratio=("transaction_id", "count"),
            unique_merchants=("merchant_id", "nunique"),
        )
        .reset_index()
    )
    ratio_agg["weekend_spending_ratio"] = (
        ratio_agg["weekend_txns"] / ratio_agg["total_for_ratio"].replace(0, 1)
    ).round(4)
    ratio_agg["night_transaction_ratio"] = (
        ratio_agg["night_txns"] / ratio_agg["total_for_ratio"].replace(0, 1)
    ).round(4)
    ratio_agg["large_transaction_ratio"] = (
        ratio_agg["large_txns"] / ratio_agg["total_for_ratio"].replace(0, 1)
    ).round(4)
    ratio_agg["merchant_diversity"] = ratio_agg["unique_merchants"]
    ratio_agg = ratio_agg[
        [
            "customer_id",
            "weekend_spending_ratio",
            "night_transaction_ratio",
            "large_transaction_ratio",
            "merchant_diversity",
        ]
    ]

    # --- Merge all ---
    df = amt_agg.copy()
    for sub_df in [
        daily_avg,
        weekly_avg,
        monthly_avg,
        roll7,
        roll30,
        velocity,
        ratio_agg,
    ]:
        df = df.merge(sub_df, on="customer_id", how="left")

    df = df.fillna(0)
    print(f"[Transaction] Generated {len(df)} rows, {len(df.columns)} features.")
    return df
