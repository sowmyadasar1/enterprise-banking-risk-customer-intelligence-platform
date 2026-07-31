"""Data generator for Beneficiaries."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_beneficiaries(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic beneficiaries data.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers'.
        
    Returns:
        pd.DataFrame: DataFrame containing generated beneficiaries.
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
            "beneficiary_id": str(fake.unique.uuid4()),
            "customer_id": random.choice(customer_ids),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "relationship": random.choice(["Spouse", "Child", "Parent", "Sibling", "Other"]),
            "allocation_percentage": round(random.uniform(1.0, 100.0), 2),
            "contact_number": fake.phone_number(),
            "email": fake.email()
        })
    return pd.DataFrame(data)
