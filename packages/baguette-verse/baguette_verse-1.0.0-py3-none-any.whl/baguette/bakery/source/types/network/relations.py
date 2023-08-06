"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from ....logger import logger
from ...config import SwitchSetting
from ...colors import Color
from ...graph import Arrow, Edge, Vertex
from ..data.entities import Data
from ..execution.entities import Call, Process
from .entities import Connection, Host, Socket

__all__ = ["SpawnedProcess", "HasSocket", "HasConnection", "Communicates", "CreatesSocket", "Binds", "Connects", "Sends", "Receives", "Conveys", "Closes", "CloseSocket", "ListensOn", "Shutdown", "Accepts", "Duplicates"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class SpawnedProcess(Edge):
    
    """
    This kind of edge indicates that a machine hosts a process.
    """

    source : Host
    destination : Process





class HasSocket(Edge):

    """
    This kind of edge indicates that a process opened a socket.
    """

    label : str = ""

    source : Process
    destination : Socket





class HasConnection(Edge):

    """
    This kind of edge indicates that a socket makes a connection.
    """

    label : str = ""

    source : Socket
    destination : Connection





class Communicates(Edge):

    """
    This kind of edge indicates that two hosts communicate via a connection
    """

    source : Connection
    destination : Host





class CreatesSocket(Edge):

    """
    This kind of edge indicates that a system call created a socket.
    """

    label : str = ""

    source : Call
    destination : Socket





class Binds(Edge):

    """
    This kind of edge indicates that a system call bound a connection to a local address.
    """

    __slots__ = {
        "src" : "The source (local) address of the connection",
    }

    __pickle_slots__ = {
        "src"
    }

    label : str = ""

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True) -> None:
        from typing import Any
        super().__init__(source, destination, auto_write=auto_write)
        self.src : Any = None





class Connects(Edge):

    """
    This kind of edge indicates that a system call connected a connection to a remote address.
    """

    __slots__ = {
        "dest" : "The destination (remote) address of the connection"
    }

    __pickle_slots__ = {
        "dest"
    }

    label : str = ""

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True) -> None:
        from typing import Any
        super().__init__(source, destination, auto_write=auto_write)
        self.dest : Any = None





class Sends(Arrow):

    """
    This kind of arrow indicates that a system call sent data through a connection.
    """

    source : Call
    destination : Data





class Receives(Arrow):

    """
    This kind of arrow indicates that a system call received data through a connection.
    """

    source : Data
    destination : Call





class Conveys(Arrow):
    
    """
    This kind of arrow indicates that a connection conveyed a message.
    """

    label : str = ""

    source : Connection | Data
    destination : Connection | Data





class Closes(Edge):

    """
    This kind of edge indicates that a system call closed a connection.
    """
    
    label : str = ""

    source : Call
    destination : Connection





class CloseSocket(Edge):

    """
    This kind of edge indicates that a system call closed a socket object.
    """

    label : str = ""

    source : Call
    destination : Socket





class ListensOn(Edge):

    """
    This kind of edge indicates that a system call set a socket to listening mode.
    """

    source : Call
    destination : Socket





class Shutdown(Edge):

    """
    This kind of edge indicates that a connection was shutdown by a system call.
    """

    label : str = ""

    source : Call
    destination : Connection





class Accepts(Edge):

    """
    This kind of arrow indicates that a system call accepted a connection from a remote address.
    """

    __slots__ = {
        "dest" : "The destination (remote) address of the connection"
    }

    __pickle_slots__ = {
        "dest"
    }

    source : Call
    destination : Connection

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True) -> None:
        from typing import Any
        super().__init__(source, destination, auto_write=auto_write)
        self.dest : Any = None





class Duplicates(Arrow):

    """
    This kind of arrow indicates that a socket was duplicated to form a similar socket (example: after a call to accept()).
    """

    source : Socket
    destination : Socket





del Arrow, Call, Color, SwitchSetting, Connection, Data, Edge, Host, Process, Socket, Vertex, logger