import pandas as pd
from faker import Faker
import numpy as np


def generate_credit_cards(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for credit cards.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.

    Returns:
        pd.DataFrame: Generated credit cards data.
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

    card_types = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]

    data = {
        "card_id": [fake.uuid4() for _ in range(n)],
        "customer_id": np.random.choice(customer_ids, size=n),
        "account_id": np.random.choice(account_ids, size=n),
        "card_number": [fake.credit_card_number() for _ in range(n)],
        "expiration_date": [fake.credit_card_expire() for _ in range(n)],
        "cvv": [fake.credit_card_security_code() for _ in range(n)],
        "card_type": np.random.choice(card_types, size=n),
        "is_active": np.random.choice([True, False], size=n, p=[0.85, 0.15]),
        "issued_date": [
            fake.date_between(start_date="-3y", end_date="today") for _ in range(n)
        ],
        "credit_limit": np.round(np.random.uniform(1000, 50000, size=n), -2),
    }

    return pd.DataFrame(data)
