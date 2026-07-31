import os
import pandas as pd
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
import json
import logging

from src.etl.base import BaseExtractor, PipelineResult
from src.etl.config import ETLConfig


logger = logging.getLogger(__name__)


import warnings

class CsvExtractor(BaseExtractor):
    def extract(self, path: Path) -> pd.DataFrame:
        logger.info(f"Extracting CSV from {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")
        try:
            df = pd.read_csv(path, low_memory=False)
            if df.empty:
                warnings.warn("File is empty", UserWarning)
            return df
        except pd.errors.EmptyDataError:
            warnings.warn("File is empty", UserWarning)
            return pd.DataFrame()
        except UnicodeDecodeError:
            logger.warning(f"Encoding issue with {path}, falling back to ISO-8859-1")
            return pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)


class ParquetExtractor(BaseExtractor):
    def extract(self, path: Path) -> pd.DataFrame:
        logger.info(f"Extracting Parquet from {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")
        try:
            df = pd.read_parquet(path)
            if df.empty:
                warnings.warn("File is empty", UserWarning)
            return df
        except Exception:
            # For empty parquet files that raise exception
            warnings.warn("File is empty", UserWarning)
            return pd.DataFrame()


class JsonExtractor(BaseExtractor):
    def extract(self, path: Path) -> pd.DataFrame:
        logger.info(f"Extracting JSON from {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")
        try:
            df = pd.read_json(path, lines=True)
            if df.empty:
                warnings.warn("File is empty", UserWarning)
            return df
        except ValueError:
            try:
                df = pd.read_json(path)
                if df.empty:
                    warnings.warn("File is empty", UserWarning)
                return df
            except Exception:
                warnings.warn("File is empty", UserWarning)
                return pd.DataFrame()


class DataExtractor:
    DATASET_MAPPING = {
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

    def __init__(self, config: ETLConfig):
        self.config = config
        self.raw_dir = Path(config.raw_dir)
        self.csv_extractor = CsvExtractor()
        self.parquet_extractor = ParquetExtractor()
        self.json_extractor = JsonExtractor()

    def extract_dataset(self, dataset_name: str, prefer_parquet: bool = True) -> Tuple[pd.DataFrame, PipelineResult]:
        folder = self.DATASET_MAPPING.get(dataset_name, "")
        base_path = self.raw_dir / folder / dataset_name
        
        df = None
        result = None
        
        # Extensions to try based on preference
        extensions = [".parquet", ".csv", ".json", ".jsonl"] if prefer_parquet else [".csv", ".parquet", ".json", ".jsonl"]
        
        found_file = None
        for ext in extensions:
            file_path = base_path.with_suffix(ext)
            if file_path.exists():
                found_file = file_path
                break
                
        if not found_file:
            return pd.DataFrame(), PipelineResult(
                success=False, records_in=0, records_out=0, records_rejected=0,
                errors=[f"No file found for dataset: {dataset_name} in {base_path.parent}"],
                stage="extract"
            )
            
        try:
            if found_file.suffix == ".csv":
                df = self.csv_extractor.extract(found_file)
            elif found_file.suffix == ".parquet":
                df = self.parquet_extractor.extract(found_file)
            elif found_file.suffix in [".json", ".jsonl"]:
                df = self.json_extractor.extract(found_file)
            else:
                return pd.DataFrame(), PipelineResult(
                    success=False, records_in=0, records_out=0, records_rejected=0,
                    errors=[f"Unsupported file format: {found_file.suffix}"], stage="extract"
                )

            return df, PipelineResult(
                success=True, records_in=len(df), records_out=len(df),
                records_rejected=0, stage="extract"
            )
        except Exception as e:
            logger.error(f"Error extracting {dataset_name}: {str(e)}")
            return pd.DataFrame(), PipelineResult(
                success=False, records_in=0, records_out=0, records_rejected=0,
                errors=[f"Error extracting {dataset_name}: {str(e)}"], stage="extract"
            )

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        datasets = {}
        for dataset_name in self.DATASET_MAPPING.keys():
            logger.info(f"Starting extraction for {dataset_name}")
            df, result = self.extract_dataset(dataset_name)
            if result.success:
                datasets[dataset_name] = df
            else:
                logger.warning(f"Failed to extract {dataset_name}: {result.errors}")
        return datasets
