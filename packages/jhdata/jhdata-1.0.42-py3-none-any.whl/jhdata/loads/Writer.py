"""
Writer classes are meant to write a delivery of data to a target, which can contain multiple tables

They take a dict in a format like {"table1": dataframe1, "table2": dataframe2}
"""

from jhdata.loads.helpers import *


# Base Writer class
class Writer:
    def write(self, load_step, input: dict[str, pd.DataFrame]):
        load_step.logger.fail("The Writer class should not be used directly, but inherited from. "
                               "You can use NoopWriter instead")


# Writer class that does nothing on write
class NoopWriter(Writer):
    def write(self, load_step, input: dict[str, pd.DataFrame]):
        load_step.logger.info("Write step skipped")


# Reads parquet files from a directory
class ParquetWriter(Writer):
    def __init__(self, filehelper=None, directory=None, **parquet_args):
        self.filehelper = filehelper
        self.directory = directory
        self.parquet_args = parquet_args

    def write(self, load_step, input: dict[str, pd.DataFrame]) -> None:
        fh = self.filehelper if self.filehelper else load_step.filehelper

        for table_name, df in input.items():
            path = f"{self.directory}/{table_name}" if self.directory is not None else f"raw/{load_step.load.source_name}/staging/{table_name}.parquet"
            fh.write_parquet(path, df, **self.parquet_args)
            size = get_pd_statistics(df)["size"]
            load_step.logger.info(f"Wrote file to {path} with {size}")
