from jhdata.filehelper import FileHelper
from jhdata.logger import Logger
from jhdata.loads.LoadStep import LoadStep
from jhdata.dates import current_timestamp


class Load:
    def __init__(self, source_name: str, steps: list[LoadStep] = None, input=None, filehelper=None, logger=None):
        self.steps = steps if steps is not None else []
        self.files = filehelper if filehelper is not None else FileHelper()
        self.logger = logger if logger is not None else Logger()
        self.input = input
        self.source_name = source_name

    def run(self):
        result_dict = {}
        current_data = self.input

        for step in self.steps:
            step.load = self
            data_out, metadata = step.run(current_data)

            current_data = data_out
            result_dict[step.step_name] = metadata

        self.finalize()

        return current_data, result_dict

    def finalize(self):
        self.logger.analyze_log()
        log_content = self.logger.get_log_contents()
        log_path = f"logs/{self.source_name}/log_{current_timestamp()}"
        self.files.write_text(log_path, log_content)
