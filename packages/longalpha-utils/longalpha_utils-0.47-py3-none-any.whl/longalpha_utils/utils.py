import datetime
from typing import List

import pandas as pd
from pyspark.sql import DataFrame


def max_pandas_display(pd: pd, max_row: int = 100) -> None:
    """
    set pandas print format to print all
    Args:
        pd: pandas object

    Returns: None

    """
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", max_row)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.expand_frame_repr", False)

def validate_date_format(date_str, date_format = "%Y-%m-%d"):
    try:
        datetime.datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def multi_union_by_name(dfs: List[DataFrame]) -> DataFrame:
    """
    union a list of dataframes to one. dataframes need to have the same columns for join.
    Args:
        dfs: a list of dataframes

    Returns: a post-join single dataframe

    """
    if len(dfs) == 0:
        raise ValueError("Dataframes list cannot be empty")
    df = dfs[0]
    for i in dfs[1:]:
        df = df.unionByName(i)
    return df