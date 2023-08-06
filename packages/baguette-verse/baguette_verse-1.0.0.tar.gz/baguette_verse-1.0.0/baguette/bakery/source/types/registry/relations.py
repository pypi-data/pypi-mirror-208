"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from ....logger import logger
from ...graph import Arrow, Edge
from ..execution.entities import Process
from ..filesystem.entities import Directory, File
from ..network.entities import Host
from .entities import Handle, Key, KeyEntry

__all__ = ["HasSubKey", "HasEntry", "UsesKey", "HasHandle", "Discovered", "QueriesEntry", "SetsEntry", "DeletesEntry", "ChangesTowards", "ReferencesFileSystem"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class HasSubKey(Arrow):

    """
    This kind of arrow indicates that a key has a sub-key.
    """

    label : str = ""

    source : Host | Key
    destination : Key





class HasEntry(Edge):

    """
    This kind of edge indicates that a registry key has one registry entry.
    """

    label : str = ""

    source : Key
    destination : KeyEntry





class UsesKey(Edge):

    """
    This kind of edge indicates that a handle uses a registry key.
    """

    label : str = ""

    source : Handle
    destination : Key





class HasHandle(Edge):

    """
    This kind of edge indicates that a process owns a registry key handle.
    """

    label : str = ""

    source : Process
    destination : Handle





class Discovered(Arrow):

    """
    This kind of arrow indicates that a key handle discovered a sub-key throught enumeration.
    """

    source : Handle
    destination : Key





class QueriesEntry(Arrow):

    """
    This kind of arrow indicates that a key entry was queried by a key handle. 
    """

    source : KeyEntry
    destination : Handle





class SetsEntry(Arrow):

    """
    This kind of arrow indicates that a key handle set the value of key entry.
    """

    source : Handle
    destination : KeyEntry





class DeletesEntry(Edge):

    """
    This kind of edge indicates that a key handle deleted a key entry.
    """

    source : Handle
    destination : KeyEntry





class ChangesTowards(Arrow):

    """
    This kind of arrow indicates that a key entry's content changed to another.
    """

    label : str = ""

    source : KeyEntry
    destination : KeyEntry





class ReferencesFileSystem(Edge):
    
    """
    This kind of edge indicates that a key's entry references a file or a folder.
    """

    source : KeyEntry
    destination : File | Directory





del Arrow, Directory, Edge, File, Handle, Host, Key, KeyEntry, Process, logger