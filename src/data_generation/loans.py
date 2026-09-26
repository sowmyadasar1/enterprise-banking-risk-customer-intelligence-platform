import pandas as pd
from faker import Faker
import numpy as np


def generate_loans(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for loans.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.

    Returns:
        pd.DataFrame: Generated loans data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    customers_df = dependencies.get("customers")
    accounts_df = dependencies.get("accounts")

    customer_ids = (
        customers_df["customer_id"].tolist()
        if customers_df is not None and not customers_df.empty
        else [fake.uuid4() for _ in range(n)]
    )
    account_ids = (
        accounts_df["account_id"].tolist()
        if accounts_df is not None and not accounts_df.empty
        else [fake.uuid4() for _ in range(n)]
    )

    loan_types = ["PERSONAL", "MORTGAGE", "AUTO", "STUDENT", "BUSINESS"]
    statuses = ["ACTIVE", "PAID_OFF", "DEFAULTED", "DELINQUENT"]

    amounts = np.round(np.random.lognormal(mean=10, sigma=1.5, size=n), 2)

    data = {
        "loan_id": [fake.uuid4() for _ in range(n)],
        "customer_id": np.random.choice(customer_ids, size=n),
        "funding_account_id": np.random.choice(account_ids, size=n),
        "loan_type": np.random.choice(loan_types, size=n),
        "loan_amount": amounts,
        "principal_balance": [a * np.random.uniform(0, 1) for a in amounts],
        "interest_rate": np.round(np.random.uniform(0.02, 0.20, size=n), 4),
        "start_date": [
            fake.date_between(start_date="-5y", end_date="today") for _ in range(n)
        ],
        "term_months": np.random.choice([12, 24, 36, 48, 60, 120, 360], size=n),
        "status": np.random.choice(statuses, size=n, p=[0.7, 0.2, 0.05, 0.05]),
    }

    df = pd.DataFrame(data)
    df["end_date"] = pd.to_datetime(df["start_date"]) + pd.to_timedelta(
        df["term_months"] * 30, unit="D"
    )
    return df
