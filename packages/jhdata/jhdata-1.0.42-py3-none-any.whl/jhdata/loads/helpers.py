import pandas as pd


def get_pd_statistics(df: pd.DataFrame):
    return {
        "columns": df.columns,
        "dtypes": df.dtypes,
        "size": df.size
    }
