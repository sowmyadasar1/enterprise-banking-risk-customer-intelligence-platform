"""Data generator for Employees."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_employees(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generate synthetic employee data.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'branches'.

    Returns:
        pd.DataFrame: DataFrame containing generated employees.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    branches_df = dependencies.get("branches")
    if branches_df is None or branches_df.empty:
        raise ValueError("Branches dataframe must be provided as a dependency.")

    branch_ids = branches_df["branch_id"].tolist()

    data = []
    for i in range(n):
        data.append(
            {
                "employee_id": f"EMP{i+1:06d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.unique.company_email(),
                "phone": fake.phone_number(),
                "job_title": random.choice(
                    [
                        "Teller",
                        "Branch Manager",
                        "Loan Officer",
                        "Financial Advisor",
                        "Customer Service Rep",
                    ]
                ),
                "branch_id": random.choice(branch_ids),
                "hire_date": fake.date_between(start_date="-20y", end_date="today"),
                "salary": round(random.uniform(40000, 150000), 2),
                "is_active": random.choice([True, True, False]),
            }
        )
    return pd.DataFrame(data)
