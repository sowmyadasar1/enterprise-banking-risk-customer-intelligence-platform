import pandas as pd
from faker import Faker
import numpy as np


def generate_transaction_types(n: int, seed: int = 42, **dependencies) -> pd.DataFrame:
    """
    Generate synthetic data for transaction types.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Dictionary of dependent DataFrames.

    Returns:
        pd.DataFrame: Generated transaction types data.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    types = [
        ("PURCHASE", "Point of sale purchase", False),
        ("WITHDRAWAL", "ATM Withdrawal", False),
        ("DEPOSIT", "Cash or check deposit", True),
        ("TRANSFER_IN", "Inbound transfer", True),
        ("TRANSFER_OUT", "Outbound transfer", False),
        ("FEE", "Bank fee", False),
        ("INTEREST", "Interest paid", True),
        ("REFUND", "Merchant refund", True),
        ("PAYMENT", "Bill payment", False),
        ("DIRECT_DEPOSIT", "Payroll direct deposit", True),
    ]

    actual_n = min(n, len(types))
    selected_types = types[:actual_n]

    data = {
        "transaction_type_id": [fake.uuid4() for _ in range(actual_n)],
        "type_name": [t[0] for t in selected_types],
        "description": [t[1] for t in selected_types],
        "is_credit": [t[2] for t in selected_types],
    }

    return pd.DataFrame(data)
