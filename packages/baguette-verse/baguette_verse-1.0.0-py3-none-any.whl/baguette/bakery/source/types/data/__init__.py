"""
This package defines the graph-related subclasses that modelize the flow of data.
"""

from ....logger import logger





logger.info("Finalizing {} library.".format(__name__.rpartition(".")[2]))

from .entities import *
from .relations import *