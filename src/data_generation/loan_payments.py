import pandas as pd
from faker import Faker
import numpy as np


def generate_loan_payments(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for loan payments.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.

    Returns:
        pd.DataFrame: Generated loan payments data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    loans_df = dependencies.get("loans")
    loan_ids = (
        loans_df["loan_id"].tolist()
        if loans_df is not None and not loans_df.empty
        else [fake.uuid4() for _ in range(n)]
    )

    statuses = ["COMPLETED", "PENDING", "MISSED"]

    total_amounts = np.round(np.random.uniform(50, 2000, size=n), 2)
    principal_amounts = np.round(
        total_amounts * np.random.uniform(0.6, 0.95, size=n), 2
    )
    interest_amounts = total_amounts - principal_amounts

    data = {
        "payment_id": [fake.uuid4() for _ in range(n)],
        "loan_id": np.random.choice(loan_ids, size=n),
        "payment_date": [
            fake.date_between(start_date="-1y", end_date="today") for _ in range(n)
        ],
        "total_amount": total_amounts,
        "principal_amount": principal_amounts,
        "interest_amount": interest_amounts,
        "status": np.random.choice(statuses, size=n, p=[0.9, 0.05, 0.05]),
    }

    return pd.DataFrame(data)
