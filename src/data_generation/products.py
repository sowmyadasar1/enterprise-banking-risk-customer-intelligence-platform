"""Data generator for Products."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_products(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic products data.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets.
        
    Returns:
        pd.DataFrame: DataFrame containing generated products.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()
    
    product_types = [
        "Checking Account", "Savings Account", "Credit Card", 
        "Personal Loan", "Mortgage", "Auto Loan", 
        "Investment Account", "Business Checking"
    ]
    
    data = []
    for i in range(min(n, len(product_types) * 3)):
        p_type = random.choice(product_types)
        data.append({
            "product_id": f"PRD{i+1:04d}",
            "product_name": f"{fake.company()} {p_type}",
            "product_type": p_type,
            "interest_rate": round(random.uniform(0.01, 20.0), 2) if "Loan" in p_type or "Card" in p_type else round(random.uniform(0.0, 5.0), 2),
            "minimum_balance": round(random.uniform(0, 10000), 2) if "Account" in p_type else 0.0,
            "monthly_fee": round(random.choice([0.0, 5.0, 10.0, 25.0]), 2),
            "is_active": random.choice([True, True, True, False]),
            "launch_date": fake.date_between(start_date="-20y", end_date="today")
        })
    return pd.DataFrame(data)
