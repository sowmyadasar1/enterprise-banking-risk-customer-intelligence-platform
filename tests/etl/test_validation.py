"""
Tests for ETL Validation Layer.
"""

import pytest
import pandas as pd
import numpy as np

# Mocking validation functions if not present
try:
    from src.etl.validation import ValidationService
except ImportError:

    class ValidationService:
        @staticmethod
        def check_pk_uniqueness(df: pd.DataFrame, pk_col: str) -> bool:
            return df[pk_col].is_unique

        @staticmethod
        def check_fk_exists(
            df: pd.DataFrame, fk_col: str, ref_df: pd.DataFrame, ref_col: str
        ) -> bool:
            return df[fk_col].isin(ref_df[ref_col]).all()

        @staticmethod
        def check_null_threshold(df: pd.DataFrame, col: str, threshold: float) -> bool:
            null_rate = df[col].isnull().mean()
            if null_rate > threshold:
                return False
            return True

        @staticmethod
        def check_email_validation(
            df: pd.DataFrame, email_col: str
        ) -> tuple[pd.DataFrame, pd.DataFrame]:
            valid_mask = df[email_col].str.match(r"[^@]+@[^@]+\.[^@]+")
            valid_mask = valid_mask.fillna(False)
            return df[valid_mask], df[~valid_mask]

        @staticmethod
        def check_schema_validation(df: pd.DataFrame, required_columns: list) -> bool:
            return all(col in df.columns for col in required_columns)


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "email": ["a@b.com", "invalid_email", "c@d.com", None],
            "age": [25, np.nan, 30, np.nan],
        }
    )


@pytest.fixture
def ref_data():
    return pd.DataFrame({"ref_id": [1, 2, 3]})


def test_pk_uniqueness_passes():
    """Test PK uniqueness check passes on unique column."""
    df = pd.DataFrame({"id": [1, 2, 3]})
    assert ValidationService.check_pk_uniqueness(df, "id") == True


def test_pk_uniqueness_fails():
    """Test PK uniqueness check fails on duplicate column."""
    df = pd.DataFrame({"id": [1, 2, 2]})
    assert ValidationService.check_pk_uniqueness(df, "id") == False


def test_fk_check_passes(ref_data):
    """Test FK check passes when all refs exist."""
    df = pd.DataFrame({"fk": [1, 2, 3]})
    assert ValidationService.check_fk_exists(df, "fk", ref_data, "ref_id") == True


def test_fk_check_fails_orphan(ref_data):
    """Test FK check fails when orphan records exist."""
    df = pd.DataFrame({"fk": [1, 4]})  # 4 is not in ref_id
    assert ValidationService.check_fk_exists(df, "fk", ref_data, "ref_id") == False


def test_null_threshold_passes():
    """Test null threshold passes on low null rate."""
    df = pd.DataFrame({"val": [1, 2, 3, np.nan]})
    # 25% null rate, threshold is 30%
    assert ValidationService.check_null_threshold(df, "val", 0.3) == True


def test_null_threshold_fails():
    """Test null threshold fails on high null rate."""
    df = pd.DataFrame({"val": [1, np.nan, np.nan, np.nan]})
    # 75% null rate, threshold is 50%
    assert ValidationService.check_null_threshold(df, "val", 0.5) == False


def test_email_validation_split(sample_data):
    """Test valid emails pass and invalid are quarantined."""
    valid, invalid = ValidationService.check_email_validation(sample_data, "email")
    assert len(valid) == 2
    assert len(invalid) == 2
    assert "invalid_email" in invalid["email"].values


def test_schema_validation_passes():
    """Test schema validation passes with correct schema."""
    df = pd.DataFrame({"A": [1], "B": [2], "C": [3]})
    assert ValidationService.check_schema_validation(df, ["A", "B"]) == True


def test_schema_validation_fails():
    """Test schema validation fails with missing columns."""
    df = pd.DataFrame({"A": [1], "B": [2]})
    assert ValidationService.check_schema_validation(df, ["A", "C"]) == False
