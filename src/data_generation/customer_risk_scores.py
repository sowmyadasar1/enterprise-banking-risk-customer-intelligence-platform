"""
Generates synthetic data for Customer Risk Scores.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from typing import Any

def generate_customer_risk_scores(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic customer risk scores.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'customers' DataFrame.
        
    Returns:
        pd.DataFrame: A dataframe of customer risk scores.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    
    customers_df = dependencies.get("customers")
    
    data = []
    for _ in range(n):
        if customers_df is not None and not customers_df.empty:
            cust_id = customers_df.sample(1).iloc[0].get("customer_id", str(uuid.uuid4()))
        else:
            cust_id = str(uuid.uuid4())
            
        # Normal distribution centered around 500
        score = int(np.clip(np.random.normal(500, 150), 300, 850))
        
        if score < 580:
            category = "High"
        elif score < 670:
            category = "Medium"
        elif score < 740:
            category = "Low"
        else:
            category = "Very Low"
            
        data.append({
            "risk_id": str(uuid.uuid4()),
            "customer_id": cust_id,
            "risk_score": score,
            "risk_category": category,
            "assessment_date": fake.date_time_between(start_date="-1y", end_date="now"),
            "model_version": "v2.1.0"
        })
        
    return pd.DataFrame(data)
