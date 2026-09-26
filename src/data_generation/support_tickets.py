"""Data generator for Support Tickets."""

import random
from typing import Any
import pandas as pd
from faker import Faker


def generate_support_tickets(
    n: int, seed: int = 42, **dependencies: Any
) -> pd.DataFrame:
    """
    Generate synthetic support tickets data.

    Args:
        n (int): Number of records to generate.
        seed (int, optional): Random seed for reproducibility. Defaults to 42.
        **dependencies: Additional dependent datasets, specifically 'customers'.

    Returns:
        pd.DataFrame: DataFrame containing generated support tickets.
    """
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    customers_df = dependencies.get("customers")
    if customers_df is None or customers_df.empty:
        raise ValueError("Customers dataframe must be provided as a dependency.")

    customer_ids = customers_df["customer_id"].tolist()

    data = []
    for i in range(n):
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        status = random.choice(["Open", "In Progress", "Resolved", "Closed"])
        resolved_at = None
        if status in ["Resolved", "Closed"]:
            resolved_at = fake.date_time_between(start_date=created_at, end_date="now")

        data.append(
            {
                "ticket_id": f"TKT{i+1:08d}",
                "customer_id": random.choice(customer_ids),
                "issue_category": random.choice(
                    [
                        "Account Access",
                        "Transaction Dispute",
                        "Fraud Report",
                        "Card Replacement",
                        "General Inquiry",
                    ]
                ),
                "priority": random.choice(["Low", "Medium", "High", "Critical"]),
                "status": status,
                "created_at": created_at,
                "resolved_at": resolved_at,
                "assigned_to_employee_id": f"EMP{random.randint(1, 1000):06d}",
                "satisfaction_score": (
                    random.randint(1, 5) if status in ["Resolved", "Closed"] else None
                ),
            }
        )
    return pd.DataFrame(data)
