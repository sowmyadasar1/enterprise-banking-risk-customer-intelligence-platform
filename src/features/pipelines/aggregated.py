"""
Aggregated Features Pipeline
Generates entity-level aggregations for merchants, branches, regions, and products.
"""

import pandas as pd
import numpy as np


def build_merchant_aggregations(conn):
    """Aggregate transaction stats per merchant."""
    print("[Aggregated] Building merchant aggregations...")
    df = pd.read_sql(
        """
        SELECT t.merchant_id, m.merchant_name, m.merchant_category, m.is_online,
               t.amount_abs, t.transaction_id
        FROM fact_transactions t
        JOIN dim_merchant m ON t.merchant_id = m.merchant_id
    """,
        conn,
    )
    df["amount_abs"] = pd.to_numeric(df["amount_abs"], errors="coerce").fillna(0)
    agg = (
        df.groupby(["merchant_id", "merchant_name", "merchant_category"])
        .agg(
            merchant_txn_count=("transaction_id", "count"),
            merchant_total_spend=("amount_abs", "sum"),
            merchant_avg_spend=("amount_abs", "mean"),
            merchant_max_spend=("amount_abs", "max"),
        )
        .reset_index()
        .round(2)
    )
    print(f"  -> {len(agg)} merchants")
    return agg


def build_branch_aggregations(conn):
    """Aggregate account stats per branch."""
    print("[Aggregated] Building branch aggregations...")
    df = pd.read_sql(
        """
        SELECT a.branch_id, b.branch_name, b.city, b.state,
               a.account_id, a.current_balance
        FROM dim_account a
        JOIN dim_branch b ON a.branch_id = b.branch_id
    """,
        conn,
    )
    df["current_balance"] = pd.to_numeric(
        df["current_balance"], errors="coerce"
    ).fillna(0)
    agg = (
        df.groupby(["branch_id", "branch_name", "city", "state"])
        .agg(
            branch_account_count=("account_id", "nunique"),
            branch_total_balance=("current_balance", "sum"),
            branch_avg_balance=("current_balance", "mean"),
        )
        .reset_index()
        .round(2)
    )
    print(f"  -> {len(agg)} branches")
    return agg


def build_region_aggregations(conn):
    """Aggregate branch stats per region."""
    print("[Aggregated] Building region aggregations...")
    df = pd.read_sql(
        """
        SELECT r.region_id, r.region_name, b.branch_id, a.current_balance, a.account_id
        FROM dim_region r
        JOIN dim_branch b ON r.region_id = b.region_id
        JOIN dim_account a ON b.branch_id = a.branch_id
    """,
        conn,
    )
    df["current_balance"] = pd.to_numeric(
        df["current_balance"], errors="coerce"
    ).fillna(0)
    agg = (
        df.groupby(["region_id", "region_name"])
        .agg(
            region_branch_count=("branch_id", "nunique"),
            region_account_count=("account_id", "nunique"),
            region_total_balance=("current_balance", "sum"),
            region_avg_balance=("current_balance", "mean"),
        )
        .reset_index()
        .round(2)
    )
    print(f"  -> {len(agg)} regions")
    return agg


def build_product_aggregations(conn):
    """Aggregate usage stats per product."""
    print("[Aggregated] Building product aggregations...")
    df = pd.read_sql(
        """
        SELECT p.product_id, p.product_name, p.product_category, p.product_type,
               a.account_id, a.current_balance
        FROM dim_product p
        JOIN dim_account a ON p.product_id = a.product_id
    """,
        conn,
    )
    df["current_balance"] = pd.to_numeric(
        df["current_balance"], errors="coerce"
    ).fillna(0)
    agg = (
        df.groupby(["product_id", "product_name", "product_category", "product_type"])
        .agg(
            product_account_count=("account_id", "nunique"),
            product_total_balance=("current_balance", "sum"),
            product_avg_balance=("current_balance", "mean"),
        )
        .reset_index()
        .round(2)
    )
    print(f"  -> {len(agg)} products")
    return agg


def build_all_aggregations(conn):
    """Build all entity-level aggregations and return as dict of DataFrames."""
    return {
        "merchant": build_merchant_aggregations(conn),
        "branch": build_branch_aggregations(conn),
        "region": build_region_aggregations(conn),
        "product": build_product_aggregations(conn),
    }
