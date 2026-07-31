"""Data generator for Marketing Campaigns."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_marketing_campaigns(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic marketing campaigns.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets.
        
    Returns:
        pd.DataFrame: DataFrame containing generated marketing campaigns.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()
    
    data = []
    for i in range(n):
        start_date = fake.date_between(start_date="-5y", end_date="+1y")
        end_date = fake.date_between(start_date=start_date, end_date="+2y")
        data.append({
            "campaign_id": f"CMP{i+1:05d}",
            "campaign_name": f"{fake.catch_phrase()} Campaign",
            "campaign_type": random.choice(["Email", "SMS", "Social Media", "Direct Mail", "In-App"]),
            "target_audience": random.choice(["High Net Worth", "Students", "Small Business", "Retirees", "All"]),
            "start_date": start_date,
            "end_date": end_date,
            "budget": round(random.uniform(5000, 500000), 2),
            "status": random.choice(["Planned", "Active", "Completed", "Cancelled"])
        })
    return pd.DataFrame(data)
