"""Data generator for Campaign Responses."""

import random
from typing import Any
import pandas as pd
from faker import Faker

def generate_campaign_responses(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic campaign responses.
    
    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers' and 'marketing_campaigns'.
        
    Returns:
        pd.DataFrame: DataFrame containing generated campaign responses.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()
    
    customers_df = dependencies.get('customers')
    campaigns_df = dependencies.get('marketing_campaigns')
    
    if customers_df is None or customers_df.empty:
        raise ValueError("Customers dataframe must be provided as a dependency.")
    if campaigns_df is None or campaigns_df.empty:
        raise ValueError("Marketing campaigns dataframe must be provided as a dependency.")
        
    customer_ids = customers_df['customer_id'].tolist()
    campaign_ids = campaigns_df['campaign_id'].tolist()
    
    data = []
    for _ in range(n):
        data.append({
            "response_id": str(fake.unique.uuid4()),
            "campaign_id": random.choice(campaign_ids),
            "customer_id": random.choice(customer_ids),
            "response_type": random.choice(["Opened", "Clicked", "Ignored", "Opted Out", "Converted"]),
            "response_date": fake.date_time_between(start_date="-5y", end_date="now"),
            "channel": random.choice(["Email", "SMS", "Social Media", "Direct Mail", "In-App"])
        })
    return pd.DataFrame(data)
