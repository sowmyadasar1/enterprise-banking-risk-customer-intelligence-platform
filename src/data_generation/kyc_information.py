"""Data generator for KYC Information."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_kyc_information(
    n: int, seed: int = 42, **dependencies: Any
) -> pd.DataFrame:
    """
    Generate synthetic KYC information.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers'.

    Returns:
        pd.DataFrame: DataFrame containing generated KYC information.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    customers_df = dependencies.get("customers")
    if customers_df is None or customers_df.empty:
        raise ValueError("Customers dataframe must be provided as a dependency.")

    customer_ids = customers_df["customer_id"].tolist()

    data = []
    for _ in range(n):
        customer_id = random.choice(customer_ids)
        data.append(
            {
                "kyc_id": str(fake.unique.uuid4()),
                "customer_id": customer_id,
                "document_type": random.choice(
                    ["Passport", "Driver's License", "National ID"]
                ),
                "document_number": fake.bothify(text="??#######"),
                "issue_date": fake.date_between(start_date="-10y", end_date="-1y"),
                "expiry_date": fake.date_between(start_date="today", end_date="+10y"),
                "verification_status": random.choice(
                    ["Verified", "Pending", "Rejected"]
                ),
                "last_verified_date": fake.date_between(
                    start_date="-1y", end_date="today"
                ),
                "verified_by_employee_id": f"EMP{random.randint(1, 1000):06d}",
            }
        )
    return pd.DataFrame(data)
