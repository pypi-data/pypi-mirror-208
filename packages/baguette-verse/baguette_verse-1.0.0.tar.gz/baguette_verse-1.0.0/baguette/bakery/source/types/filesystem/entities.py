"""
This module contains Vertex subclasses for this behavioral package.
"""

import pathlib

from ....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import UniqueVertex, Vertex

__all__ = ["File", "Directory", "Handle"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class File(UniqueVertex):

    """
    A file vertex. Represents a (real) file opened during execution.
    """

    __slots__ = {
        "__path" : "The path to the file in the file system",
    }

    __pickle_slots__ = {
        "path"
    }

    default_color = ColorSetting(Color(0, 255, 50))
    default_size = SizeSetting(2.5)

    deleted_file_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, parent: Vertex | None = None) -> None:
        from pathlib import PurePath
        super().__init__(parent=parent)
        self.__path : PurePath | None = None

    @property
    def path(self) -> pathlib.PurePath:
        """
        The absolute path to the file.
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path

    @path.setter
    def path(self, value : str):
        from ...utils import path_factory
        self.__path = path_factory(value)
    
    @property
    def name(self) -> str:
        """
        The name of the file (tail of the path).
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.name
    
    @property
    def extension(self) -> str:
        """
        The file extention (lowercased without '.').
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.suffix.lower().replace(".", "")
    
    @property
    def label(self) -> str:
        """
        Returns a label for this File node.
        """
        return 'File "' + self.name + '"'
    




class Directory(UniqueVertex):

    """
    A directory vertex. Represents a (real) directory opened during execution.
    """

    __slots__ = {
        "__path" : "The path to the directory in the file system",
    }

    __pickle_slots__ = {
        "path"
        }
    
    default_color = ColorSetting(Color(0, 100, 0))
    default_size = SizeSetting(2.5)

    deleted_directory_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, parent: Vertex | None = None) -> None:
        from pathlib import PurePath
        super().__init__(parent=parent)
        self.__path : PurePath | None = None

    @property
    def path(self) -> pathlib.PurePath:
        """
        The absolute path to the directory.
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path

    @path.setter
    def path(self, value : str):
        from ...utils import path_factory
        self.__path = path_factory(value)
    
    @property
    def name(self) -> str:
        """
        The name of the directory (tail of the path).
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        return self.__path.name if self.__path.name else self.__path.drive
    
    @property
    def label(self) -> str:
        """
        Returns a label for this Directory node.
        """
        if self.__path is None:
            raise RuntimeError("Got a File without path.")
        if not self.__path.name:
            return 'Drive "' + self.name.replace(":", "") + '"'
        return 'Directory "' + self.name + '"'
    




class Handle(UniqueVertex):

    """
    A handle vertex. Represents a file handle, used when a program opens a file.
    """

    __slots__ = {
        # For all objects:
        "synchronize" : "If the handle can perform synchronization operations on the object",

        # For file objects:
        "read" : "If the handle has the right to read the file",
        "write" : "If the handle has the right to write to the file",
        "append" : "If the handle has the right to append to the file",
        "execute" : "If the handle has the right to execute the file",
        "read_attributes" : "If the handle has the right to read file attributes",
        "write_attributes" : "If the handle can change the file attributes",
        "read_extended_attributes" : "If the handle can read the extended file attributes",
        "write_extended_attributes" : "If the handle can change the extended file attributes",

        # For directory objects:
        "list_directory" : "If the handle has the right to list the items in the given directory",
        "traverse" : "If the handle has the right to traverse the directory and use it to access subforlders/files"
    }

    __pickle_slots__ = {
        "synchronize",
        "read",
        "write",
        "append",
        "execute",
        "read_attributes",
        "write_attributes",
        "read_extended_attributes",
        "write_extended_attributes",
        "list_directory",
        "traverse"
    }

    default_color = ColorSetting(Color(128, 255, 50))
    default_size = SizeSetting(1.5)

    def __init__(self, *, parent: Vertex | None = None) -> None:
        super().__init__(parent=parent)

        self.synchronize : bool = False

        self.read : bool = False
        self.write : bool = False
        self.append : bool = False
        self.execute : bool = False
        self.read_attributes : bool = False
        self.write_attributes : bool = False
        self.read_extended_attributes : bool = False
        self.write_extended_attributes : bool = False

        self.list_directory : bool = False
        self.traverse : bool = False
    
    @property
    def file(self) -> File | Directory:
        """
        Returns the file (or directory) node that this handle is working on.
        """
        from .relations import UsesDirectory, UsesFile
        for e in self.edges:
            if isinstance(e, UsesFile | UsesDirectory):
                return e.destination
        raise RuntimeError("Got a Handle working on no File or Directory.")





del Color, ColorSetting, SizeSetting, UniqueVertex, Vertex, logger, pathlib