"""
This module contains Vertex subclasses for this behavioral package.
"""

from abc import abstractmethod
from types import NoneType
from typing import Any, Callable, Generic, Optional, TypeVar

from ....logger import logger
from ...config import ColorSetting, SizeSetting
from ...colors import Color
from ...graph import UniqueVertex, Vertex

__all__ = ["Key", "KeyEntry", "Handle"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class Key(UniqueVertex):

    """
    A registry key vertex. Represents a key without its associated value(s).
    """

    __slots__ = {
        "__name" : "The local name of the registry key int the registry tree."
    }

    __pickle_slots__ = {
        "name"
    }

    default_color = ColorSetting(Color(0, 150, 255))
    default_size = SizeSetting(1.5)

    unprintable_key_color = ColorSetting(Color(255, 0, 50))
    deleted_key_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, parent: Vertex | None = None) -> None:
        super().__init__(parent=parent)
        self.__name : str = ""

    @property
    def name(self) -> str:
        """
        The (local) name of the registry key.
        """
        return self.__name
    
    @name.setter
    def name(self, value : str):
        if not isinstance(value, str):
            raise TypeError("Expected str, got " + repr(type(value).__name__))
        if "\\" in value:
            raise ValueError("'\\' not permitted in a registry key name")
        if len(value) > 255:
            raise ValueError("Key name is too long to be allowed by registry")
        self.__name = value.lower().title().replace("\x00", "\uFFFD")
        if not self.printable:
            from ....logger import logger
            from ...config import ColorSetting
            logger.info("Got an unprintable registry key.")
            self.color = self.unprintable_key_color
    
    @property
    def path(self) -> str:
        """
        The global key name (path from root key and all sub-keys to reach this key included).
        """
        if not self.parent_key:
            return self.name
        return self.parent_key.path + "\\" + self.name

    @property
    def printable(self) -> bool:
        """
        True if the (relative) key name is printable.
        """
        return self.name.isprintable() and "\uFFFD" not in self.name

    @property
    def parent_key(self) -> Optional["Key"]:
        """
        The parent key of this registry key if any (None for root keys).
        """
        from .relations import HasSubKey
        for e in self.edges:
            if isinstance(e, HasSubKey) and e.destination is self and isinstance(e.source, Key):
                return e.source
    
    @property
    def entries(self) -> list["KeyEntry"]:
        """
        All the known entries of this key.
        """
        from .relations import HasEntry
        return [e.destination for e in self.edges if isinstance(e, HasEntry)]
    
    @property
    def label(self) -> str:
        """
        The label of this node.
        """
        return "Key " + self.name





T = TypeVar("T")

class KeyEntry(UniqueVertex, Generic[T]):

    """
    A registry key entry vertex. This represents a value (with name, type and actual value) that a registry key has.
    """

    __slots__ = {
        "__name" : "The name of the registry key entry",
        "__value" : "The actual value stored in this entry"
    }

    __pickle_slots__ = {
        "name",
        "value"
    }

    default_color = ColorSetting(Color(0, 255, 255))
    default_size = SizeSetting(1.0)

    deleted_key_entry_color = ColorSetting(Color(100, 100, 100))

    def __init__(self, *, parent: Optional["Vertex"] = None) -> None:
        super().__init__(parent=parent)
        self.__name : str = ""

    @property
    def name(self) -> str:
        """
        The name of this registry key entry.
        """
        return self.__name
    
    @name.setter
    def name(self, value : str):
        if not isinstance(value, str):
            raise TypeError("Expected str, got " + repr(type(value).__name__))
        if len(value) > 16383:
            raise ValueError("Registry key value name is too long.")
        self.__name = value
    
    py_type : type[T] | None = None
    reg_type : str | None = None

    __types : dict[str, type["KeyEntry"]] = {}

    def __init_subclass__(cls) -> None:
        res = super().__init_subclass__()
        from types import GenericAlias, UnionType
        if not isinstance(cls.py_type, type | GenericAlias | UnionType) or not isinstance(cls.reg_type, str):
            raise ValueError("Cannot subclass KeyEntry without setting 'py_type' and 'reg_type' to type and str values.")
        if cls.reg_type in KeyEntry.__types:
            raise KeyError("A subclass of KeyEntry for reg_type '{}' already exists.".format(cls.reg_type))
        KeyEntry.__types[cls.reg_type] = cls
        return res
    
    @staticmethod
    def key_types() -> list[str]:
        """
        Lists all registered KeyEntry subclasses names (the native name of the entry type they represent).
        Use 'KeyEntry[<name>]' to get one of the corresponding subclasses.
        """
        return list(KeyEntry.__types)

    def __class_getitem__(cls, key : type | str):
        if isinstance(key, str) and key in KeyEntry.__types:
            return KeyEntry.__types[key]
        return super().__class_getitem__(key) # type: ignore
                
    @property
    def value(self) -> T:
        """
        The value of the entry.
        """
        return self.__value

    @value.setter
    @abstractmethod
    def value(self, val : T):
        raise NotImplementedError

    def _set_value(self, val : T):
        """
        Internal method to change the value in the base class.
        """
        self.__value = val
    
    @abstractmethod
    def process_value(self, val : str | int) -> None:
        """
        Processes the raw value from an API node and sets the result as this entry's value.
        """
        raise NotImplementedError
                    
    @property
    def key(self) -> Key:
        """
        The registry Key that this entry is part of.
        """
        from .relations import HasEntry
        for e in self.edges:
            if isinstance(e, HasEntry):
                return e.source
        raise RuntimeError("Found a KeyEntry that has not been affected to a Key")
    
    @property
    def label(self) -> str:
        return "KeyEntry"
    




