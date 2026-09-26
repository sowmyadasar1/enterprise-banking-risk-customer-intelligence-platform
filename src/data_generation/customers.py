"""Data generator for Customers."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_customers(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic customer data.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets.

    Returns:
        pd.DataFrame: DataFrame containing generated customers.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    data = []
    for i in range(n):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
        data.append(
            {
                "customer_id": f"CUST{i+1:08d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "date_of_birth": dob,
                "gender": random.choice(["Male", "Female", "Non-binary", "Other"]),
                "email": fake.unique.email(),
                "phone_number": fake.phone_number(),
                "ssn": fake.ssn(),
                "join_date": fake.date_between(start_date="-10y", end_date="today"),
                "customer_type": random.choice(["Retail", "Corporate", "SME"]),
                "risk_rating": random.choice(["Low", "Medium", "High"]),
                "is_active": random.choice([True, True, True, False]),
            }
        )
    return pd.DataFrame(data)
