"""
This module contains Vertex subclasses for this behavioral package.
"""

from typing import Iterator, Optional

from ....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import UniqueVertex, Vertex
from ...utils import chrono
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from .utils import IOOperation

__all__ = ["Data", "Diff"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Data(UniqueVertex):
    
    """
    A data vertex. Represents data read, written or appended to a file.
    """

    similarity_threshold = 0.75

    __slots__ = {
        "data" : "The bytes data exchanged through the handle",
        "length" : "The length of the data in bytes",
        "entropy" : "The byte-wise entropy of the message",
        "time" : "The time at which this message was seen",
        "isprintable" : "Indicates if a message can be converted to a UTF-8 str and contains only printable characters",
        "__initialized" : "Indicates if this Vertex can be compared to other Data Vertices"
    }

    __pickle_slots__ = {
        "data",
        "length",
        "entropy",
        "time",
        "isprintable"
    }

    default_color = ColorSetting(Color(0.5882352941176471, 1.0, 1.0))
    default_size = SizeSetting(0.5)

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        super().__init__(parent=parent)
        self.__initialized = False
        self.data : bytes = b""
        self.length : int = 0
        self.entropy : float = 0.0
        self.time : float = 0.0
        self.isprintable : bool = False
    
    @property
    def vector(self) -> Handle | Socket:
        """
        The Handle or Socket Vertex that this Data node is Conveying data to or from.
        """
        from ..filesystem import Handle
        from ..network import Socket
        for u in self.neighbors():
            if isinstance(u, Handle | Socket):
                return u
        raise RuntimeError("Got a data node without vector.")
    
    @chrono
    def set_data(self, data : str):
        """
        Writes the corresponding data to the node.
        Also computes all related metrics.
        """
        from .utils import entropy
        self.data = data.encode("utf-8")
        self.length = len(self.data)
        self.entropy = entropy(self.data)
        self.isprintable = data.isprintable()
    
    def compare(self):
        """
        Links the node to other similar nodes.
        """
        from .relations import IsSimilarTo
        from .utils import levenshtein_similarity
        self.__initialized = True
        for d in Data:
            if (1 - Data.similarity_threshold) * max(len(d.data), len(self.data)) < abs(len(d.data) - len(self.data)):      # Size difference is too high, similarity will be below threshold
                continue
            if d is not self and d.__initialized:
                s1 = levenshtein_similarity(d.data, self.data, Data.similarity_threshold)
                if s1 < Data.similarity_threshold:
                    continue
                if self.time < d.time:
                    l1 = IsSimilarTo(self, d)
                else:
                    l1 = IsSimilarTo(d, self)
                l1.weight = s1
                # s2 = levenshtein_subset_similarity(d.data, self.data)
                # if self.time < d.time:
                #     l2 = IsAlmostIn(self, d)
                # else:
                #     l2 = IsAlmostIn(d, self)
                # l2.weight = s2





class Diff(UniqueVertex):

    """
    A diff vertex. This represents all the information gathered on a file's content during the lifetime of a handle.
    """

    similarity_threshold = 0.90

    __slots__ = {
        "read" : "The content of the read diff file",
        "read_type" : "The file type determined by libmagic from what has been read",
        "written" : "The content of the write diff file",
        "written_type" : "The file type determined by libmagic from what has been written",
        "glob" : "The content of the global diff file",
        "glob_type" : "The file type determined by libmagic from the final state of the file",
        "read_total" : "The total amount of bytes that were read",  # Counts double if you read twice the same byte
        "read_space" : "The amount of bytes that were read in the file",    # This one only counts one
        "written_total" : "The total amount of bytes that were written",
        "written_space" : "The amount of bytes that were written in the file",
        "glob_space" : "The amount of bytes that were accessed in the file",
        "read_entropy" : "The amount of entropy that was read from the file",
        "written_entropy" : "The amount of entropy that was written to the file",
        "glob_entropy" : "The entropy that resulted in the file from all operations",
        "printable_rate" : "Indicates how much of the final state of the file only contains printable characters",
        "encoding" : "A valid encoding for the final file",
        "__initialized" : "Indicates if this Vertex can be compared to other Diff Vertices",
        "__reader_difffile" : "The DiffFile that will store the result of all reading operations",
        "__writer_difffile" : "The DiffFile that will store the result of all writing operations",
        "__glob_difffile" : "The DiffFile that will store the result of all IO operations",
        "__operations" : "The list of all operations that appear in the Diff node"
    }

    __pickle_slots__ = {
        "read",
        "read_type",
        "written",
        "written_type",
        "glob",
        "glob_type",
        "read_total",
        "read_space",
        "written_total",
        "written_space",
        "glob_space",
        "read_entropy",
        "written_entropy",
        "glob_entropy",
        "printable_rate",
        "encoding",
    }

    _active_target_diff : dict[File | Connection, "Diff"] = {}
    _active_vector_diff : dict[Handle | Socket, "Diff"] = {}

    default_color = ColorSetting(Color(50, 150, 255))
    default_size = SizeSetting(1.5)

    min_size = SizeSetting(0.5)
    max_size = SizeSetting(2.5)

    diff_low_entropy_color = ColorSetting(Color(50, 150, 255))
    diff_high_entropy_color = ColorSetting(Color(255, 50, 150))

    def __init__(self, *, parent: Optional["Vertex"] = None) -> None:
        from .utils import DiffFile, IOOperation
        super().__init__(parent=parent)
        self.__initialized : bool = False
        self.__reader_difffile = DiffFile()
        self.__writer_difffile = DiffFile()
        self.__glob_difffile = DiffFile()
        self.__operations : list[IOOperation] = []
        self.read : bytes = b""
        self.read_type : list[str] = []
        self.written : bytes = b""
        self.written_type : list[str] = []
        self.glob : bytes = b""
        self.glob_type : list[str] = []
        self.read_total : int = 0
        self.read_space : int = 0
        self.written_total : int = 0
        self.written_space : int = 0
        self.glob_space : int = 0
        self.read_entropy : float = 0.0
        self.written_entropy : float = 0.0
        self.glob_entropy : float = 0.0
        self.printable_rate : float = 0.0
        self.encoding : str = "raw"

    @property
    def read_buffer(self) -> bytes:
        """
        The current content of the read diff file.
        """
        return self.__reader_difffile.dump()
    
    @property
    def write_buffer(self) -> bytes:
        """
        The current content of the write diff file.
        """
        return self.__writer_difffile.dump()
    
    @property
    def glob_buffer(self) -> bytes:
        """
        The current content of the global diff file.
        """
        return self.__glob_difffile.dump()
    
    @property
    def content(self) -> tuple[bytes, bytes, bytes]:
        """
        The current content of the read, write and global diff files.
        """
        return self.read_buffer, self.write_buffer, self.glob_buffer
        
    def last_pos(self) -> int:
        """
        Returns the offset after the las operation performed in this Diff node.
        """
        if self.__operations:
            return self.__operations[-1].stop
        else:
            return 0
    
    @chrono
    def add_operation(self, op : IOOperation):
        """
        Registers a new IO operation to this Diff node.
        """
        from .utils import Read, Write
        self.__operations.append(op)
        self.__glob_difffile.write(op.data, op.start)
        if isinstance(op, Read):
            self.__reader_difffile.write(op.data, op.start)
        elif isinstance(op, Write):
            self.__writer_difffile.write(op.data, op.start)
    
    @chrono
    def compute_data(self):
        """
        Computes the values of all the attributes given the state of operations and DiffFiles.
        """
        from magic import Magic

        from ...config import CompilationParameters
        from ...graph import Graph
        from .relations import (HasSimilarContent, IsDiffOf, IsReadBy,
                                WritesInto)
        from .utils import (Read, Write, entropy, levenshtein_similarity,
                            printable_rate)

        analyzer = Magic(keep_going=True, uncompress=True)
        r, w, g = self.content
        self.read, self.written, self.glob = r, w, g
        self.read_type = analyzer.from_buffer(r).split("\\012- ")
        self.written_type = analyzer.from_buffer(w).split("\\012- ")
        self.glob_type = analyzer.from_buffer(g).split("\\012- ")
        self.read_total = sum(len(op.data) for op in self.__operations if isinstance(op, Read))
        self.written_total = sum(len(op.data) for op in self.__operations if isinstance(op, Write))
        self.read_space = len(r)
        self.written_space = len(w)
        self.glob_space = len(g)
        self.read_entropy = entropy(r)
        self.written_entropy = entropy(w)
        self.glob_entropy = entropy(g)
        self.printable_rate, self.encoding = printable_rate(g)

        if not r and w:
            for e in self.edges:
                if isinstance(e, IsDiffOf):
                    WritesInto(e.source, e.destination)
                    e.delete()
                    for G in Graph.active_graphs():
                        G.remove(e)
        elif not w and r:
            for e in self.edges:
                if isinstance(e, IsDiffOf):
                    IsReadBy(e.destination, e.source)
                    e.delete()
                    for G in Graph.active_graphs():
                        G.remove(e)

        if CompilationParameters.SkipLevenshteinForDiffNodes:
            return
        
        for u in Diff:
            if u not in self.neighbors() and u is not self:
                lw, ls, ld = 0.0, "", ""
                for sn, sb in zip(("read_buffer", "write_buffer", "global_buffer"), (r, w, g)):
                    if sb:
                        for un, ub in zip(("read_buffer", "write_buffer", "global_buffer"), u.content):
                            if (1 - Diff.similarity_threshold) * max(len(sb), len(ub)) < abs(len(sb) - len(ub)):      # Size difference is too high, similarity will be below threshold
                                continue
                            if ub:
                                s = levenshtein_similarity(sb, ub, Diff.similarity_threshold)
                                if s >= lw:
                                    lw = s
                                    ls = sn
                                    ld= un
                if ls and lw >= Diff.similarity_threshold:      # Heuristic is not perfect : checking that the threshold has indeed been reached!
                    l = HasSimilarContent(self, u)
                    l.weight = lw * (l.max_weight - l.min_weight) + l.min_weight        # 0 <= lw <= 1
                    l.source_buffer = ls
                    l.destination_buffer = ld
    
    @property
    def label(self) -> str:
        """
        The name of the node to display. It is the global data type.
        """
        if len(self.glob_type) == 1:
            return self.glob_type[0]
        return " | ".join(t for t in self.glob_type if t != "data")

    @property
    def vectors(self) -> Iterator[Handle | Socket]:
        """
        The Handle or Socket Vertices that this Diff node is interacting with.
        """
        from ..filesystem import Handle
        from ..network import Socket
        for u in self.neighbors():
            if isinstance(u, Handle | Socket):
                yield u
    
    @property
    def targets(self) -> Iterator[File | Connection]:
        """
        The File or Connection Vertices that this Diff node is interacting with.
        """
        from ..filesystem import File
        from ..network import Connection
        for u in self.neighbors():
            if isinstance(u, File | Connection):
                yield u





del Color, ColorSetting, SizeSetting, Connection, File, Handle, IOOperation, Iterator, Optional, Socket, UniqueVertex, Vertex, chrono, logger