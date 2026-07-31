"""
ETL Configuration — Enterprise Banking Risk & Customer Intelligence Platform

Centralized configuration for the complete ETL pipeline. All paths, thresholds,
batch sizes, and runtime options are defined here.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class ETLConfig:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    raw_dir: Path = field(init=False)
    bronze_dir: Path = field(init=False)
    silver_dir: Path = field(init=False)
    gold_dir: Path = field(init=False)
    quarantine_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)
    
    batch_size: int = 50000
    random_seed: int = 42
    log_level: str = "INFO"
    validate_fk: bool = True
    validate_pk: bool = True
    null_threshold: float = 0.30  # max allowed null fraction
    duplicate_threshold: float = 0.01
    output_formats: List[str] = field(default_factory=lambda: ["parquet", "csv"])

    def __post_init__(self):
        self.raw_dir = self.project_root / "data" / "raw"
        self.bronze_dir = self.project_root / "data" / "bronze"
        self.silver_dir = self.project_root / "data" / "silver"
        self.gold_dir = self.project_root / "data" / "gold"
        self.quarantine_dir = self.project_root / "data" / "temp" / "quarantine"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir = self.project_root / "data" / "exports" / "quality_reports"

    def ensure_dirs(self) -> None:
        """Creates all directories if they do not exist."""
        dirs = [
            self.raw_dir, self.bronze_dir, self.silver_dir, self.gold_dir,
            self.quarantine_dir, self.logs_dir, self.reports_dir
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "ETLConfig":
        """Reads overrides from environment variables and returns a new config instance."""
        config = cls()
        
        # Override fields if environment variables are present
        if "ETL_BATCH_SIZE" in os.environ:
            config.batch_size = int(os.environ["ETL_BATCH_SIZE"])
        if "ETL_RANDOM_SEED" in os.environ:
            config.random_seed = int(os.environ["ETL_RANDOM_SEED"])
        if "ETL_LOG_LEVEL" in os.environ:
            config.log_level = os.environ["ETL_LOG_LEVEL"]
        if "ETL_VALIDATE_FK" in os.environ:
            config.validate_fk = os.environ["ETL_VALIDATE_FK"].lower() in ("true", "1", "yes")
        if "ETL_VALIDATE_PK" in os.environ:
            config.validate_pk = os.environ["ETL_VALIDATE_PK"].lower() in ("true", "1", "yes")
        if "ETL_NULL_THRESHOLD" in os.environ:
            config.null_threshold = float(os.environ["ETL_NULL_THRESHOLD"])
        if "ETL_DUPLICATE_THRESHOLD" in os.environ:
            config.duplicate_threshold = float(os.environ["ETL_DUPLICATE_THRESHOLD"])
        if "ETL_OUTPUT_FORMATS" in os.environ:
            config.output_formats = [fmt.strip() for fmt in os.environ["ETL_OUTPUT_FORMATS"].split(",")]
            
        return config

CONFIG = ETLConfig()
