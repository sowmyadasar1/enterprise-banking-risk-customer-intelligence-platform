"""
Risk & Credit Features Pipeline
Generates risk and credit features per customer from dim_risk and fact_fraud.
"""

import pandas as pd
import numpy as np


def build_risk_features(conn):
    """Build credit and risk features per customer."""
    print("[Risk] Loading risk tables...")

    df_risk = pd.read_sql(
        "SELECT customer_id, risk_score, risk_category, credit_score " "FROM dim_risk",
        conn,
    )
    df_fraud = pd.read_sql(
        """
        SELECT a.customer_id, f.fraud_case_id, f.financial_loss
        FROM fact_fraud f
        JOIN fact_transactions t ON f.transaction_id = t.transaction_id
        JOIN dim_account a ON t.account_id = a.account_id
    """,
        conn,
    )

    # Coerce numerics
    df_risk["risk_score"] = pd.to_numeric(
        df_risk["risk_score"], errors="coerce"
    ).fillna(0)
    df_risk["credit_score"] = pd.to_numeric(
        df_risk["credit_score"], errors="coerce"
    ).fillna(0)
    df_fraud["financial_loss"] = pd.to_numeric(
        df_fraud["financial_loss"], errors="coerce"
    ).fillna(0)

    # Take latest risk per customer (if duplicates)
    df_risk = df_risk.drop_duplicates(subset="customer_id", keep="last")

    # Credit Score Band
    df_risk["credit_score_band"] = pd.cut(
        df_risk["credit_score"],
        bins=[0, 580, 670, 740, 800, 850],
        labels=["Poor", "Fair", "Good", "Very Good", "Exceptional"],
        right=True,
    ).astype(str)

    # --- Fraud features ---
    fraud_agg = (
        df_fraud.groupby("customer_id")
        .agg(
            fraud_case_count=("fraud_case_id", "count"),
            total_fraud_loss=("financial_loss", "sum"),
        )
        .reset_index()
    )
    fraud_agg["fraud_risk_indicator"] = 1  # anyone with fraud cases gets flagged

    # --- Merge ---
    df = df_risk[
        [
            "customer_id",
            "risk_score",
            "risk_category",
            "credit_score",
            "credit_score_band",
        ]
    ].copy()
    df = df.merge(fraud_agg, on="customer_id", how="left")
    df["fraud_case_count"] = df["fraud_case_count"].fillna(0).astype(int)
    df["total_fraud_loss"] = df["total_fraud_loss"].fillna(0.0)
    df["fraud_risk_indicator"] = df["fraud_risk_indicator"].fillna(0).astype(int)

    # Loan risk indicator (high risk if risk_score > 70)
    df["loan_risk_indicator"] = (df["risk_score"] > 70).astype(int)

    print(f"[Risk] Generated {len(df)} rows, {len(df.columns)} features.")
    return df
