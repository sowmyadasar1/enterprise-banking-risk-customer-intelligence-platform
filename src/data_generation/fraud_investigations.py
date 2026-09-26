"""
Generates synthetic data for Fraud Investigations.
"""

import uuid
import random
import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta
from typing import Any


def generate_fraud_investigations(
    n: int, seed: int = 42, **dependencies: Any
) -> pd.DataFrame:
    """
    Generates a DataFrame containing synthetic fraud investigations.

    Args:
        n (int): Number of records to generate.
        seed (int): Random seed for reproducibility.
        **dependencies: Optional dependencies like 'fraud_cases' DataFrame.

    Returns:
        pd.DataFrame: A dataframe of fraud investigations.
    """
    Faker.seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()

    cases_df = dependencies.get("fraud_cases")

    data = []
    for _ in range(n):
        if cases_df is not None and not cases_df.empty:
            sample_case = cases_df.sample(1).iloc[0]
            case_id = sample_case.get("case_id", str(uuid.uuid4()))
            start_date = sample_case.get(
                "report_date", fake.date_time_between(start_date="-2y", end_date="now")
            )
        else:
            case_id = str(uuid.uuid4())
            start_date = fake.date_time_between(start_date="-2y", end_date="now")

        end_date = start_date + timedelta(days=random.randint(1, 90))

        data.append(
            {
                "investigation_id": str(uuid.uuid4()),
                "case_id": case_id,
                "investigator_id": str(uuid.uuid4()),
                "start_date": start_date,
                "end_date": end_date if random.random() > 0.3 else None,
                "outcome": random.choice(
                    ["Fraud Confirmed", "False Positive", "Inconclusive", "Pending"]
                ),
                "notes": fake.sentence(nb_words=10),
            }
        )

    return pd.DataFrame(data)
