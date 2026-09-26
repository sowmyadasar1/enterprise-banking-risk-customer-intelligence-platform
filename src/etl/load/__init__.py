"""
ETL Loading Layer — Writes processed DataFrames to Bronze, Silver, and Gold layers.
Supports Parquet (primary) and CSV (secondary) formats.
"""

from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.etl.base import BaseLoader, PipelineResult


class DataLoader(BaseLoader):
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)

    def _get_domain(self, dataset_name: str) -> str:
        domain_mapping = {
            "regions": "reference",
            "products": "reference",
            "transaction_types": "reference",
            "merchant_categories": "reference",
            "exchange_rates": "reference",
            "calendar": "reference",
            "branches": "reference",
            "employees": "reference",
            "merchants": "finance",
            "customers": "customers",
            "customer_addresses": "customers",
            "customer_employment": "customers",
            "customer_segments": "customers",
            "kyc_information": "customers",
            "beneficiaries": "customers",
            "accounts": "finance",
            "loans": "finance",
            "credit_cards": "finance",
            "transactions": "finance",
            "loan_payments": "finance",
            "loan_default_labels": "finance",
            "customer_risk_scores": "finance",
            "fraud_cases": "finance",
            "fraud_investigations": "finance",
            "marketing_campaigns": "customers",
            "campaign_responses": "customers",
            "support_tickets": "customers",
            "device_information": "customers",
            "login_history": "customers",
        }
        return domain_mapping.get(dataset_name, "other")

    def _add_metadata(
        self, df: pd.DataFrame, layer: str, dataset_name: str
    ) -> pd.DataFrame:
        df = df.copy()
        df["_etl_loaded_at"] = datetime.now()
        df["_etl_layer"] = layer
        df["_etl_source"] = dataset_name
        return df

    def load(
        self, df: pd.DataFrame, dest_path: Path, layer: str, save_csv: bool = False
    ) -> PipelineResult:
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(dest_path.with_suffix(".parquet"), index=False)
            if save_csv:
                df.to_csv(dest_path.with_suffix(".csv"), index=False)
            return PipelineResult(
                success=True,
                records_in=len(df),
                records_out=len(df),
                records_rejected=0,
                stage=layer,
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                records_in=len(df),
                records_out=0,
                records_rejected=0,
                errors=[str(e)],
                stage=layer,
            )

    def load_bronze(
        self, df: pd.DataFrame, dataset_name: str, config: Optional[Dict] = None
    ) -> PipelineResult:
        df_meta = self._add_metadata(df, "bronze", dataset_name)
        domain = self._get_domain(dataset_name)
        dest = self.base_path / "bronze" / domain / dataset_name
        return self.load(df_meta, dest, "bronze", save_csv=True)

    def load_silver(
        self, df: pd.DataFrame, dataset_name: str, config: Optional[Dict] = None
    ) -> PipelineResult:
        df_meta = self._add_metadata(df, "silver", dataset_name)
        domain = self._get_domain(dataset_name)
        dest = self.base_path / "silver" / domain / dataset_name
        return self.load(df_meta, dest, "silver")

    def load_gold(
        self, df: pd.DataFrame, dataset_name: str, config: Optional[Dict] = None
    ) -> PipelineResult:
        df_meta = self._add_metadata(df, "gold", dataset_name)
        domain = self._get_domain(dataset_name)
        dest = self.base_path / "gold" / domain / dataset_name
        return self.load(df_meta, dest, "gold")
