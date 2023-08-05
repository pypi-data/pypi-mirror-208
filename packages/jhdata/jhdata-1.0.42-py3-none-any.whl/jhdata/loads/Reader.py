"""
Reader classes are meant to read a delivery of data, which can contain multiple tables

They take an arbitrary input and return a dict in a format like {"table1": dataframe1, "table2": dataframe2}
"""

import os
import pandas as pd


# Takes a dict of {table: dataframe} directly in Memory and just returns it
class Reader:
    def read(self, load_step, input: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input


# Reads parquet files from a directory
class JSONReader(Reader):
    def __init__(self, filehelper=None, table_regex=r"(?P<table_name>.*)_(?P<timestamp>[0-9]{8}_[0-9]{6})\.json", directory=None, **json_args):
        self.filehelper = filehelper
        self.directory = directory
        self.json_args = json_args
        self.table_regex = table_regex

    def read(self, load_step, input) -> dict[str, pd.DataFrame]:
        fh = self.filehelper if self.filehelper else load_step.filehelper
        path = self.directory if self.directory is not None else f"raw/{load_step.load.source_name}/staging"

        load_step.logger.info(f"Looking for valid files in {path}")
        valid_files = fh.find_regex(path, self.table_regex)
        print(valid_files)

        table_dict = {}
        for file_path, groups in valid_files:
            table_dict[groups["table_name"]] = fh.read_json(file_path, **self.json_args)
            load_step.logger.info(f"Read JSON file at {file_path}")

        return table_dict


class SQLReader(Reader):
    def __init__(self, filehelper=None, table=None, **sql_args):
        self.filehelper = filehelper
        self.table = table

