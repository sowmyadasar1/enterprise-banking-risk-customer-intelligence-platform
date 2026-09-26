"""
ETL Utilities — Shared helpers for the ETL pipeline.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd


def save_parquet(df: pd.DataFrame, path: Union[str, Path]) -> None:
    """
    Saves a DataFrame as a parquet file with snappy compression, creating parent dirs.

    Args:
        df: The pandas DataFrame to save.
        path: Path to the output parquet file.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, engine="pyarrow", compression="snappy", index=False)


def save_csv(df: pd.DataFrame, path: Union[str, Path]) -> None:
    """
    Saves a DataFrame as a CSV file without index, creating parent dirs.

    Args:
        df: The pandas DataFrame to save.
        path: Path to the output CSV file.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def load_parquet(path: Union[str, Path]) -> pd.DataFrame:
    """
    Loads a parquet file into a pandas DataFrame.

    Args:
        path: Path to the input parquet file.

    Returns:
        Loaded DataFrame.
    """
    return pd.read_parquet(path, engine="pyarrow")


def load_csv(path: Union[str, Path]) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame.

    Args:
        path: Path to the input CSV file.

    Returns:
        Loaded DataFrame.
    """
    return pd.read_csv(path)


def quarantine_records(
    df: pd.DataFrame, reason: str, dataset_name: str, config: Any
) -> None:
    """
    Saves rejected records to the quarantine directory with an attached reason.

    Args:
        df: The pandas DataFrame containing rejected records.
        reason: The reason for rejection.
        dataset_name: Name of the dataset.
        config: ETLConfig object that contains directory paths.
    """
    if df.empty:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = config.quarantine_dir / f"{dataset_name}_{timestamp}_rejected.csv"

    # Add reason column
    df = df.copy()
    df["_quarantine_reason"] = reason

    save_csv(df, out_path)


def get_dataset_paths(config: Any, layer: str) -> Dict[str, Path]:
    """
    Returns a dictionary of dataset_name -> path for a given layer.

    Args:
        config: ETLConfig object containing layer directory paths.
        layer: The layer name (e.g., 'raw', 'bronze', 'silver', 'gold').

    Returns:
        Dictionary mapping dataset name to its file path.
    """
    layer_dir_map = {
        "raw": config.raw_dir,
        "bronze": config.bronze_dir,
        "silver": config.silver_dir,
        "gold": config.gold_dir,
    }

    layer_dir = layer_dir_map.get(layer.lower())
    if not layer_dir or not layer_dir.exists():
        return {}

    paths = {}
    for p in layer_dir.glob("*"):
        if p.is_file():
            # Use stem as dataset name for simplicity
            dataset_name = p.stem
            paths[dataset_name] = p

    return paths


def hash_column(series: pd.Series) -> pd.Series:
    """
    Generates a SHA-256 hash for each value in a pandas Series.

    Args:
        series: Pandas Series containing values to hash.

    Returns:
        Pandas Series containing SHA-256 hashes.
    """

    def _hash(val: Any) -> Optional[str]:
        if pd.isna(val):
            return None
        s = str(val).encode("utf-8")
        return hashlib.sha256(s).hexdigest()

    return series.apply(_hash)


def safe_cast_datetime(series: pd.Series, fmt: Optional[str] = None) -> pd.Series:
    """
    Robust datetime parsing with coercion for invalid values.

    Args:
        series: Pandas Series containing datetime strings.
        fmt: Optional datetime format string.

    Returns:
        Pandas Series converted to datetime.
    """
    if fmt:
        return pd.to_datetime(series, format=fmt, errors="coerce")
    return pd.to_datetime(series, errors="coerce")


def normalize_string(s: Any) -> Optional[str]:
    """
    Strips whitespace, converts to lowercase, and removes extra spaces.

    Args:
        s: Input string.

    Returns:
        Normalized string or None if input is null.
    """
    if pd.isna(s):
        return None
    s = str(s).strip().lower()
    return re.sub(r"\s+", " ", s)


def standardize_phone(phone: Any) -> Optional[str]:
    """
    Normalizes a phone number to an E.164-like format by keeping only digits.
    Prepends '+' if a country code is assumed, otherwise just returns digits.

    Args:
        phone: Input phone number string.

    Returns:
        Standardized phone string.
    """
    if pd.isna(phone):
        return None
    phone_str = str(phone)
    digits = re.sub(r"\D", "", phone_str)

    if not digits:
        return None

    # Assume US if 10 digits
    if len(digits) == 10:
        return f"+1{digits}"

    # Generic prefix for anything else
    return f"+{digits}"
