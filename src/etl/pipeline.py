"""
ETL Pipeline — Master orchestrator for the Enterprise Banking ETL pipeline.
Enterprise Banking Risk & Customer Intelligence Platform — Phase 3

Coordinates Extract → Validate → Clean → Transform → Load → Quality for all 29 datasets.
Execution follows topological dependency order to respect FK constraints.
"""

import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Bootstrap project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.etl.config import ETLConfig, CONFIG
from src.etl.base import PipelineResult
from src.etl.logging import get_pipeline_logger, ETLTimer, PipelineAuditLogger

log = get_pipeline_logger("pipeline")
audit = PipelineAuditLogger()

# ---------------------------------------------------------------------------
# Dataset → raw folder mapping (mirrors run_generator.py)
# ---------------------------------------------------------------------------
DATASET_FOLDER_MAP: Dict[str, str] = {
    "regions": "reference_data",
    "branches": "reference_data",
    "products": "reference_data",
    "transaction_types": "reference_data",
    "merchant_categories": "reference_data",
    "exchange_rates": "reference_data",
    "calendar": "reference_data",
    "customers": "customers",
    "customer_addresses": "customers",
    "customer_employment": "customers",
    "customer_segments": "customers",
    "kyc_information": "customers",
    "beneficiaries": "customers",
    "customer_risk_scores": "customers",
    "accounts": "finance",
    "credit_cards": "finance",
    "loans": "finance",
    "loan_payments": "finance",
    "loan_default_labels": "risk",
    "employees": "operations",
    "support_tickets": "operations",
    "device_information": "operations",
    "login_history": "operations",
    "marketing_campaigns": "marketing",
    "campaign_responses": "marketing",
    "merchants": "transactions",
    "transactions": "transactions",
    "fraud_cases": "fraud",
    "fraud_investigations": "fraud",
}

# Execution order respecting FK dependencies
EXECUTION_TIERS: List[List[str]] = [
    # Tier 0: Pure reference data
    [
        "regions",
        "products",
        "transaction_types",
        "merchant_categories",
        "exchange_rates",
        "calendar",
    ],
    # Tier 1: Branches
    ["branches"],
    # Tier 2: Independent operational
    ["employees", "merchants"],
    # Tier 3: Customers
    [
        "customers",
        "customer_addresses",
        "customer_employment",
        "customer_segments",
        "kyc_information",
        "beneficiaries",
    ],
    # Tier 4: Finance (depend on customers + branches)
    ["accounts", "loans", "credit_cards"],
    # Tier 5: Transactions
    ["transactions"],
    # Tier 6: All downstream
    [
        "loan_payments",
        "loan_default_labels",
        "customer_risk_scores",
        "fraud_cases",
        "fraud_investigations",
        "marketing_campaigns",
        "campaign_responses",
        "support_tickets",
        "device_information",
        "login_history",
    ],
]


