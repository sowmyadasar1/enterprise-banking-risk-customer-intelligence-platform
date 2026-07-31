"""
Generates synthetic data for Fraud Cases / Labels.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from typing import Any

def generate_fraud_cases(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic fraud cases.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'transactions' DataFrame to link FKs.
        
    Returns:
        pd.DataFrame: A dataframe of fraud cases.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    
    transactions_df = dependencies.get("transactions")
    
    data = []
    for _ in range(n):
        if transactions_df is not None and not transactions_df.empty:
            sample_tx = transactions_df.sample(1).iloc[0]
            tx_id = sample_tx.get("transaction_id", str(uuid.uuid4()))
            cust_id = sample_tx.get("customer_id", str(uuid.uuid4()))
        else:
            tx_id = str(uuid.uuid4())
            cust_id = str(uuid.uuid4())
            
        data.append({
            "case_id": str(uuid.uuid4()),
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "report_date": fake.date_time_between(start_date="-2y", end_date="now"),
            "fraud_type": random.choice(["Identity Theft", "Card Skimming", "Account Takeover", "Phishing", "Friendly Fraud"]),
            "amount_involved": round(random.uniform(50.0, 15000.0), 2),
            "status": random.choice(["Open", "Under Investigation", "Resolved", "Closed - False Positive"])
        })
        
    return pd.DataFrame(data)
