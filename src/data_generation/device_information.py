"""
Generates synthetic data for Device Information.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from typing import Any


def generate_device_information(
    n: int, seed: int = 42, **dependencies: Any
) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic device information.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'customers' DataFrame.

    Returns:
        pd.DataFrame: A dataframe of device information.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()

    customers_df = dependencies.get("customers")

    data = []
    for _ in range(n):
        if customers_df is not None and not customers_df.empty:
            cust_id = (
                customers_df.sample(1).iloc[0].get("customer_id", str(uuid.uuid4()))
            )
        else:
            cust_id = str(uuid.uuid4())

        device_type = random.choice(["Smartphone", "Tablet", "Desktop", "Laptop"])
        os = random.choice(["iOS", "Android", "Windows", "macOS", "Linux"])

        data.append(
            {
                "device_id": str(uuid.uuid4()),
                "customer_id": cust_id,
                "device_type": device_type,
                "os": os,
                "ip_address": fake.ipv4(),
                "is_trusted": np.random.choice([True, False], p=[0.8, 0.2]),
                "registered_at": fake.date_time_between(
                    start_date="-3y", end_date="now"
                ),
            }
        )

    return pd.DataFrame(data)
