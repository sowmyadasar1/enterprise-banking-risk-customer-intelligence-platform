"""
ETL Cleaning Layer — Removes duplicates, handles nulls, normalizes formats,
standardizes dates, currencies, strings, and categories for Silver layer.
"""

import logging
from typing import Tuple

import pandas as pd
import numpy as np

from src.etl.base import BaseCleaner, PipelineResult

logger = logging.getLogger(__name__)


class DataCleaner(BaseCleaner):
    """
    Cleans datasets by handling nulls, duplicates, outliers, and normalizing data types.
    """

    def clean(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, PipelineResult]:
        """
        Main entry point for cleaning a dataset.

        Args:
            df (pd.DataFrame): The input DataFrame.
            dataset_name (str): The name of the dataset.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, PipelineResult]: Cleaned DataFrame, rejected DataFrame, and result metadata.
        """
        logger.info(f"Starting cleaning process for dataset: {dataset_name}")

        # Assume first column is PK if not specified, or we look for 'id'
        pk_col = next(
            (col for col in df.columns if col.endswith("_id") or col == "id"),
            df.columns[0],
        )

        clean_df, rejected_dupes = self._remove_duplicates(df, pk_col)
        clean_df = self._handle_nulls(clean_df, dataset_name)
        clean_df = self._normalize_strings(clean_df)
        clean_df = self._standardize_dates(clean_df)
        clean_df = self._normalize_categories(clean_df, dataset_name)
        clean_df = self._clip_outliers(clean_df)
        clean_df, rejected_emails = self._validate_emails(clean_df)

        rejected_df = pd.concat([rejected_dupes, rejected_emails]).drop_duplicates()

        records_processed = len(clean_df)
        records_rejected = len(rejected_df)

        result = PipelineResult(
            success=True,
            records_in=len(df),
            records_out=records_processed,
            records_rejected=records_rejected,
            stage="clean",
        )
        logger.info(
            f"Finished cleaning {dataset_name}. Processed: {records_processed}, Rejected: {records_rejected}"
        )
        return clean_df, rejected_df, result

    def _remove_duplicates(
        self, df: pd.DataFrame, pk_col: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Deduplicate on PK, quarantine dupes."""
        if pk_col not in df.columns:
            return df, pd.DataFrame(columns=df.columns)

        is_duplicate = df.duplicated(subset=[pk_col], keep="first")
        rejected_df = df[is_duplicate].copy()
        clean_df = df[~is_duplicate].copy()
        return clean_df, rejected_df

    def _handle_nulls(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """
        Fill or drop based on column type:
        - Numeric columns → fill with median
        - String/categorical columns → fill with 'Unknown'
        - Date columns → forward-fill
        """
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].ffill()
            else:
                df[col] = df[col].fillna("Unknown")
        return df

    def _normalize_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip whitespace, title-case names, lower-case emails."""
        df = df.copy()
        string_cols = df.select_dtypes(include=["object", "string"]).columns

        title_case_targets = ["first_name", "last_name", "city", "state"]

        for col in string_cols:
            if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(str).str.strip()
                if any(target in col.lower() for target in title_case_targets):
                    df[col] = df[col].str.title()
                elif "email" in col.lower():
                    df[col] = df[col].str.lower()
        return df

    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse all *_date, *_at columns to ISO 8601 datetime, coerce errors to NaT."""
        df = df.copy()
        date_cols = [
            col for col in df.columns if col.endswith("_date") or col.endswith("_at")
        ]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
        return df

    def _normalize_categories(
        self, df: pd.DataFrame, dataset_name: str
    ) -> pd.DataFrame:
        """
        Standardize known categoricals:
        - status: uppercase
        - gender: 'M'/'F'/'Other' → 'Male'/'Female'/'Other'
        - boolean columns: ensure True/False (not 1/0)
        """
        df = df.copy()
        for col in df.columns:
            col_lower = col.lower()
            if col_lower == "status":
                df[col] = df[col].astype(str).str.upper()
            elif col_lower == "gender":
                mapping = {
                    "M": "Male",
                    "F": "Female",
                    "OTHER": "Other",
                    "UNKNOWN": "Unknown",
                }
                df[col] = df[col].astype(str).str.upper().map(mapping).fillna("Unknown")
            elif pd.api.types.is_bool_dtype(df[col]) or (
                set(df[col].dropna().unique()).issubset({0, 1, 0.0, 1.0, "0", "1"})
            ):
                if len(set(df[col].dropna().unique())) <= 2:
                    df[col] = df[col].astype(bool)
        return df

    def _clip_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """For numeric columns, clip values beyond 3 std devs (log warning, don't reject)."""
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Exclude ID columns from outlier clipping
            if not (col.endswith("_id") or col == "id"):
                mean = df[col].mean()
                std = df[col].std()
                if not pd.isna(std) and std > 0:
                    lower_bound = mean - (3 * std)
                    upper_bound = mean + (3 * std)
                    outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                    if outliers_mask.any():
                        logger.warning(
                            f"Clipping {outliers_mask.sum()} outliers in column {col}"
                        )
                        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        return df

    def _validate_emails(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Regex validate emails if column present, quarantine invalid."""
        email_cols = [col for col in df.columns if "email" in col.lower()]
        if not email_cols:
            return df, pd.DataFrame(columns=df.columns)

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        rejected_mask = pd.Series(False, index=df.index)

        for col in email_cols:
            # Check for emails that don't match the regex and aren't 'unknown' or empty
            invalid_format = ~df[col].astype(str).str.match(email_regex, na=False)
            is_not_unknown = df[col].astype(str).str.lower() != "unknown"
            is_not_empty = df[col].astype(str) != ""

            invalid_emails = invalid_format & is_not_unknown & is_not_empty
            rejected_mask = rejected_mask | invalid_emails

        rejected_df = df[rejected_mask].copy()
        clean_df = df[~rejected_mask].copy()
        return clean_df, rejected_df
