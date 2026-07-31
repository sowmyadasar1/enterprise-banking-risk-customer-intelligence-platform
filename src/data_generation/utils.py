import os
import json
import logging
from typing import List
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

def get_base_dir() -> Path:
    """Get the base directory of the project."""
    # Assuming this file is at src/data_generation/utils.py
    # Project root would be ../../
    return Path(__file__).resolve().parent.parent.parent

def save_dataset(df: pd.DataFrame, category: str, name: str, formats: List[str] = ["csv", "parquet", "json"]):
    """
    Save a pandas DataFrame to specified formats in the correct data/raw/ subdirectory.
    
    Args:
        df: The pandas DataFrame to save.
        category: The subdirectory category (e.g., 'customers', 'finance', 'transactions').
        name: The base name of the file (e.g., 'customer_profiles').
        formats: List of formats to save as (e.g., ['csv', 'parquet', 'json']).
    """
    base_dir = get_base_dir()
    output_dir = base_dir / "data" / "raw" / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for fmt in formats:
        fmt = fmt.lower()
        if fmt == "csv":
            file_path = output_dir / f"{name}.csv"
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {name} to {file_path}")
        elif fmt == "parquet":
            file_path = output_dir / f"{name}.parquet"
            df.to_parquet(file_path, index=False)
            logger.info(f"Saved {name} to {file_path}")
        elif fmt == "json":
            file_path = output_dir / f"{name}.json"
            df.to_json(file_path, orient="records", indent=2)
            logger.info(f"Saved {name} to {file_path}")
        else:
            logger.warning(f"Unsupported format: {fmt}")

def generate_metadata(df: pd.DataFrame, category: str, name: str, description: str = ""):
    """
    Generate metadata/schema JSON files for a dataset.
    
    Args:
        df: The pandas DataFrame.
        category: The subdirectory category.
        name: The base name of the dataset.
        description: An optional description of the dataset.
    """
    base_dir = get_base_dir()
    output_dir = base_dir / "data" / "raw" / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    schema = {}
    for col, dtype in df.dtypes.items():
        schema[col] = str(dtype)
        
    metadata = {
        "dataset_name": name,
        "category": category,
        "description": description,
        "row_count": len(df),
        "column_count": len(df.columns),
        "schema": schema
    }
    
    file_path = output_dir / f"{name}_metadata.json"
    with open(file_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    logger.info(f"Saved metadata for {name} to {file_path}")
