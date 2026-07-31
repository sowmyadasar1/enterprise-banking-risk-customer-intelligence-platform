"""
Generates synthetic data for Customer Segments.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from typing import Any

def generate_customer_segments(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic customer segments.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'customers' DataFrame.
        
    Returns:
        pd.DataFrame: A dataframe of customer segments.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    
    customers_df = dependencies.get("customers")
    segments = ["Retail", "Wealth", "Corporate", "Small Business", "Student"]
    weights = [0.5, 0.1, 0.15, 0.2, 0.05]
    
    data = []
    for _ in range(n):
        if customers_df is not None and not customers_df.empty:
            cust_id = customers_df.sample(1).iloc[0].get("customer_id", str(uuid.uuid4()))
        else:
            cust_id = str(uuid.uuid4())
            
        data.append({
            "segment_id": str(uuid.uuid4()),
            "customer_id": cust_id,
            "segment_name": np.random.choice(segments, p=weights),
            "assignment_date": fake.date_time_between(start_date="-5y", end_date="now"),
            "is_active": True
        })
        
    return pd.DataFrame(data)
