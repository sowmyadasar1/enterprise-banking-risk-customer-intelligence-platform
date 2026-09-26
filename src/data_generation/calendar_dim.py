"""
Generates the Calendar / Date Dimension dataset.
"""

import pandas as pd
from datetime import date, timedelta
from typing import Any


def generate_calendar_dim(n: int, seed: int = 42, **dependencies: Any) -> pd.DataFrame:
    """
    Generates a calendar dimension dataframe for analytical purposes.

    Args:
        n (int): Number of days to generate starting from a base date.
        seed (int): Seed for consistency (though deterministic here).
        **dependencies: Optional dependencies.

    Returns:
        pd.DataFrame: A dataframe of date dimensions.
    """
    # Start date e.g. 2015-01-01
    start_date = date(2015, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n)]

    data = []
    for d in dates:
        data.append(
            {
                "date_id": int(d.strftime("%Y%m%d")),
                "full_date": pd.Timestamp(d),
                "year": d.year,
                "month": d.month,
                "day": d.day,
                "quarter": (d.month - 1) // 3 + 1,
                "day_of_week": d.weekday(),
                "day_name": d.strftime("%A"),
                "is_weekend": d.weekday() >= 5,
                "is_holiday": False,  # Simplified for this dataset
            }
        )
    return pd.DataFrame(data)
