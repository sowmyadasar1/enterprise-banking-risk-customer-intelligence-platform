"""
Enterprise Banking Risk & Customer Intelligence Platform
Phase 2 — Synthetic Data Generation Runner

Calls each generator in topological dependency order and saves all datasets
to data/raw/<category>/ as CSV + Parquet + metadata JSON.

Usage:
    python run_generator.py --scale 0.1   # 10% of full scale (~small dataset)
    python run_generator.py --scale 1.0   # Full scale
    python run_generator.py               # Default scale 0.1
"""

import argparse
import json
import logging
import os
import sys
import time

import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("DataGenerator")

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Dataset → folder mapping
# ---------------------------------------------------------------------------
DATASET_FOLDERS = {
    "regions":               "reference_data",
    "branches":              "reference_data",
    "products":              "reference_data",
    "transaction_types":     "reference_data",
    "merchant_categories":   "reference_data",
    "exchange_rates":        "reference_data",
    "calendar":              "reference_data",
    "customers":             "customers",
    "customer_addresses":    "customers",
    "customer_employment":   "customers",
    "customer_segments":     "customers",
    "customer_risk_scores":  "customers",
    "kyc_information":       "customers",
    "beneficiaries":         "customers",
    "accounts":              "finance",
    "credit_cards":          "finance",
    "loans":                 "finance",
    "loan_payments":         "finance",
    "loan_default_labels":   "risk",
    "employees":             "operations",
    "support_tickets":       "operations",
    "marketing_campaigns":   "marketing",
    "campaign_responses":    "marketing",
    "merchants":             "transactions",
    "transactions":          "transactions",
    "fraud_cases":           "fraud",
    "fraud_investigations":  "fraud",
    "device_information":    "operations",
    "login_history":         "operations",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_dirs():
    for folder in set(DATASET_FOLDERS.values()):
        os.makedirs(os.path.join(RAW_DIR, folder), exist_ok=True)
    log.info("Data directories ready.")


def save_dataset(df: pd.DataFrame, name: str) -> None:
    folder = DATASET_FOLDERS.get(name, "reference_data")
    base_path = os.path.join(RAW_DIR, folder, name)
    df.to_csv(f"{base_path}.csv", index=False)
    df.to_parquet(f"{base_path}.parquet", index=False)
    meta = {
        "dataset": name,
        "row_count": len(df),
        "columns": len(df.columns),
        "schema": {col: str(df[col].dtype) for col in df.columns},
        "generated_at": pd.Timestamp.utcnow().isoformat(),
    }
    with open(f"{base_path}_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    log.info(f"  ✓ {name:30s} {len(df):>10,} rows  → data/raw/{folder}/")


def load_fn(module_name: str, func_name: str):
    import importlib
    mod = importlib.import_module(f"src.data_generation.{module_name}")
    return getattr(mod, func_name)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(scale: float = 0.1, seed: int = 42):
    ensure_dirs()

    def n(base: int) -> int:
        return max(1, int(base * scale))

    dfs = {}
    t0 = time.time()

    # ── Tier 0: Pure Reference Data ────────────────────────────────────────
    log.info("── Tier 0: Reference Data ──────────────────────────────")

    dfs["regions"] = load_fn("regions", "generate_regions")(n=n(50), seed=seed)
    save_dataset(dfs["regions"], "regions")

    dfs["products"] = load_fn("products", "generate_products")(n=n(30), seed=seed)
    save_dataset(dfs["products"], "products")

    dfs["transaction_types"] = load_fn("transaction_types", "generate_transaction_types")(n=n(20), seed=seed)
    save_dataset(dfs["transaction_types"], "transaction_types")

    dfs["merchant_categories"] = load_fn("merchant_categories", "generate_merchant_categories")(n=n(100), seed=seed)
    save_dataset(dfs["merchant_categories"], "merchant_categories")

    dfs["exchange_rates"] = load_fn("exchange_rates", "generate_exchange_rates")(n=n(1000), seed=seed)
    save_dataset(dfs["exchange_rates"], "exchange_rates")

    dfs["calendar"] = load_fn("calendar_dim", "generate_calendar_dim")(n=n(3650), seed=seed)
    save_dataset(dfs["calendar"], "calendar")

    # ── Tier 1: Branches (depends on regions) ─────────────────────────────
    log.info("── Tier 1: Branches ────────────────────────────────────")
    dfs["branches"] = load_fn("branches", "generate_branches")(n=n(500), seed=seed, regions=dfs["regions"])
    save_dataset(dfs["branches"], "branches")

    # ── Tier 2: Employees & Merchants ─────────────────────────────────────
    log.info("── Tier 2: Employees & Merchants ───────────────────────")
    dfs["employees"] = load_fn("employees", "generate_employees")(n=n(5000), seed=seed, branches=dfs["branches"])
    save_dataset(dfs["employees"], "employees")

    dfs["merchants"] = load_fn("merchants", "generate_merchants")(n=n(2000), seed=seed, merchant_categories=dfs["merchant_categories"])
    save_dataset(dfs["merchants"], "merchants")

    # ── Tier 3: Customers ─────────────────────────────────────────────────
    log.info("── Tier 3: Customers ───────────────────────────────────")
    dfs["customers"] = load_fn("customers", "generate_customers")(n=n(10000), seed=seed, branches=dfs["branches"])
    save_dataset(dfs["customers"], "customers")

    dfs["customer_addresses"] = load_fn("customer_addresses", "generate_customer_addresses")(n=n(10000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["customer_addresses"], "customer_addresses")

    dfs["customer_employment"] = load_fn("customer_employment", "generate_customer_employment")(n=n(9000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["customer_employment"], "customer_employment")

    dfs["customer_segments"] = load_fn("customer_segments", "generate_customer_segments")(n=n(10000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["customer_segments"], "customer_segments")

    dfs["kyc_information"] = load_fn("kyc_information", "generate_kyc_information")(n=n(10000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["kyc_information"], "kyc_information")

    dfs["beneficiaries"] = load_fn("beneficiaries", "generate_beneficiaries")(n=n(15000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["beneficiaries"], "beneficiaries")

    # ── Tier 4: Finance ───────────────────────────────────────────────────
    log.info("── Tier 4: Finance ─────────────────────────────────────")
    dfs["accounts"] = load_fn("accounts", "generate_accounts")(n=n(15000), seed=seed, customers=dfs["customers"], branches=dfs["branches"])
    save_dataset(dfs["accounts"], "accounts")

    dfs["loans"] = load_fn("loans", "generate_loans")(n=n(5000), seed=seed, customers=dfs["customers"], branches=dfs["branches"])
    save_dataset(dfs["loans"], "loans")

    dfs["credit_cards"] = load_fn("credit_cards", "generate_credit_cards")(n=n(8000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["credit_cards"], "credit_cards")

    # ── Tier 5: Transactions ──────────────────────────────────────────────
    log.info("── Tier 5: Transactions ────────────────────────────────")
    dfs["transactions"] = load_fn("transactions", "generate_transactions")(n=n(500000), seed=seed, accounts=dfs["accounts"], merchants=dfs["merchants"])
    save_dataset(dfs["transactions"], "transactions")

    # ── Tier 6: Downstream ────────────────────────────────────────────────
    log.info("── Tier 6: Downstream Entities ────────────────────────")
    dfs["loan_payments"] = load_fn("loan_payments", "generate_loan_payments")(n=n(50000), seed=seed, loans=dfs["loans"])
    save_dataset(dfs["loan_payments"], "loan_payments")

    dfs["loan_default_labels"] = load_fn("loan_default_labels", "generate_loan_default_labels")(n=n(5000), seed=seed, loans=dfs["loans"])
    save_dataset(dfs["loan_default_labels"], "loan_default_labels")

    dfs["customer_risk_scores"] = load_fn("customer_risk_scores", "generate_customer_risk_scores")(n=n(10000), seed=seed, customers=dfs["customers"], loans=dfs["loans"])
    save_dataset(dfs["customer_risk_scores"], "customer_risk_scores")

    dfs["fraud_cases"] = load_fn("fraud_cases", "generate_fraud_cases")(n=n(5000), seed=seed, transactions=dfs["transactions"])
    save_dataset(dfs["fraud_cases"], "fraud_cases")

    dfs["fraud_investigations"] = load_fn("fraud_investigations", "generate_fraud_investigations")(n=n(1000), seed=seed, fraud_cases=dfs["fraud_cases"])
    save_dataset(dfs["fraud_investigations"], "fraud_investigations")

    dfs["marketing_campaigns"] = load_fn("marketing_campaigns", "generate_marketing_campaigns")(n=n(500), seed=seed, products=dfs["products"])
    save_dataset(dfs["marketing_campaigns"], "marketing_campaigns")

    dfs["campaign_responses"] = load_fn("campaign_responses", "generate_campaign_responses")(n=n(20000), seed=seed, customers=dfs["customers"], marketing_campaigns=dfs["marketing_campaigns"])
    save_dataset(dfs["campaign_responses"], "campaign_responses")

    dfs["support_tickets"] = load_fn("support_tickets", "generate_support_tickets")(n=n(20000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["support_tickets"], "support_tickets")

    dfs["device_information"] = load_fn("device_information", "generate_device_information")(n=n(25000), seed=seed, customers=dfs["customers"])
    save_dataset(dfs["device_information"], "device_information")

    dfs["login_history"] = load_fn("login_history", "generate_login_history")(n=n(100000), seed=seed, customers=dfs["customers"], device_information=dfs["device_information"])
    save_dataset(dfs["login_history"], "login_history")

    # ── Summary ────────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    total_rows = sum(len(v) for v in dfs.values())
    log.info("")
    log.info("═══════════════════════════════════════════════════════")
    log.info(f"  ✅ Phase 2 Complete!")
    log.info(f"  📊 Datasets generated : {len(dfs)}")
    log.info(f"  📈 Total rows          : {total_rows:,}")
    log.info(f"  ⏱  Time elapsed        : {elapsed:.1f}s")
    log.info(f"  📁 Output dir          : data/raw/")
    log.info("═══════════════════════════════════════════════════════")
    return dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise Banking Synthetic Data Generator")
    parser.add_argument("--scale", type=float, default=0.1,
                        help="Scale factor (0.1 = 10%% of full size, 1.0 = full size)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    run(scale=args.scale, seed=args.seed)
