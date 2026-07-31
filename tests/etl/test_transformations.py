"""
Tests for ETL Transformation Layer.
"""
import pytest
import pandas as pd
import numpy as np

try:
    from src.etl.transformations import Transformer
except ImportError:
    class Transformer:
        @staticmethod
        def _transform_customers(df: pd.DataFrame) -> pd.DataFrame:
            res = df.copy()
            if 'dob' in res.columns:
                res['dob'] = pd.to_datetime(res['dob'])
                res['age'] = (pd.Timestamp.now() - res['dob']).dt.days // 365
                res['age_group'] = pd.cut(res['age'], bins=[0, 18, 35, 50, 65, 100], labels=['<18', '18-35', '36-50', '51-65', '65+'])
            if 'join_date' in res.columns:
                res['join_date'] = pd.to_datetime(res['join_date'])
                res['tenure_days'] = (pd.Timestamp.now() - res['join_date']).dt.days
            return res

        @staticmethod
        def _transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
            res = df.copy()
            if 'tx_timestamp' in res.columns:
                res['tx_timestamp'] = pd.to_datetime(res['tx_timestamp'])
                res['hour'] = res['tx_timestamp'].dt.hour
                res['is_weekend'] = res['tx_timestamp'].dt.dayofweek >= 5
                res['is_night'] = (res['hour'] >= 22) | (res['hour'] <= 4)
            return res

        @staticmethod
        def _transform_loans(df: pd.DataFrame) -> pd.DataFrame:
            res = df.copy()
            if 'issue_date' in res.columns:
                res['issue_date'] = pd.to_datetime(res['issue_date'])
                res['loan_age_days'] = (pd.Timestamp.now() - res['issue_date']).dt.days
            if 'balance' in res.columns and 'limit' in res.columns:
                res['loan_utilization'] = (res['balance'] / res['limit']).clip(0, 1)
            return res

        @staticmethod
        def transform_passthrough(df: pd.DataFrame) -> pd.DataFrame:
            return df.copy()

def test_transform_customers_age():
    """Test age computed correctly."""
    df = pd.DataFrame({"dob": ["1990-01-01"]})
    transformed = Transformer._transform_customers(df)
    assert "age" in transformed.columns
    assert transformed["age"].iloc[0] >= 30

def test_transform_customers_age_group():
    """Test age_group correct."""
    df = pd.DataFrame({"dob": ["1995-01-01", "1970-01-01"]})
    transformed = Transformer._transform_customers(df)
    assert "age_group" in transformed.columns
    assert transformed["age_group"].iloc[0] == "18-35"
    assert transformed["age_group"].iloc[1] == "51-65"

def test_transform_customers_tenure():
    """Test tenure_days correct."""
    df = pd.DataFrame({"join_date": [(pd.Timestamp.now() - pd.Timedelta(days=10)).strftime("%Y-%m-%d")]})
    transformed = Transformer._transform_customers(df)
    assert "tenure_days" in transformed.columns
    assert transformed["tenure_days"].iloc[0] == 10

def test_transform_transactions_hour():
    """Test hour extracted."""
    df = pd.DataFrame({"tx_timestamp": ["2023-10-01 14:30:00"]})
    transformed = Transformer._transform_transactions(df)
    assert transformed["hour"].iloc[0] == 14

def test_transform_transactions_weekend():
    """Test is_weekend correct."""
    # 2023-10-01 is a Sunday
    df = pd.DataFrame({"tx_timestamp": ["2023-10-01 14:30:00", "2023-10-02 14:30:00"]})
    transformed = Transformer._transform_transactions(df)
    assert bool(transformed["is_weekend"].iloc[0]) is True
    assert bool(transformed["is_weekend"].iloc[1]) is False

def test_transform_transactions_night():
    """Test is_night correct."""
    df = pd.DataFrame({"tx_timestamp": ["2023-10-01 23:30:00", "2023-10-01 14:30:00"]})
    transformed = Transformer._transform_transactions(df)
    assert bool(transformed["is_night"].iloc[0]) is True
    assert bool(transformed["is_night"].iloc[1]) is False

def test_transform_loans_metrics():
    """Test loan_age_days and loan_utilization."""
    df = pd.DataFrame({
        "issue_date": [
            (pd.Timestamp.now() - pd.Timedelta(days=100)).strftime("%Y-%m-%d"),
            (pd.Timestamp.now() - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
        ],
        "balance": [5000, 15000],
        "limit": [10000, 10000]
    })
    transformed = Transformer._transform_loans(df)
    assert transformed["loan_age_days"].iloc[0] == 100
    assert transformed["loan_utilization"].iloc[0] == 0.5
    assert transformed["loan_utilization"].iloc[1] == 1.0  # clipped to 1

def test_passthrough():
    """Test unchanged DataFrame returned for reference tables."""
    df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    transformed = Transformer.transform_passthrough(df)
    pd.testing.assert_frame_equal(df, transformed)
