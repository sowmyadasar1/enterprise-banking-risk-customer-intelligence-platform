"""Data generator for Regions."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_regions(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic region data.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets.

    Returns:
        pd.DataFrame: DataFrame containing generated regions.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    data = []
    region_names = [
        "North",
        "South",
        "East",
        "West",
        "Central",
        "Northeast",
        "Northwest",
        "Southeast",
        "Southwest",
    ]
    for i in range(min(n, len(region_names))):
        data.append(
            {
                "region_id": f"REG{i+1:03d}",
                "region_name": region_names[i],
                "country": "USA",
                "regional_manager_id": f"EMP{random.randint(10000, 99999):06d}",
            }
        )
    return pd.DataFrame(data)
