"""
ETL Logging — Structured logging for the Enterprise Banking ETL Pipeline.
"""

import json
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


def get_pipeline_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Creates and returns a configured logger with StreamHandler and RotatingFileHandler.

    Args:
        name: Name of the logger
        log_file: Optional path to the log file. If None, uses a default in logs/ dir.

    Returns:
        logging.Logger configured for the ETL pipeline.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times if logger already exists
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
    )

    # Stream Handler
    try:
        import colorlog

        stream_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
        )
    except ImportError:
        stream_formatter = formatter

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # File Handler
    if not log_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True, parents=True)
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = str(log_dir / f"etl_{name}_{date_str}.log")

    # Ensure log file directory exists
    Path(log_file).parent.mkdir(exist_ok=True, parents=True)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class ETLTimer:
    """Context manager for timing ETL operations and logging the duration."""

    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time: float = 0.0

    def __enter__(self) -> "ETLTimer":
        self.start_time = time.time()
        self.logger.info(f"Started: {self.operation_name}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration = time.time() - self.start_time
        if exc_type:
            self.logger.error(
                f"Failed: {self.operation_name} (Duration: {duration:.2f}s) - Error: {exc_val}"
            )
        else:
            self.logger.info(
                f"Completed: {self.operation_name} (Duration: {duration:.2f}s)"
            )


class PipelineAuditLogger:
    """Writes JSON-lines audit events to an audit log file."""

    def __init__(self, audit_file: str = "logs/audit.jsonl"):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(exist_ok=True, parents=True)

    def log_event(
        self,
        stage: str,
        dataset: str,
        records_in: int,
        records_out: int,
        rejected: int,
        status: str,
        duration_seconds: float,
    ) -> None:
        """Log a single audit event."""
        event: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "dataset": dataset,
            "records_in": records_in,
            "records_out": records_out,
            "rejected": rejected,
            "status": status,
            "duration_seconds": duration_seconds,
        }

        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
