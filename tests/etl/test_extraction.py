"""
Tests for ETL Extraction Layer.
"""
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.etl.extract import CsvExtractor, ParquetExtractor, DataExtractor

@pytest.fixture
def sample_df():
    """Fixture providing a sample DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })

def test_csv_extractor_valid_file(tmp_path, sample_df):
    """Test CsvExtractor successfully extracts data from a valid CSV."""
    file_path = tmp_path / "test.csv"
    sample_df.to_csv(file_path, index=False)
    
    extractor = CsvExtractor()
    df = extractor.extract(str(file_path))
    
    assert not df.empty
    assert len(df) == 3
    assert list(df.columns) == ["id", "name"]

def test_parquet_extractor_valid_file(tmp_path, sample_df):
    """Test ParquetExtractor successfully extracts data from a valid Parquet file."""
    file_path = tmp_path / "test.parquet"
    sample_df.to_parquet(file_path, index=False)
    
    extractor = ParquetExtractor()
    df = extractor.extract(str(file_path))
    
    assert not df.empty
    assert len(df) == 3
    assert "name" in df.columns

def test_csv_extractor_missing_file():
    """Test CsvExtractor raises FileNotFoundError for missing files."""
    extractor = CsvExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("non_existent_file.csv")

def test_parquet_extractor_missing_file():
    """Test ParquetExtractor raises FileNotFoundError for missing files."""
    extractor = ParquetExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("non_existent_file.parquet")

def test_csv_extractor_empty_file(tmp_path):
    """Test CsvExtractor returns an empty DataFrame and warns on empty file."""
    file_path = tmp_path / "empty.csv"
    pd.DataFrame().to_csv(file_path, index=False)
    
    extractor = CsvExtractor()
    with pytest.warns(UserWarning):
        df = extractor.extract(str(file_path))
    
    assert df.empty

def test_parquet_extractor_empty_file(tmp_path):
    """Test ParquetExtractor returns an empty DataFrame and warns on empty file."""
    file_path = tmp_path / "empty.parquet"
    pd.DataFrame().to_parquet(file_path, index=False)
    
    extractor = ParquetExtractor()
    with pytest.warns(UserWarning):
        df = extractor.extract(str(file_path))
    
    assert df.empty

def test_data_extractor_csv(tmp_path, sample_df):
    """Test DataExtractor dispatches to CsvExtractor correctly."""
    from src.etl.config import ETLConfig
    raw_dir = tmp_path / "raw"
    customer_dir = raw_dir / "customers"
    customer_dir.mkdir(parents=True)
    file_path = customer_dir / "customers.csv"
    sample_df.to_csv(file_path, index=False)
    
    config = ETLConfig()
    config.raw_dir = raw_dir
    
    extractor = DataExtractor(config)
    df, result = extractor.extract_dataset("customers", prefer_parquet=False)
    
    assert result.success
    assert len(df) == 3

@patch("src.etl.extract.ParquetExtractor.extract")
def test_data_extractor_mocked(mock_extract, tmp_path):
    """Test DataExtractor extract_dataset uses mocked file paths."""
    from src.etl.config import ETLConfig
    mock_extract.return_value = pd.DataFrame({"id": [99]})
    
    raw_dir = tmp_path / "raw"
    accounts_dir = raw_dir / "finance"
    accounts_dir.mkdir(parents=True)
    (accounts_dir / "accounts.parquet").touch()
    
    config = ETLConfig()
    config.raw_dir = raw_dir
    
    extractor = DataExtractor(config)
    df, result = extractor.extract_dataset("accounts", prefer_parquet=True)
    
    assert result.success
    assert len(df) == 1
    assert df["id"].iloc[0] == 99
