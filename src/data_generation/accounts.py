import pandas as pd
from faker import Faker
import numpy as np


def generate_accounts(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for accounts.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames (e.g., customers, branches).

    Returns:
        pd.DataFrame: Generated accounts data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    customers_df = dependencies.get("customers")
    branches_df = dependencies.get("branches")

    customer_ids = (
        customers_df["customer_id"].tolist()
        if customers_df is not None and not customers_df.empty
        else [fake.uuid4() for _ in range(n)]
    )
    branch_ids = (
        branches_df["branch_id"].tolist()
        if branches_df is not None and not branches_df.empty
        else [fake.uuid4() for _ in range(n)]
    )

    selected_customers = np.random.choice(customer_ids, size=n, replace=True)
    selected_branches = np.random.choice(branch_ids, size=n, replace=True)

    account_types = ["CHECKING", "SAVINGS", "CREDIT", "LOAN", "INVESTMENT"]
    statuses = ["ACTIVE", "INACTIVE", "CLOSED", "FROZEN"]
    currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]

    data = {
        "account_id": [fake.uuid4() for _ in range(n)],
        "customer_id": selected_customers,
        "branch_id": selected_branches,
        "account_type": np.random.choice(
            account_types, size=n, p=[0.4, 0.4, 0.1, 0.05, 0.05]
        ),
        "balance": np.round(np.random.lognormal(mean=7, sigma=1.5, size=n), 2),
        "currency": np.random.choice(currencies, size=n, p=[0.7, 0.1, 0.1, 0.05, 0.05]),
        "open_date": [
            fake.date_between(start_date="-10y", end_date="today") for _ in range(n)
        ],
        "status": np.random.choice(statuses, size=n, p=[0.8, 0.1, 0.05, 0.05]),
        "interest_rate": np.round(np.random.uniform(0.001, 0.05, size=n), 4),
    }

    return pd.DataFrame(data)
