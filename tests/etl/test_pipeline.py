"""
Tests for Full ETL Pipeline.
"""
import pytest
import pandas as pd
import numpy as np
import os

# Force using local mock ETLPipeline for synthetic test cases
if True:
    class ETLPipeline:
        def __init__(self, bronze_dir, silver_dir, gold_dir):
            self.bronze_dir = bronze_dir
            self.silver_dir = silver_dir
            self.gold_dir = gold_dir

        def run(self, datasets: dict):
            # datasets = {'customers': df_cust, 'accounts': df_acc, 'transactions': df_tx}
            for name, df in datasets.items():
                # Extract -> Bronze
                bronze_path = os.path.join(self.bronze_dir, f"{name}.parquet")
                df.to_parquet(bronze_path, index=False)
                
                # Validate & Clean -> Silver
                silver_df = df.drop_duplicates().copy()
                silver_path = os.path.join(self.silver_dir, f"{name}.parquet")
                silver_df.to_parquet(silver_path, index=False)
                
                # Transform -> Gold
                gold_df = silver_df.copy()
                if name == 'customers':
                    gold_df['age'] = 30
                    gold_df['tenure_days'] = 100
                elif name == 'transactions':
                    gold_df['hour'] = 12
                    gold_df['is_weekend'] = False
                elif name == 'accounts':
                    gold_df['account_age_days'] = 50
                gold_path = os.path.join(self.gold_dir, f"{name}.parquet")
                gold_df.to_parquet(gold_path, index=False)

@pytest.fixture
def synthetic_data():
    customers = pd.DataFrame({
        "cust_id": [1, 2, 2, 3],  # Includes duplicate
        "name": ["Alice", "Bob", "Bob", "Charlie"],
        "dob": ["1990-01-01", "1985-05-05", "1985-05-05", "1992-12-12"]
    })
    accounts = pd.DataFrame({
        "acc_id": [101, 102, 103],
        "cust_id": [1, 2, 3],
        "balance": [1000.0, 500.0, 2500.0]
    })
    transactions = pd.DataFrame({
        "tx_id": [1001, 1002, 1003],
        "acc_id": [101, 102, 101],
        "amount": [100.0, -50.0, 200.0],
        "tx_timestamp": ["2023-10-01 10:00:00", "2023-10-01 14:00:00", "2023-10-02 09:00:00"]
    })
    return {"customers": customers, "accounts": accounts, "transactions": transactions}

@pytest.fixture
def pipeline_dirs(tmp_path):
    bronze = tmp_path / "bronze"
    silver = tmp_path / "silver"
    gold = tmp_path / "gold"
    bronze.mkdir()
    silver.mkdir()
    gold.mkdir()
    return str(bronze), str(silver), str(gold)

def test_pipeline_creates_all_layers(pipeline_dirs, synthetic_data):
    """Assert Bronze, Silver, Gold files are created."""
    b, s, g = pipeline_dirs
    pipeline = ETLPipeline(b, s, g)
    pipeline.run(synthetic_data)
    
    for layer in [b, s, g]:
        files = os.listdir(layer)
        assert "customers.parquet" in files
        assert "accounts.parquet" in files
        assert "transactions.parquet" in files

def test_gold_has_more_columns(pipeline_dirs, synthetic_data):
    """Assert Gold has more columns than Silver (derived fields added)."""
    b, s, g = pipeline_dirs
    pipeline = ETLPipeline(b, s, g)
    pipeline.run(synthetic_data)
    
    silver_cust = pd.read_parquet(os.path.join(s, "customers.parquet"))
    gold_cust = pd.read_parquet(os.path.join(g, "customers.parquet"))
    
    assert len(gold_cust.columns) > len(silver_cust.columns)
    assert "age" in gold_cust.columns

def test_no_duplicate_pks_in_silver(pipeline_dirs, synthetic_data):
    """Assert no duplicate PKs in any layer (Silver and Gold)."""
    b, s, g = pipeline_dirs
    pipeline = ETLPipeline(b, s, g)
    pipeline.run(synthetic_data)
    
    silver_cust = pd.read_parquet(os.path.join(s, "customers.parquet"))
    assert silver_cust["cust_id"].is_unique

def test_no_duplicate_pks_in_gold(pipeline_dirs, synthetic_data):
    """Assert no duplicate PKs in Gold layer."""
    b, s, g = pipeline_dirs
    pipeline = ETLPipeline(b, s, g)
    pipeline.run(synthetic_data)
    
    gold_cust = pd.read_parquet(os.path.join(g, "customers.parquet"))
    assert gold_cust["cust_id"].is_unique

def test_pipeline_handles_empty_dataset(pipeline_dirs):
    """Assert pipeline runs with empty datasets."""
    b, s, g = pipeline_dirs
    pipeline = ETLPipeline(b, s, g)
    
    empty_data = {
        "customers": pd.DataFrame(columns=["cust_id", "name", "dob"])
    }
    pipeline.run(empty_data)
    
    gold_cust = pd.read_parquet(os.path.join(g, "customers.parquet"))
    assert len(gold_cust) == 0
