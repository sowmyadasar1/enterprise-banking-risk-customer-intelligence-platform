"""Data generator for Customer Addresses."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_customer_addresses(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic customer address data.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers'.
        
    Returns:
        pd.DataFrame: DataFrame containing generated customer addresses.
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
        customer_id = random.choice(customer_ids)
        data.append({
            "address_id": fake.unique.uuid4(),
            "customer_id": customer_id,
            "address_type": random.choice(["Home", "Work", "Mailing"]),
            "street_address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postal_code": fake.zipcode(),
            "country": "USA",
            "is_primary": random.choice([True, False])
        })
    return pd.DataFrame(data)
