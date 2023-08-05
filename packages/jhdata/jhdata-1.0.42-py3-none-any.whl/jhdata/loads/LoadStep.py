import pandas as pd

from jhdata.logger import Logger
from jhdata.loads.Reader import Reader
from jhdata.loads.Writer import Writer
from jhdata.filehelper import FileHelper
from jhdata.loads.helpers import get_pd_statistics

"""
One step of a load - meant to be inherited from
By default receives a DataFrame in Memory and writes it as a Parquet file only if write_to_disk is set to True
"""


class LoadStep:
    def __init__(self, step_name, reader: Reader = Reader(), writer: Writer = Writer(),
                 transformation=lambda data: data, filehelper: FileHelper = None):
        self.load = None
        self.step_name = step_name
        self.filehelper = filehelper if filehelper is not None else FileHelper()
        self.logger = Logger()

        self.reader = reader
        self.transformation = transformation
        self.writer = writer

    """
    Call the other relevant methods in order:
    - load
    - process
    - write
    
    Then return the data and some metadata if applicable
    """

    def run(self, input):
        data_in = self.reader.read(self, input)
        data_out = self.transformation(data_in)

        self.writer.write(self, data_out)

        # Can be expanded in the future by using a more general metadata function
        if isinstance(data_out, pd.DataFrame):
            return data_out, get_pd_statistics(data_out)
        else:
            return data_out, None