class ETLPipeline:
    """
    Master ETL pipeline orchestrator.

    Executes the full Extract → Validate → Clean → Transform → Load → Quality
    cycle for all 29 banking datasets using the Medallion Architecture.
    """

    def __init__(self, config: Optional[ETLConfig] = None):
        self.config = config or CONFIG
        self.config.ensure_dirs()

        # Import all ETL components
        from src.etl.extract import DataExtractor
        from src.etl.validate import DatasetValidator
        from src.etl.clean import DataCleaner
        from src.etl.transform import DataTransformer
        from src.etl.load import DataLoader
        from src.etl.quality import DataQualityChecker

        self.extractor = DataExtractor(self.config)
        self.validator = DatasetValidator()
        self.cleaner = DataCleaner()
        self.transformer = DataTransformer()
        self.loader = DataLoader(base_path=str(PROJECT_ROOT / "data"))
        self.dq_checker = DataQualityChecker()

        # In-memory dataset stores for cross-dataset transforms
        self.raw_dfs: Dict[str, pd.DataFrame] = {}
        self.bronze_dfs: Dict[str, pd.DataFrame] = {}
        self.silver_dfs: Dict[str, pd.DataFrame] = {}
        self.gold_dfs: Dict[str, pd.DataFrame] = {}

        # Pipeline summary metrics
        self.pipeline_errors: List[str] = []
        self.pipeline_warnings: List[str] = []
        self.dq_checks: List = []

    # -------------------------------------------------------------------------
    # Internal stage helpers
    # -------------------------------------------------------------------------

    def _extract(self, dataset_name: str) -> Tuple[pd.DataFrame, PipelineResult]:
        """Extract raw data for a single dataset."""
        t0 = time.time()
        try:
            df, result = self.extractor.extract_dataset(dataset_name)
            result.duration_seconds = time.time() - t0
            return df, result
        except Exception as exc:
            dur = time.time() - t0
            err = f"Extraction failed for {dataset_name}: {exc}"
            log.error(err)
            return pd.DataFrame(), PipelineResult(
                success=False,
                records_in=0,
                records_out=0,
                records_rejected=0,
                errors=[err],
                warnings=[],
                duration_seconds=dur,
                stage="extract",
            )

    def _validate(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Validate schema, PKs, FKs, and business rules."""
        t0 = time.time()
        try:
            valid_df, errors, warnings = self.validator.validate(
                df, dataset_name, self.raw_dfs
            )
            result = PipelineResult(
                success=len(errors) == 0,
                records_in=len(df),
                records_out=len(valid_df),
                records_rejected=len(df) - len(valid_df),
                errors=errors,
                warnings=warnings,
                duration_seconds=time.time() - t0,
                stage="validate",
            )
            return valid_df, result
        except Exception as exc:
            dur = time.time() - t0
            err = f"Validation error for {dataset_name}: {exc}"
            log.error(err)
            return df, PipelineResult(
                success=False,
                records_in=len(df),
                records_out=len(df),
                records_rejected=0,
                errors=[err],
                warnings=[],
                duration_seconds=dur,
                stage="validate",
            )

    def _clean(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Clean: deduplicate, fill nulls, normalize strings/dates."""
        t0 = time.time()
        try:
            clean_df, rejected_df, result = self.cleaner.clean(df, dataset_name)
            result.duration_seconds = time.time() - t0
            return clean_df, result
        except Exception as exc:
            dur = time.time() - t0
            err = f"Cleaning error for {dataset_name}: {exc}"
            log.error(err)
            return df, PipelineResult(
                success=False,
                records_in=len(df),
                records_out=len(df),
                records_rejected=0,
                errors=[err],
                warnings=[],
                duration_seconds=dur,
                stage="clean",
            )

    def _transform(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, PipelineResult]:
        """Add derived/engineered columns for Gold layer."""
        t0 = time.time()
        try:
            gold_df, result = self.transformer.transform(
                df,
                dataset_name,
                customers_df=self.silver_dfs.get("customers"),
                accounts_df=self.silver_dfs.get("accounts"),
                loans_df=self.silver_dfs.get("loans"),
                transactions_df=self.silver_dfs.get("transactions"),
            )
            result.duration_seconds = time.time() - t0
            return gold_df, result
        except Exception as exc:
            dur = time.time() - t0
            err = f"Transform error for {dataset_name}: {exc}"
            log.error(err)
            return df, PipelineResult(
                success=False,
                records_in=len(df),
                records_out=len(df),
                records_rejected=0,
                errors=[err],
                warnings=[],
                duration_seconds=dur,
                stage="transform",
            )

    def _process_dataset(self, dataset_name: str) -> bool:
        """
        Run full pipeline for one dataset:
        Extract → Validate → Bronze → Clean → Silver → Transform → Gold
        """
        log.info(f"  ── {dataset_name}")
        folder = DATASET_FOLDER_MAP.get(dataset_name, "reference_data")

        try:
            # 1. EXTRACT
            df, result = self._extract(dataset_name)
            if df.empty and not result.success:
                self.pipeline_errors.append(f"{dataset_name}: extraction failed")
                return False
            self.raw_dfs[dataset_name] = df
            audit.log_event(
                "extract",
                dataset_name,
                result.records_in,
                result.records_out,
                result.records_rejected,
                "SUCCESS" if result.success else "FAIL",
                result.duration_seconds,
            )

            # 2. VALIDATE
            valid_df, result = self._validate(df, dataset_name)
            for w in result.warnings:
                log.warning(f"    [WARN] {w}")
            for e in result.errors:
                log.error(f"    [ERR]  {e}")
            audit.log_event(
                "validate",
                dataset_name,
                result.records_in,
                result.records_out,
                result.records_rejected,
                "SUCCESS" if result.success else "WARN",
                result.duration_seconds,
            )

            # 3. LOAD BRONZE (validated raw copy)
            bronze_result = self.loader.load_bronze(valid_df, dataset_name)
            self.bronze_dfs[dataset_name] = valid_df
            audit.log_event(
                "load_bronze",
                dataset_name,
                bronze_result.records_in,
                bronze_result.records_out,
                bronze_result.records_rejected,
                "SUCCESS" if bronze_result.success else "FAIL",
                bronze_result.duration_seconds,
            )

            # 4. CLEAN
            clean_df, result = self._clean(valid_df, dataset_name)
            audit.log_event(
                "clean",
                dataset_name,
                result.records_in,
                result.records_out,
                result.records_rejected,
                "SUCCESS" if result.success else "WARN",
                result.duration_seconds,
            )

            # 5. LOAD SILVER (cleaned)
            silver_result = self.loader.load_silver(clean_df, dataset_name)
            self.silver_dfs[dataset_name] = clean_df
            audit.log_event(
                "load_silver",
                dataset_name,
                silver_result.records_in,
                silver_result.records_out,
                silver_result.records_rejected,
                "SUCCESS" if silver_result.success else "FAIL",
                silver_result.duration_seconds,
            )

            # 6. TRANSFORM
            gold_df, result = self._transform(clean_df, dataset_name)
            audit.log_event(
                "transform",
                dataset_name,
                result.records_in,
                result.records_out,
                result.records_rejected,
                "SUCCESS" if result.success else "WARN",
                result.duration_seconds,
            )

            # 7. LOAD GOLD (enriched)
            gold_result = self.loader.load_gold(gold_df, dataset_name)
            self.gold_dfs[dataset_name] = gold_df
            audit.log_event(
                "load_gold",
                dataset_name,
                gold_result.records_in,
                gold_result.records_out,
                gold_result.records_rejected,
                "SUCCESS" if gold_result.success else "FAIL",
                gold_result.duration_seconds,
            )

            log.info(
                f"    Raw:{len(df):>8,}  Bronze:{len(valid_df):>8,}  "
                f"Silver:{len(clean_df):>8,}  Gold:{len(gold_df):>8,}"
            )
            return True

        except Exception as exc:
            err = f"{dataset_name}: unexpected error — {exc}"
            log.error(err)
            log.debug(traceback.format_exc())
            self.pipeline_errors.append(err)
            return False

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(self, datasets: Optional[List[str]] = None) -> Dict:
        """
        Execute the full ETL pipeline in dependency order.

        Args:
            datasets: Optional subset of dataset names to process.
                      If None, all 29 datasets are processed.

        Returns:
            Summary dict with row counts, error count, duration.
        """
        t_total = time.time()
        log.info("╔══════════════════════════════════════════════════════╗")
        log.info("║  Enterprise Banking ETL Pipeline — Starting         ║")
        log.info("╚══════════════════════════════════════════════════════╝")

        processed = 0
        failed = 0

        for tier_num, tier in enumerate(EXECUTION_TIERS):
            log.info(f"\n── Tier {tier_num} ──────────────────────────────────────")
            for ds in tier:
                if datasets and ds not in datasets:
                    continue
                ok = self._process_dataset(ds)
                if ok:
                    processed += 1
                else:
                    failed += 1

        # Run quality report
        log.info("\n── Data Quality Report ─────────────────────────────────")
        try:
            self.dq_checks = self.dq_checker.run_all_checks(
                {
                    "bronze": self.bronze_dfs,
                    "silver": self.silver_dfs,
                    "gold": self.gold_dfs,
                },
                self.raw_dfs,
            )
            report = self.dq_checker.generate_report(
                self.dq_checks, self.config.reports_dir / "dq_report.json"
            )
            log.info(
                f"  DQ Score: {report.get('overall_score', 0):.1f}%  "
                f"({report.get('passed', 0)} passed / "
                f"{report.get('total_checks', 0)} total checks)"
            )
        except Exception as exc:
            log.warning(f"  Quality report failed: {exc}")
            report = {}

        elapsed = time.time() - t_total

        summary = {
            "datasets_processed": processed,
            "datasets_failed": failed,
            "total_raw_rows": sum(len(v) for v in self.raw_dfs.values()),
            "total_bronze_rows": sum(len(v) for v in self.bronze_dfs.values()),
            "total_silver_rows": sum(len(v) for v in self.silver_dfs.values()),
            "total_gold_rows": sum(len(v) for v in self.gold_dfs.values()),
            "pipeline_errors": self.pipeline_errors,
            "dq_report": report,
            "duration_seconds": elapsed,
        }

        self._print_summary(summary)
        return summary

    def _print_summary(self, summary: Dict) -> None:
        elapsed = summary["duration_seconds"]
        log.info("\n╔══════════════════════════════════════════════════════╗")
        log.info("║  ETL Pipeline Summary                               ║")
        log.info("╠══════════════════════════════════════════════════════╣")
        log.info(f"║  Datasets processed : {summary['datasets_processed']:<30}║")
        log.info(f"║  Datasets failed    : {summary['datasets_failed']:<30}║")
        log.info(
            f"║  Raw rows           : {summary['total_raw_rows']:>15,}               ║"
        )
        log.info(
            f"║  Bronze rows        : {summary['total_bronze_rows']:>15,}               ║"
        )
        log.info(
            f"║  Silver rows        : {summary['total_silver_rows']:>15,}               ║"
        )
        log.info(
            f"║  Gold rows          : {summary['total_gold_rows']:>15,}               ║"
        )
        log.info(f"║  Duration           : {elapsed:<.1f}s{'':<28}║")
        dq = summary.get("dq_report", {})
        log.info(f"║  DQ Score           : {dq.get('overall_score', 'N/A')!s:<30}║")
        log.info("╚══════════════════════════════════════════════════════╝")
        if summary["pipeline_errors"]:
            log.warning("  Errors:")
            for e in summary["pipeline_errors"]:
                log.warning(f"    • {e}")

    def get_summary(self) -> Dict:
        """Return a summary dict of current pipeline state."""
        return {
            "bronze_datasets": list(self.bronze_dfs.keys()),
            "silver_datasets": list(self.silver_dfs.keys()),
            "gold_datasets": list(self.gold_dfs.keys()),
            "errors": self.pipeline_errors,
        }