class Key_DWORD_Entry(KeyEntry[int]):

    py_type = int
    reg_type = "REG_DWORD"
    
    @property
    def value(self) -> int:
        return super().value
    
    @value.setter
    def value(self, val : int):
        if not isinstance(val, int):
            raise TypeError("Expected int, got " + repr(type(val).__name__))
        self._set_value(val)

    def process_value(self, val: int):
        if not isinstance(val, int):
            raise TypeError("Expected int, got " + repr(type(val).__name__))
        self.value = val

class Key_QWORD_LITTLE_ENDIAN_Entry(Key_DWORD_Entry):
    reg_type = "REG_QWORD_LITTLE_ENDIAN"
    
class Key_DWORD_LITTLE_ENDIAN_Entry(Key_DWORD_Entry):
    reg_type = "REG_DWORD_LITTLE_ENDIAN"
    
class Key_DWORD_BIG_ENDIAN_Entry(Key_DWORD_Entry):
    reg_type = "REG_DWORD_BIG_ENDIAN"
    
class Key_QWORD_Entry(Key_DWORD_Entry):
    reg_type = "REG_QWORD"
    




class Key_SZ_Entry(KeyEntry[str]):

    py_type = str
    reg_type = "REG_SZ"
    
    @property
    def value(self) -> str:
        return super().value
    
    @value.setter
    def value(self, val : str):
        if not isinstance(val, str):
            raise TypeError("Expected str, got " + repr(type(val).__name__))
        self._set_value(val)

    def process_value(self, val: str):
        if not isinstance(val, str):
            raise TypeError("Expected str, got " + repr(type(val).__name__))
        self.value = val

class Key_EXPAND_SZ_Entry(Key_SZ_Entry):
    reg_type = "REG_EXPAND_SZ"
    
class Key_LINK_Entry(Key_SZ_Entry):
    reg_type = "REG_LINK"





class Key_MULTI_SZ_Entry(KeyEntry[list[str]]):

    py_type = list[str]
    reg_type = "REG_MULTI_SZ"
    
    @property
    def value(self) -> list[str]:
        return super().value
    
    @value.setter
    def value(self, val : list[str]):
        if not isinstance(val, list) or any(not isinstance(vi, str) for vi in val):
            raise TypeError("Expected list of str, got " + repr(type(val).__name__))
        self._set_value(val)

    def process_value(self, val: str):
        if not isinstance(val, str):
            raise TypeError("Expected str, got " + repr(type(val).__name__))
        if val.endswith("\x00"):
            v = val[:-1]
        else:
            v = val
        self.value = v.split("\x00")





class Key_BINARY_Entry(KeyEntry[bytes]):

    py_type = bytes
    reg_type = "REG_BINARY"
    
    @property
    def value(self) -> bytes:
        return super().value
    
    @value.setter
    def value(self, val : bytes):
        if not isinstance(val, bytes):
            raise TypeError("Expected bytes, got " + repr(type(val).__name__))
        self._set_value(val)

    def process_value(self, val: str):
        if not isinstance(val, str):
            raise TypeError("Expected str, got " + repr(type(val).__name__))
        self.value = val.encode()





class Key_NONE_Entry(KeyEntry[NoneType]):

    py_type = type(None)
    reg_type = "REG_NONE"
    
    @property
    def value(self) -> NoneType:
        return None
    
    @value.setter
    def value(self, val : NoneType):
        raise ValueError("Cannot set value of REG_NONE registry key entry")
    
    def process_value(self, val: str):
        pass
    




class Handle(UniqueVertex):

    """
    A handle vertex. Represents a registry key handle, used when a program opens a registry key.
    """

    default_color = ColorSetting(Color(128, 203, 153))
    default_size = SizeSetting(1.0)

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        super().__init__(parent=parent)
    
    @property
    def key(self) -> Key:
        """
        Returns the key node that this handle is working on.
        """
        from .relations import UsesKey
        for e in self.edges:
            if isinstance(e, UsesKey):
                return e.destination
        raise RuntimeError("Key handle with no attached key")
    




del Any, Color, ColorSetting, SizeSetting, Generic, Optional, TypeVar, UniqueVertex, Vertex, logger, T, Callable, NoneType, abstractmethod