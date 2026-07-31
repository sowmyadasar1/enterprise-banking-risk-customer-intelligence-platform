"""Data generator for Customer Employment."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_customer_employment(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic customer employment data.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers'.
        
    Returns:
        pd.DataFrame: DataFrame containing generated customer employment.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()
    
    customers_df = dependencies.get('customers')
    if customers_df is None or customers_df.empty:
        raise ValueError("Customers dataframe must be provided as a dependency.")
        
    customer_ids = customers_df['customer_id'].tolist()
    
    data = []
    for _ in range(n):
        data.append({
            "employment_id": fake.unique.uuid4(),
            "customer_id": random.choice(customer_ids),
            "employer_name": fake.company(),
            "occupation": fake.job(),
            "annual_income": round(random.uniform(30000, 300000), 2),
            "employment_status": random.choice(["Employed", "Self-Employed", "Unemployed", "Retired"]),
            "start_date": fake.date_between(start_date="-20y", end_date="today")
        })
    return pd.DataFrame(data)
