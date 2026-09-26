"""Data generator for Branches."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_branches(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic branch data.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'regions'.

    Returns:
        pd.DataFrame: DataFrame containing generated branches.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    regions_df = dependencies.get("regions")
    region_ids = (
        regions_df["region_id"].tolist()
        if regions_df is not None and not regions_df.empty
        else [f"REG{i:03d}" for i in range(1, 10)]
    )

    data = []
    for i in range(n):
        data.append(
            {
                "branch_id": f"BRN{i+1:05d}",
                "branch_name": f"{fake.city()} Branch",
                "region_id": random.choice(region_ids),
                "address": fake.street_address(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip_code": fake.zipcode(),
                "phone_number": fake.phone_number(),
                "open_date": fake.date_between(start_date="-50y", end_date="-1y"),
            }
        )
    return pd.DataFrame(data)
