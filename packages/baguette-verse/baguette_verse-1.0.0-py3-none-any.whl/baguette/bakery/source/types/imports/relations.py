"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from ....logger import logger
from ...graph import Edge
from ..execution.entities import Process
from ..filesystem.entities import File
from .entities import *

__all__ = ["HasImport", "IsFile"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class HasImport(Edge):

    """
    This kind of edge indicates that a process imported something.
    """

    label : str = ""

    source : Process
    destination : Import





class IsFile(Edge):

    """
    This kind of edge indicates that an import corresponds to an existing file object.
    """

    label : str = ""

    source : Import
    destination : File





del Edge, File, Import, Process, logger