import datetime
import time
from typing import Union


class LoggerException(Exception):
    pass


class Logger:
    def __init__(self, do_print=True, name: Union[str, None] = None):
        self.messages = []
        self.do_print = do_print
        self.levels = ["ok", "fail", "warn", "info", "debug"]
        self.name = name

    def pretty_print(self, message):
        level, timestamp, content = message
        timecode = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H-%M-%S")
        print(f"[{level}][{timecode}] {content}")

    def get_messages(self):
        return self.messages

    def get_messages_on_level(self, wanted_level):
        return [(level, timestamp, content) for level, timestamp, content in self.messages if level == wanted_level]

    def log(self, level: str, *messages):
        content = " ".join([str(message) for message in messages])

        if level not in self.levels:
            level_string = ", ".join(self.levels)
            raise LoggerException(f"Unknown Log level {level}, should be one of {level_string}")

        timestamp = time.time()

        message = (level, timestamp, content)
        self.messages.append(message)

        if self.do_print:
            self.pretty_print(message)

    def info(self, message: str):
        self.log("info", message)

    def warn(self, message: str):
        self.log("warn", message)

    def fail(self, message: str):
        self.log("fail", message)

    def success(self, message: str):
        self.log("ok", message)

    def exception(self, exception: Exception):
        self.fail(f"{exception.__class__}: {exception}")

    def log_list(self, messages):
        self.messages += messages

    def merge(self, logger):
        self.log_list(logger.messages)

    def analyze_log(self):
        for level in ["ok", "fail", "warn"]:
            self.info(f"{level} - {len(self.get_messages_on_level(level))}")

    def get_log_contents(self):
        return "\n".join(self.get_messages())
