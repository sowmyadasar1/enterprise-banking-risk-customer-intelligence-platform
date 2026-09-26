"""
Customer Features Pipeline
Generates customer-level features from dim_customer, dim_account, fact_support_tickets,
and fact_marketing_responses.
"""

import pandas as pd
import numpy as np


def build_customer_features(conn):
    """Build comprehensive customer-level features."""
    print("[Customer] Loading base tables...")

    # --- Base customer data ---
    df_cust = pd.read_sql(
        "SELECT customer_id, date_of_birth, join_date, customer_type, "
        "risk_rating, is_active, tenure_days, tenure_years "
        "FROM dim_customer",
        conn,
    )
    for col in df_cust.columns:
        if df_cust[col].dtype == "object":
            try:
                df_cust[col] = pd.to_numeric(df_cust[col])
            except (ValueError, TypeError):
                pass

    # Customer Age
    df_cust["date_of_birth"] = pd.to_datetime(
        df_cust["date_of_birth"], errors="coerce", utc=True
    ).dt.tz_localize(None)
    df_cust["join_date"] = pd.to_datetime(
        df_cust["join_date"], errors="coerce", utc=True
    ).dt.tz_localize(None)
    today = pd.Timestamp.now().tz_localize(None)
    df_cust["customer_age"] = (
        ((today - df_cust["date_of_birth"]).dt.days / 365.25).fillna(0).astype(int)
    )
    df_cust["customer_tenure_days"] = df_cust["tenure_days"].fillna(0).astype(int)
    df_cust["customer_tenure_years"] = df_cust["tenure_years"].fillna(0.0)

    # --- Account aggregations ---
    df_acc = pd.read_sql(
        "SELECT customer_id, account_id, account_type, current_balance, "
        "open_date FROM dim_account",
        conn,
    )
    for col in df_acc.columns:
        if df_acc[col].dtype == "object":
            try:
                df_acc[col] = pd.to_numeric(df_acc[col])
            except (ValueError, TypeError):
                pass
    df_acc["current_balance"] = pd.to_numeric(
        df_acc["current_balance"], errors="coerce"
    ).fillna(0)

    acc_agg = (
        df_acc.groupby("customer_id")
        .agg(
            account_count=("account_id", "nunique"),
            avg_balance=("current_balance", "mean"),
            total_balance=("current_balance", "sum"),
            max_balance=("current_balance", "max"),
            min_balance=("current_balance", "min"),
            products_owned=("account_type", "nunique"),
        )
        .reset_index()
    )

    # Balance trend proxy: max - min
    acc_agg["balance_range"] = acc_agg["max_balance"] - acc_agg["min_balance"]

    # --- Support ticket count ---
    df_tickets = pd.read_sql(
        "SELECT customer_id, ticket_id FROM fact_support_tickets", conn
    )
    ticket_agg = (
        df_tickets.groupby("customer_id")
        .agg(support_ticket_count=("ticket_id", "count"))
        .reset_index()
    )

    # --- Marketing engagement ---
    df_mkt = pd.read_sql(
        "SELECT customer_id, response_id, converted FROM fact_marketing_responses", conn
    )
    df_mkt["converted"] = pd.to_numeric(df_mkt["converted"], errors="coerce").fillna(0)
    mkt_agg = (
        df_mkt.groupby("customer_id")
        .agg(
            marketing_responses=("response_id", "count"),
            marketing_conversions=("converted", "sum"),
        )
        .reset_index()
    )
    mkt_agg["marketing_engagement_score"] = (
        mkt_agg["marketing_conversions"] / mkt_agg["marketing_responses"].replace(0, 1)
    ).round(4)

    # --- Merge all ---
    df = df_cust[
        [
            "customer_id",
            "customer_age",
            "customer_tenure_days",
            "customer_tenure_years",
            "customer_type",
            "risk_rating",
            "is_active",
        ]
    ].copy()
    df = df.merge(acc_agg, on="customer_id", how="left")
    df = df.merge(ticket_agg, on="customer_id", how="left")
    df = df.merge(
        mkt_agg[["customer_id", "marketing_responses", "marketing_engagement_score"]],
        on="customer_id",
        how="left",
    )

    # Fill NAs
    df["account_count"] = df["account_count"].fillna(0).astype(int)
    df["avg_balance"] = df["avg_balance"].fillna(0.0)
    df["total_balance"] = df["total_balance"].fillna(0.0)
    df["products_owned"] = df["products_owned"].fillna(0).astype(int)
    df["balance_range"] = df["balance_range"].fillna(0.0)
    df["support_ticket_count"] = df["support_ticket_count"].fillna(0).astype(int)
    df["marketing_responses"] = df["marketing_responses"].fillna(0).astype(int)
    df["marketing_engagement_score"] = df["marketing_engagement_score"].fillna(0.0)

    # Customer Lifetime Value proxy: total_balance * tenure_years
    df["customer_lifetime_value"] = (
        df["total_balance"] * df["customer_tenure_years"]
    ).round(2)

    # Income band (proxy based on total balance)
    df["income_band"] = pd.cut(
        df["total_balance"],
        bins=[-np.inf, 10000, 50000, 150000, 500000, np.inf],
        labels=["Low", "Lower-Mid", "Middle", "Upper-Mid", "High"],
    ).astype(str)

    print(f"[Customer] Generated {len(df)} rows, {len(df.columns)} features.")
    return df
