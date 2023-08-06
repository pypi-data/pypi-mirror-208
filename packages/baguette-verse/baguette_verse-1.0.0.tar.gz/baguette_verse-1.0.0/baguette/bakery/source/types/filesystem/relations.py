"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from ....logger import logger
from ...graph import Arrow, Edge
from ..data.entities import Data
from ..execution.entities import Call, Process
from ..network.entities import Host
from .entities import Directory, File, Handle

__all__ = ["UsesFile", "UsesDirectory", "Opens", "Closes", "CreatesFile", "CreatesDirectory", "DeletesFile", "DeletesDirectory", "Reads", "Writes", "Conveys", "HasDrive", "HasHandle", "Contains", "IsCopyiedInto"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class UsesFile(Edge):

    """
    This kind of edge indicates that a handle uses a file.
    """

    label : str = ""

    source : Handle
    destination : File





class UsesDirectory(Edge):

    """
    This kind of edge indicates that a handle uses a directory.
    """

    label : str = ""

    source : Handle
    destination : Directory





class Opens(Edge):

    """
    This kind of edge indicates that a system call opened a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class Closes(Edge):

    """
    This kind of edge indicates that a system call closed a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class CreatesFile(Edge):

    """
    This kind of edge indicates that a system call created a file through a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class CreatesDirectory(Edge):

    """
    This kind of edge indicates that a system call created a directory through a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class DeletesFile(Edge):

    """
    This kind of edge indicates that a system call deleted a file through a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class DeletesDirectory(Edge):

    """
    This kind of edge indicates that a system call deleted a directory through a handle.
    """

    label : str = ""

    source : Call
    destination : Handle





class Reads(Arrow):

    """
    This kind of arrow indicates that a system call read data from a file.
    """

    source : Data
    destination : Call





class Writes(Arrow):

    """
    This kind of arror indicates that a system call wrote data to a file.
    """

    source : Call
    destination : Data





class Conveys(Arrow):

    """
    This kind of arrow indicates a data flux with a file handle.
    """

    label : str = ""

    source : Handle | Data
    destination : Handle | Data





class HasDrive(Edge):

    """
    This kind of edge indicates that a machine owns a disk drive/partition(/root directory).
    """

    label : str = ""

    source : Host
    destination : Directory





class HasHandle(Edge):

    """
    This kind of edge indicates that a process owns a file handle.
    """

    label : str = ""

    source : Process
    destination : Handle





class Contains(Arrow):

    """
    This kind of arrow indicates that a directory contains a file or another directory.
    """

    label : str = ""

    source : Directory
    destination : Directory | File





class IsCopyiedInto(Arrow):

    """
    This kind indicates that the destination file is a copy of the source file.
    """

    source : File
    destination : File





del Arrow, Call, Data, Directory, Edge, File, Handle, Host, Process, logger