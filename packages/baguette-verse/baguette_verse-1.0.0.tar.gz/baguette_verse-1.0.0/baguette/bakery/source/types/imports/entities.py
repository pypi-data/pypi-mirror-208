"""
This module contains Vertex subclasses for this behavioral package.
"""

from ....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import UniqueVertex, Vertex

__all__ = ["Import"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Import(UniqueVertex):
    
    """
    An import vertex. Shows the use of a DLL or equivalent.
    """

    __slots__ = {
        "__name" : "The name of the import file.",
        "path" : "The path to the file.",
        "length" : "The size in bytes of the file."
    }

    __pickle_slots__ = {
        "name",
        "path",
        "length"
    }

    __suspicious_keyword_names = {
        "crypt",
        "advapi",
        "kernel",
        "sock"
    }

    default_color = ColorSetting(Color(150, 150, 0))
    default_size = SizeSetting(0.75)

    suspicious_import_color = ColorSetting(Color(255, 150, 0))

    def __init__(self, *, parent: Vertex | None = None) -> None:
        super().__init__(parent=parent)
        self.__name : str = ""
        self.path : str = ""
        self.length : int = 0

    @property
    def name(self) -> str:
        """
        The name of the imported library.
        """
        return self.__name

    @name.setter
    def name(self, n : str):
        from ...config import ColorSetting
        if not isinstance(n, str):
            raise TypeError("Expected str, got " + repr(type(n).__name__))
        self.__name = n
        self.color = self.default_color
        for kw in self.__suspicious_keyword_names:
            if kw in n.lower():
                self.color = self.suspicious_import_color
                break
    
    @property
    def label(self) -> str:
        """
        Returns a label for this Import node.
        """
        return "Import {}".format(self.__name.lower())
    




del Color, ColorSetting, SizeSetting, UniqueVertex, Vertex, logger