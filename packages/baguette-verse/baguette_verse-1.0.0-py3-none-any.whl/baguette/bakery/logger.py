"""
This module adds a strong logging system to the bakery package.
"""

import logging
import sys

__all__ = ["logger", "stdout_handler", "standart_formatter", "set_level", "create_log_file"]





logger = logging.getLogger()
logger.setLevel(0)
stdout_handler = logging.StreamHandler(sys.stdout)
standart_formatter = logging.Formatter("%(levelname)-8s : %(module)-10s : %(asctime)-24s : %(message)s")

logger.addHandler(stdout_handler)
stdout_handler.setFormatter(standart_formatter)





def set_level(level : int):
    """
    Sets the logging level to stdout.
    """
    stdout_handler.setLevel(level)

def create_log_file(path : str, level : int = logging.DEBUG):
    """
    Creates a new log file to which logs with a level higher or equal to the current level will be written.
    """
    handler = logging.FileHandler(path, "w")
    handler.setFormatter(standart_formatter)
    handler.setLevel(level)
    logger.addHandler(handler)

set_level(logging.WARNING)

del logging, sys