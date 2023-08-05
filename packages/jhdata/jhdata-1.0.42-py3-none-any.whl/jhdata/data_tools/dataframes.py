import pandas as pd
import numpy as np


from jhdata.data_tools.schemas import *
from jhdata.logger import Logger
from jhdata.dates import current_datetime


def add_load_timestamp(df: pd.DataFrame):
    if "load_timestamp" not in df.columns:
        df["load_timestamp"] = current_datetime()

    return df


def upsert_dataframes(target_df: pd.DataFrame, update_df: pd.DataFrame, schema: Schema, logger: Logger = None):
    logger = logger if logger is not None else Logger()

    pks = schema.primary_keys
    update_df = add_load_timestamp(update_df)

    logger.info(f"Upserting dataframe with {update_df.shape[0]} rows on primary keys {pks}...")

    update_df = update_df.set_index(pks, drop=False)
    target_df = target_df.set_index(pks, drop=False)

    result_df = pd.concat([target_df, update_df[~update_df.index.isin(target_df.index)]])
    result_df.update(update_df)

    logger.info(f"{result_df.shape[0] - target_df.shape[0]} were added to the table. {result_df.shape[0]} rows total")

    return result_df


def apply_delete_columns(target_df: pd.DataFrame, update_df: pd.DataFrame, schema: Schema):
    delete_columns = schema.delete_columns
    print("delete_columns:", delete_columns)
    delete_values = set([tuple(row) for row in update_df[delete_columns].values])
    print(delete_values)
    matched_mask = np.array([tuple(row) in delete_values for row in target_df[delete_columns].values])
    result_df = target_df[~matched_mask]
    print("Dropping values...")
    print(result_df.head())
    result_df = pd.concat([result_df, update_df], ignore_index=True)
    print("Concatenating...")
    return result_df


def append_missing_values(target_df: pd.DataFrame, update_df: pd.DataFrame, schema: Schema):
    pks = schema.primary_keys

    update_df = add_load_timestamp(update_df)
    print(update_df.head())
    update_df = update_df.set_index(pks, drop=False)
    target_df = target_df.set_index(pks, drop=False)

    print("Appending...")
    result_df = pd.concat([target_df, update_df[~update_df.index.isin(target_df.index)]])

    return result_df


def merge_dataframes(target_df: pd.DataFrame, update_df: pd.DataFrame, schema: Schema):
    if len(schema.primary_keys) > 0:
        return upsert_dataframes(target_df, update_df, schema)
    else:
        return apply_delete_columns(target_df, update_df, schema)


# Add any necessary columns to the dataframe
def add_missing_columns(df: pd.DataFrame, schema: Schema) -> pd.DataFrame:
    columns_to_add = [column_name for column_name in schema.column_names if column_name not in list(df.columns)]
    print(f"Adding columns {columns_to_add}")
    for column_name in columns_to_add:
        df[column_name] = None

    df = schema.reorder_columns(df)

    return df


def dataframe_from_data(data: list) -> pd.DataFrame:
    df = pd.DataFrame(data=data, dtype="object")
    return df
