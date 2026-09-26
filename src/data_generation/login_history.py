"""
Generates synthetic data for Login History.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from typing import Any


def generate_login_history(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic login history.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'device_information' DataFrame.

    Returns:
        pd.DataFrame: A dataframe of login history.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()

    devices_df = dependencies.get("device_information")

    data = []
    for _ in range(n):
        if devices_df is not None and not devices_df.empty:
            sample_device = devices_df.sample(1).iloc[0]
            device_id = sample_device.get("device_id", str(uuid.uuid4()))
            cust_id = sample_device.get("customer_id", str(uuid.uuid4()))
            ip = sample_device.get("ip_address", fake.ipv4())
        else:
            device_id = str(uuid.uuid4())
            cust_id = str(uuid.uuid4())
            ip = fake.ipv4()

        status = np.random.choice(
            ["Success", "Failed", "Requires MFA"], p=[0.85, 0.1, 0.05]
        )

        data.append(
            {
                "login_id": str(uuid.uuid4()),
                "customer_id": cust_id,
                "device_id": device_id,
                "login_timestamp": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ),
                "ip_address": ip,
                "location": f"{fake.city()}, {fake.country_code()}",
                "status": status,
            }
        )

    return pd.DataFrame(data)
