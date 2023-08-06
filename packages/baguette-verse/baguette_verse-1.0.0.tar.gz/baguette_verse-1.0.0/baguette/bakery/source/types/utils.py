"""
This module defines some useful functions for manipulating the BAGUETTE graph typing system.
"""

from functools import cache
from types import ModuleType
from .. import types as type_package
from ..graph import Edge, Vertex

__all__ = ["types", "relations", "relation_types"]





@cache
def types(mod : ModuleType = type_package) -> set[type[Vertex]]:
    """
    Returns the list of available Vertex types available in a given module or package (recursively). Defaults to the BAGUETTE's types package.
    """
    from ..graph import Vertex
    from types import ModuleType

    if not isinstance(mod, ModuleType):
        raise TypeError("Expected module or package, got " + repr(type(mod).__name__))

    type_set = set()
    package_name = mod.__name__

    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type) and issubclass(value, Vertex):
            type_set.add(value)
        elif isinstance(value, ModuleType):
            name = value.__name__.rpartition(".")[0]
            if name == package_name:
                type_set.update(types(value))
    
    return type_set





@cache
def relations(mod : ModuleType = type_package) -> set[type[Edge]]:
    """
    Returns the list of available Edge and Arrow types available in a given module or package (recursively). Defaults to the BAGUETTE's types package.
    """
    from ..graph import Edge
    from types import ModuleType

    if not isinstance(mod, ModuleType):
        raise TypeError("Expected module or package, got " + repr(type(mod).__name__))

    type_set = set()
    package_name = mod.__name__

    for name in dir(mod):
        value = getattr(mod, name)
        if isinstance(value, type) and issubclass(value, Edge):
            type_set.add(value)
        elif isinstance(value, ModuleType):
            name = value.__name__.rpartition(".")[0]
            if name == package_name:
                type_set.update(types(value))
    
    return type_set





@cache
def relation_types(edge_class : type[Edge]) -> tuple[type[Vertex], type[Vertex]]:
    """
    Given an Edge or Arrow subclass, gives the best type hints for the source and destination vertices.
    Defaults to (Vertex, Vertex) when no annotations exist.
    """
    from typing import get_type_hints
    from ..graph import Edge, Vertex

    if not isinstance(edge_class, type) or not issubclass(edge_class, Edge):
        raise TypeError("Expected Edge subclass, got " + repr(type(edge_class).__name__))

    hints = get_type_hints(edge_class)
    return hints.get("source", Vertex), hints.get("destination", Vertex)
    




del cache, ModuleType, type_package, Edge, Vertex