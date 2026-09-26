import pandas as pd
from typing import List


def fill_missing_values(
    df: pd.DataFrame, strategy: str = "median", columns: List[str] = None
) -> pd.DataFrame:
    """Fills missing values in specified columns using the given strategy."""
    df_out = df.copy()
    cols = columns if columns else df_out.select_dtypes(include=["number"]).columns

    for col in cols:
        if strategy == "median":
            df_out[col] = df_out[col].fillna(df_out[col].median())
        elif strategy == "mean":
            df_out[col] = df_out[col].fillna(df_out[col].mean())
        elif strategy == "mode":
            df_out[col] = df_out[col].fillna(df_out[col].mode()[0])
        elif strategy == "zero":
            df_out[col] = df_out[col].fillna(0)
    return df_out


def one_hot_encode(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Applies one-hot encoding to specified categorical columns."""
    return pd.get_dummies(df, columns=columns, drop_first=True)
