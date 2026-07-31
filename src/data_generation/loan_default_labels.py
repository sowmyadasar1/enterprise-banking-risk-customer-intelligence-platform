"""
Generates synthetic data for Loan Default Labels.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta
from typing import Any

def generate_loan_default_labels(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic loan default labels.
    
    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'loans' DataFrame.
        
    Returns:
        pd.DataFrame: A dataframe of loan default labels.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    
    loans_df = dependencies.get("loans")
    
    data = []
    for _ in range(n):
        if loans_df is not None and not loans_df.empty:
            sample_loan = loans_df.sample(1).iloc[0]
            loan_id = sample_loan.get("loan_id", str(uuid.uuid4()))
            loan_amount = sample_loan.get("loan_amount", random.uniform(5000, 1000000))
        else:
            loan_id = str(uuid.uuid4())
            loan_amount = random.uniform(5000, 1000000)
            
        is_default = np.random.choice([True, False], p=[0.05, 0.95])
        amount_defaulted = round(loan_amount * random.uniform(0.1, 1.0), 2) if is_default else 0.0
        recovery_amount = round(amount_defaulted * random.uniform(0.0, 0.8), 2) if is_default else 0.0
        
        data.append({
            "label_id": str(uuid.uuid4()),
            "loan_id": loan_id,
            "is_default": is_default,
            "default_date": fake.date_time_between(start_date="-5y", end_date="now") if is_default else None,
            "amount_defaulted": amount_defaulted,
            "recovery_amount": recovery_amount
        })
        
    return pd.DataFrame(data)
