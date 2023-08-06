"""Utils."""

import logging

from py_console import console, textColor

LEVEL_TO_COLOR = {
    logging.CRITICAL: textColor.MAGENTA,
    logging.ERROR: textColor.RED,
    logging.WARNING: textColor.YELLOW,
    logging.INFO: textColor.BLUE,
    logging.DEBUG: textColor.GREEN,
    logging.NOTSET: textColor.WHITE,
}


class CustomLoggingFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_TO_COLOR[record.levelno]
        return console.highlight(
            f'({record.name}-{record.levelname}): {record.msg}', color
        )


class Log(logging.Logger):
    def __init__(self, name: str, level: int = logging.DEBUG):
        super(Log, self).__init__(name, level)
        self.propagate = False

        formatter = CustomLoggingFormatter()
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self.handlers = [sh]
