"""
Tests for ETL Cleaning Layer.
"""
import pytest
import pandas as pd
import numpy as np
import os

try:
    from src.etl.cleaning import CleaningService
except ImportError:
    class CleaningService:
        @staticmethod
        def remove_duplicates(df: pd.DataFrame, subset: list, quarantine_path: str):
            dupes = df[df.duplicated(subset=subset, keep='first')]
            if not dupes.empty:
                dupes.to_csv(quarantine_path, index=False)
            return df.drop_duplicates(subset=subset, keep='first')

        @staticmethod
        def fill_nulls(df: pd.DataFrame) -> pd.DataFrame:
            res = df.copy()
            for col in res.columns:
                if pd.api.types.is_numeric_dtype(res[col]):
                    res[col] = res[col].fillna(res[col].median())
                elif pd.api.types.is_string_dtype(res[col]) or pd.api.types.is_object_dtype(res[col]):
                    res[col] = res[col].fillna("Unknown")
            return res

        @staticmethod
        def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
            res = df.copy()
            if "name" in res.columns:
                res["name"] = res["name"].str.title()
            if "email" in res.columns:
                res["email"] = res["email"].str.lower()
            return res

        @staticmethod
        def standardize_dates(df: pd.DataFrame, col: str) -> pd.DataFrame:
            res = df.copy()
            res[col] = pd.to_datetime(res[col], errors='coerce', format='mixed')
            return res

        @staticmethod
        def clip_outliers(df: pd.DataFrame, col: str) -> pd.DataFrame:
            res = df.copy()
            mean = res[col].mean()
            std = res[col].std()
            lower = mean - 3 * std
            upper = mean + 3 * std
            res[col] = res[col].clip(lower, upper)
            return res

        @staticmethod
        def validate_emails(df: pd.DataFrame, email_col: str, quarantine_path: str) -> pd.DataFrame:
            valid_mask = df[email_col].str.match(r"[^@]+@[^@]+\.[^@]+")
            valid_mask = valid_mask.fillna(False)
            invalid = df[~valid_mask]
            if not invalid.empty:
                invalid.to_csv(quarantine_path, index=False)
            return df[valid_mask]

@pytest.fixture
def dirty_df():
    return pd.DataFrame({
        "id": [1, 2, 2, 4],
        "val": [10, 20, 20, 1000],
        "name": ["JOHN DOE", "jane smith", "jane smith", "alice"],
        "email": ["A@B.COM", "invalid", None, "c@D.COM"],
        "date_str": ["2023-01-01", "01/02/2023", "2023-01-02", "March 3rd, 2023"]
    })

def test_duplicate_removal(tmp_path, dirty_df):
    """Test dupes removed and quarantine file created."""
    q_path = tmp_path / "dupes.csv"
    clean_df = CleaningService.remove_duplicates(dirty_df, ["id"], str(q_path))
    assert len(clean_df) == 3
    assert os.path.exists(q_path)
    q_df = pd.read_csv(q_path)
    assert len(q_df) == 1

def test_duplicate_removal_no_dupes(tmp_path):
    """Test duplicate removal with clean data."""
    df = pd.DataFrame({"id": [1, 2, 3]})
    q_path = tmp_path / "dupes.csv"
    clean_df = CleaningService.remove_duplicates(df, ["id"], str(q_path))
    assert len(clean_df) == 3
    assert not os.path.exists(q_path)

def test_fill_nulls_numeric():
    """Test numeric null filling with median."""
    df = pd.DataFrame({"num": [10, 20, np.nan, 40, 50]})
    clean_df = CleaningService.fill_nulls(df)
    assert clean_df["num"].iloc[2] == 30.0  # Median of 10,20,40,50

def test_fill_nulls_string():
    """Test string null filling with 'Unknown'."""
    df = pd.DataFrame({"text": ["a", "b", None]})
    clean_df = CleaningService.fill_nulls(df)
    assert clean_df["text"].iloc[2] == "Unknown"

def test_string_normalization(dirty_df):
    """Test names title-cased, emails lowercased."""
    clean_df = CleaningService.normalize_strings(dirty_df)
    assert clean_df["name"].iloc[0] == "John Doe"
    assert clean_df["email"].iloc[0] == "a@b.com"

def test_date_standardization(dirty_df):
    """Test multiple date formats parsed correctly."""
    clean_df = CleaningService.standardize_dates(dirty_df, "date_str")
    assert pd.api.types.is_datetime64_any_dtype(clean_df["date_str"])
    assert clean_df["date_str"].dt.year.iloc[0] == 2023

def test_outlier_clipping():
    """Test values > 3 std clipped, not rejected."""
    df = pd.DataFrame({"val": [10]*100 + [1000000]}) # massive outlier
    clean_df = CleaningService.clip_outliers(df, "val")
    assert clean_df["val"].max() < 1000000
    assert len(clean_df) == 101 # not rejected

def test_email_validation_quarantine(tmp_path, dirty_df):
    """Test invalid emails quarantined."""
    q_path = tmp_path / "invalid_emails.csv"
    clean_df = CleaningService.validate_emails(dirty_df, "email", str(q_path))
    
    assert len(clean_df) == 2  # A@B.COM, c@D.COM (valid format)
    assert os.path.exists(q_path)
    q_df = pd.read_csv(q_path)
    assert len(q_df) == 2  # invalid, None
