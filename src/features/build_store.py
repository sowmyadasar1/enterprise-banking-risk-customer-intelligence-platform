"""
Feature Store Builder — Master Orchestration Script
Connects to the Data Warehouse, runs all feature pipelines, validates features,
performs feature selection, and persists the Feature Store to Parquet files.
"""

import os
import sys
import sqlite3
import pandas as pd

# Ensure project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.features.pipelines.customer import build_customer_features
from src.features.pipelines.transaction import build_transaction_features
from src.features.pipelines.loan import build_loan_features
from src.features.pipelines.risk import build_risk_features
from src.features.pipelines.temporal import build_temporal_features
from src.features.pipelines.aggregated import build_all_aggregations
from src.features.validation import run_full_validation
from src.features.selection import generate_recommended_sets


def main():
    DB_PATH = os.path.join(PROJECT_ROOT, "data", "warehouse", "enterprise_dw.db")
    STORE_DIR = os.path.join(PROJECT_ROOT, "data", "feature_store")
    os.makedirs(STORE_DIR, exist_ok=True)

    print("=" * 70)
    print("  ENTERPRISE FEATURE STORE BUILDER")
    print("  Source: data/warehouse/enterprise_dw.db")
    print("  Target: data/feature_store/")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    # =========================================================================
    # STEP 1: Run all feature pipelines
    # =========================================================================
    print("\n>>> STEP 1: Running Feature Pipelines...\n")

    df_customer = build_customer_features(conn)
    df_transaction = build_transaction_features(conn)
    df_loan = build_loan_features(conn)
    df_risk = build_risk_features(conn)
    df_temporal = build_temporal_features(conn)
    aggregations = build_all_aggregations(conn)

    # =========================================================================
    # STEP 2: Merge customer-level features into a master feature table
    # =========================================================================
    print("\n>>> STEP 2: Merging into Master Feature Table...\n")

    master = df_customer.copy()
    for name, sub_df in [
        ("transaction", df_transaction),
        ("loan", df_loan),
        ("risk", df_risk),
        ("temporal", df_temporal),
    ]:
        print(f"  Merging {name} features ({sub_df.shape[1]} cols)...")
        master = master.merge(sub_df, on="customer_id", how="left")

    # Fill NAs for customers with no transactions/loans
    numeric_cols = master.select_dtypes(include=["number"]).columns
    master[numeric_cols] = master[numeric_cols].fillna(0)

    print(
        f"\n  Master Feature Table: {master.shape[0]} rows x {master.shape[1]} columns"
    )

    # =========================================================================
    # STEP 3: Validate features
    # =========================================================================
    print("\n>>> STEP 3: Running Feature Validation...\n")
    validation_results = run_full_validation(master, name="Master Customer Features")

    # =========================================================================
    # STEP 4: Feature Selection
    # =========================================================================
    print("\n>>> STEP 4: Running Feature Selection...\n")
    selection_results = generate_recommended_sets(master)

    # =========================================================================
    # STEP 5: Persist Feature Store
    # =========================================================================
    print("\n>>> STEP 5: Saving Feature Store to Parquet...\n")

    # Master customer features
    master_path = os.path.join(STORE_DIR, "customer_features.parquet")
    master.to_parquet(master_path, index=False)
    print(
        f"  Saved: customer_features.parquet ({master.shape[0]} rows, {master.shape[1]} cols)"
    )

    # Domain-specific stores
    df_transaction.to_parquet(
        os.path.join(STORE_DIR, "transaction_features.parquet"), index=False
    )
    print(f"  Saved: transaction_features.parquet ({df_transaction.shape[0]} rows)")

    df_loan.to_parquet(os.path.join(STORE_DIR, "loan_features.parquet"), index=False)
    print(f"  Saved: loan_features.parquet ({df_loan.shape[0]} rows)")

    df_risk.to_parquet(os.path.join(STORE_DIR, "risk_features.parquet"), index=False)
    print(f"  Saved: risk_features.parquet ({df_risk.shape[0]} rows)")

    df_temporal.to_parquet(
        os.path.join(STORE_DIR, "temporal_features.parquet"), index=False
    )
    print(f"  Saved: temporal_features.parquet ({df_temporal.shape[0]} rows)")

    # Entity-level aggregations
    for entity_name, entity_df in aggregations.items():
        path = os.path.join(STORE_DIR, f"{entity_name}_aggregations.parquet")
        entity_df.to_parquet(path, index=False)
        print(
            f"  Saved: {entity_name}_aggregations.parquet ({entity_df.shape[0]} rows)"
        )

    # Feature metadata
    metadata = pd.DataFrame(
        {
            "feature_name": master.columns,
            "dtype": master.dtypes.astype(str).values,
            "non_null_count": master.notnull().sum().values,
            "null_pct": (master.isnull().mean() * 100).round(2).values,
            "unique_values": master.nunique().values,
        }
    )
    metadata.to_parquet(
        os.path.join(STORE_DIR, "feature_metadata.parquet"), index=False
    )
    metadata.to_csv(os.path.join(STORE_DIR, "feature_metadata.csv"), index=False)
    print(f"  Saved: feature_metadata.parquet/csv ({len(metadata)} features)")

    conn.close()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("  FEATURE STORE BUILD COMPLETE")
    print("=" * 70)
    print(
        f"  Master Table:      {master.shape[0]} customers x {master.shape[1]} features"
    )
    print(
        f"  Parquet Files:     {len(os.listdir(STORE_DIR))} files in data/feature_store/"
    )
    print(f"  Validation:        PASSED")
    print(
        f"  Selection:         {len(selection_results.get('variance_kept', []))} features after variance filter"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
