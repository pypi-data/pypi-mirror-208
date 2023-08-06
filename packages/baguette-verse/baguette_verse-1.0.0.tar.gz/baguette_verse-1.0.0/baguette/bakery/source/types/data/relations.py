"""
This module contains Edge and Arrow subclasses for this behavioral package.
"""

from ....logger import logger
from ...config import WeightSetting
from ...colors import Color
from ...graph import Arrow, Edge, Vertex
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from .entities import Data, Diff

__all__ = ["IsSimilarTo", "IsAlmostIn", "IsDiffOf", "IsReadBy", "WritesInto", "HasSimilarContent"]





logger.info("Loading relations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class IsSimilarTo(Arrow):

    """
    This kind of arrow indicates two Data nodes have a similar content. The direction of the arrow indicates the order of apparition.
    """

    label : str = ""

    source : Data
    destination : Data





class IsAlmostIn(Arrow):

    """
    This kind of arrow indicates that a Data node's content might be contained in another's one. The direction of the arrow indicates the order of apparition.
    """

    label : str = ""

    source : Data
    destination : Data





class IsDiffOf(Edge):

    """
    This kind of edge indicates that a Diff node sums up operations performed on the destination node.
    """

    label : str = ""

    source : File | Connection | Handle | Socket
    destination : Diff





class IsReadBy(Arrow):

    """
    This kind of arrow indicates that a Diff node only read from a vector.
    """

    source : Diff
    destination : File | Connection | Handle | Socket





class WritesInto(Arrow):

    """
    This kind of arrow indicates that a Diff node only wrote to a vector.
    """

    source : File | Connection | Handle | Socket
    destination : Diff





class HasSimilarContent(Edge):

    """
    This kind of arrow indicates that two Diff nodes have buffers with a certain similarity rate.
    """

    __slots__ = {
        "__source_buffer" : "The name of the buffer of the source node that the similarity was computed with.",
        "__destination_buffer" : "The name of the buffer of the destination node that the similarity was computed with."
    }

    __pickle_slots__ = {
        "source_buffer",
        "destination_buffer"
    }

    label : str = ""

    source : Diff
    destination : Diff

    min_weight = WeightSetting(0.5)
    max_weight = WeightSetting(1.0)

    def __init__(self, source: Vertex, destination: Vertex, *, auto_write: bool = True) -> None:
        super().__init__(source, destination, auto_write=auto_write)
        self.__source_buffer = "global_buffer"
        self.__destination_buffer = "global_buffer"
        
    @property
    def source_buffer(self) -> str:
        """
        Returns the name of the content selected for comparison in the source node.
        """
        return self.__source_buffer
    
    @source_buffer.setter
    def source_buffer(self, name : str):
        if name not in ("read_buffer", "write_buffer", "global_buffer"):
            raise ValueError("Diff node buffers can only be set to one of ('read_buffer', 'write_buffer', 'global_buffer')")
        self.__source_buffer = name
    
    @property
    def destination_buffer(self) -> str:
        """
        Returns the name of the content selected for comparison in the destination node.
        """
        return self.__destination_buffer
    
    @destination_buffer.setter
    def destination_buffer(self, name : str):
        if name not in ("read_buffer", "write_buffer", "global_buffer"):
            raise ValueError("Diff node buffers can only be set to one of ('read_buffer', 'write_buffer', 'global_buffer')")
        self.__destination_buffer = name





del Arrow, Color, WeightSetting, Connection, Data, Diff, Edge, File, Handle, Socket, Vertex, logger