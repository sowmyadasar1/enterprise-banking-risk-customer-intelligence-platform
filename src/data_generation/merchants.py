import pandas as pd
from faker import Faker
import numpy as np


def generate_merchants(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for merchants.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.

    Returns:
        pd.DataFrame: Generated merchants data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    categories_df = dependencies.get("merchant_categories")
    category_ids = (
        categories_df["category_id"].tolist()
        if categories_df is not None and not categories_df.empty
        else [fake.uuid4() for _ in range(n)]
    )

    data = {
        "merchant_id": [fake.uuid4() for _ in range(n)],
        "category_id": np.random.choice(category_ids, size=n),
        "merchant_name": [fake.company() for _ in range(n)],
        "country": [fake.country_code() for _ in range(n)],
        "risk_score": np.random.randint(1, 100, size=n),
        "created_at": [
            fake.date_time_between(start_date="-5y", end_date="now") for _ in range(n)
        ],
    }

    return pd.DataFrame(data)
