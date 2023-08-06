import pandas as pd
from collections import Counter


def missing_days(df: pd.DataFrame) -> list[pd.Timestamp]:
    """Find timestamps of missing days."""
    if df.empty:
        raise ValueError("empty data")
    df = df.sort_index()
    return pd.date_range(df.index[0], df.index[-1]).difference(df.index)


def duplicates(df: pd.DataFrame) -> list[pd.Timestamp]:
    """Find indexes of duplicates."""
    if df.empty:
        raise ValueError("empty data")
    days = df.index.tolist()
    return [item for item, count in Counter(days).items() if count > 1]


def search_missing_values(
        df: pd.DataFrame, colname: str, val: str | float
        ) -> list[pd.Timestamp]:
    """Find indexes from samples where a specific column has value val."""
    if df.empty:
        raise ValueError("empty data")
    indexes = df.index[df[colname] == val].tolist()
    return indexes
