"""
This module defines functions that get quite useful when building MetaGraphs.
"""

import pathlib
from ..source.metagraph import MetaGraph

__all__ = ["import_env", "save", "load", "entries", "remove", "export_MG", "import_MG"]





def import_env(d : dict):

    """
    Imports all the necessary classes for building MetaGraphs
    """

    from ...bakery.source import types
    from ..source.metagraph import MetaGraph, MetaEdge, MetaArrow, MetaVertex
    from types import ModuleType

    l = locals().copy()
    if "l" in l:
        l.pop("l")
    l.pop("d")
    l.pop("types")

    for name in dir(types):
        val = getattr(types, name)
        if isinstance(val, ModuleType):
            l[name] = val

    d.update(l)





def save(mg : MetaGraph, name : str):
    """
    Saves the given MetaGraph in the library with the given name.
    """
    from ..source.metagraph import MetaGraph
    from os.path import dirname, sep
    from os import makedirs
    from pickle import dump

    if not isinstance(mg, MetaGraph) or not isinstance(name, str):
        raise TypeError("Expected MetaGraph, str, got " + repr(type(mg).__name__) + " and " + repr(type(name).__name__))
    
    path = dirname(__file__)
    if not path.endswith(sep):
        path += sep
    makedirs(path + "lib", exist_ok=True)
    path += "lib" + sep + name + ".pyt"

    with open(path, "wb") as f:
        dump(mg, f)





def load(name : str) -> MetaGraph:
    """
    Loads the MetaGraph with given name from the library.
    """
    from os.path import dirname, sep, isfile
    from os import makedirs
    from pickle import load

    if not isinstance(name, str):
        raise TypeError("Expected str, got " + repr(type(name).__name__))

    path = dirname(__file__)
    if not path.endswith(sep):
        path += sep
    makedirs(path + "lib", exist_ok=True)
    path += "lib" + sep + name + ".pyt"

    if not isfile(path):
        raise FileNotFoundError("Given MetaGraph name does not exist in the library.")
    
    with open(path, "rb") as f:
        return load(f)





def entries() -> list[str]:
    """
    Returns the names of all MetaGraphs existing in the library.
    """
    from os.path import dirname, sep, splitext, split
    from os import makedirs
    from glob import iglob

    path = dirname(__file__)
    if not path.endswith(sep):
        path += sep
    makedirs(path + "lib", exist_ok=True)
    path += "lib" + sep

    l = []
    for name in iglob(path + "**.pyt", recursive = True):
        l.append(splitext(split(name)[1])[0])

    return l





def remove(name : str):
    """
    Removes the given name from the MetaGraph library.
    """
    from os.path import dirname, sep, isfile
    from os import remove, makedirs

    if not isinstance(name, str):
        raise TypeError("Expected str, got " + repr(type(name).__name__))

    path = dirname(__file__)
    if not path.endswith(sep):
        path += sep
    makedirs(path + "lib", exist_ok=True)
    path += "lib" + sep + name + ".pyt"

    if not isfile(path):
        raise FileNotFoundError("No such MetaGraph : " + repr(path))

    remove(path)





def export_MG(mg : MetaGraph, file : str | pathlib.Path):
    """
    Exports the given MetaGraph to the given file
    """
    from pathlib import Path
    if not isinstance(mg, MetaGraph):
        raise TypeError("Expected MetaGraph, path, got " + repr(type(mg).__name__) + " and " + repr(type(file).__name__))
    if isinstance(file, str):
        try:
            file = Path(file)
        except:
            raise ValueError("Invalid path : '{}'".format(file))
    if not isinstance(file, Path):
        raise TypeError("Expected MetaGraph, path, got " + repr(type(mg).__name__) + " and " + repr(type(file).__name__))
    from pickle import dump
    with file.open("wb") as f:
        dump(mg, f)
    




def import_MG(file : str | pathlib.Path) -> MetaGraph:
    """
    Imports a MetaGraph from the given path.
    """
    from pathlib import Path
    if isinstance(file, str):
        try:
            file = Path(file)
        except:
            raise ValueError("Invalid path : '{}'".format(file))
    if not isinstance(file, Path):
        raise TypeError("Expected path, got " + repr(type(file).__name__))
    from pickle import load
    with file.open("rb") as f:
        return load(f)