import logging
from typing import Any

import colorama
from colorama import Fore


logger = logging.getLogger("potion")
logger.setLevel(logging.ERROR)


class Log:
    """ Write log messages. """
    @classmethod
    def debug(cls, msg: Any) -> None:
        """ Log a debug message. """
        logger.debug(str(msg))

    @classmethod
    def info(cls, msg: Any) -> None:
        """ Log an info message. """
        logger.info(str(msg))

    @classmethod
    def warning(cls, msg: Any) -> None:
        """ Log a warning message. """
        logger.warning(str(msg))

    @classmethod
    def error(cls, msg: Any) -> None:
        """ Log an error message. """
        logger.error(str(msg))


class ConsoleFormatter(logging.Formatter):
    colors = {
        'DEBUG': Fore.WHITE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
    }

    def format(self, record):
        color = self.colors.get(record.levelname, Fore.RESET)
        return color + super().format(record) + Fore.RESET

    def formatTime(self, record, datefmt=None):
        color = self.colors.get(record.levelname, Fore.RESET)
        return color + super().formatTime(record, datefmt)


if __debug__:
    colorama.init()
    logger.setLevel(logging.DEBUG)

    # Console logger
    console_formatter = ConsoleFormatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
