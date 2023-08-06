"""
This module defines some useful tools for MetaGraphs.
"""

from types import UnionType

__all__ = ["class_union"]





def class_union(*cls : type) -> type | UnionType:
    """
    Creates the union of classes, as sum operator but for the "|" operator.
    """
    for c in cls:
        if not isinstance(c, type):
            raise TypeError("Expected types, got " + repr(type(c).__name__))
    l = list(cls)
    if not l:
        raise ValueError("Expected at least one type.")
    c = l.pop()
    while l:
        c = c | l.pop()
    return c





del UnionType