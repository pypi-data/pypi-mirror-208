"""
This module adds some useful functions and classes for the compilation of BAGUETTE graphs.
"""

import pathlib
from functools import cache
from typing import (Any, Callable, Generic, Iterable, Iterator, ParamSpec, Set,
                    TypeVar)

from Viper.debugging.chrono import Chrono

from .graph import Edge, Vertex

__all__ = ["chrono", "extract_pickle_slots", "path_factory", "is_path", "parse_command_line", "System"]





chrono = Chrono()
chrono.enabled = False





@cache
def extract_pickle_slots(o : type[Vertex | Edge]) -> Set[str]:
    s : set[str]
    if not hasattr(o, "__pickle_slots__"):
        s = set()
    else:
        s = set(o.__pickle_slots__) # type: ignore
    for b in s:
        if not isinstance(b, str):
            raise RuntimeError("__pickle_slots__ should only contain str, got a " + repr(type(b).__name__))
    return s.union(*[extract_pickle_slots(b) for b in o.__bases__])


def path_factory(path : str) -> pathlib.PurePath:
    """
    Returns the correct path factory class for the given graph (Either WindowsPurePath or PosixPurePath).
    """
    from pathlib import PurePosixPath, PureWindowsPath

    from .graph import Graph
    platform = Graph.active_graphs()[-1].data["platform"].lower() if Graph.active_graphs() else "windows"
    if "windows" in platform:
        return PureWindowsPath(path)
    else:
        return PurePosixPath(path)


def is_path(s : str) -> bool:
    """
    Returns True if the given string represents a path for the current platform.
    """
    from pathlib import PurePosixPath, PureWindowsPath

    from .graph import Graph
    platform = Graph.active_graphs()[-1].data["platform"].lower() if Graph.active_graphs() else "windows"
    if "windows" in platform:
        forbidden = set("<>\"|?*")
        if forbidden.intersection(s):           # Contains characters that are forbidden in Windows paths.
            return False
        if s.startswith("-") or s.startswith("/"):  # Could be a path, but it is more likely to be flag
            return False
        try:
            if PureWindowsPath(s).is_reserved():
                return False
            return True
        except:
            return False
    else:
        if s.startswith("-"):                       # Could be a path, but it is more likely to be flag
            return False
        try:
            if PurePosixPath(s).is_reserved():
                return False
            return True
        except:
            return False
        

def parse_command_line(s : str) -> list[str]:
    """
    Parses command line with the syntax of the current platform's shell. Returns the argument vector.
    """
    import re

    from .graph import Graph

    platform = Graph.active_graphs()[-1].data["platform"].lower() if Graph.active_graphs() else "windows"
    if "windows" not in platform:
        RE_CMD_LEX = r'''"((?:\\["\\]|[^"])*)"|'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'"\\&|<>]+)|(\s+)|(.)'''
    else:
        RE_CMD_LEX = r'''"((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)'''

    args : list[str] = []
    accu = None   # collects pieces of one arg
    for qs, qss, esc, pipe, word, white, fail in re.findall(RE_CMD_LEX, s):
        if word:
            pass   # most frequent
        elif esc:
            word = esc[1]
        elif white or pipe:
            if accu is not None:
                args.append(accu)
            if pipe:
                args.append(pipe)
            accu = None
            continue
        elif fail:
            raise ValueError("invalid or incomplete shell string")
        elif qs:
            word = qs.replace('\\"', '"').replace('\\\\', '\\')
            if "windows" in platform:
                word = word.replace('""', '"')
        else:
            word = qss   # may be even empty; must be last

        accu = (accu or '') + word

    if accu is not None:
        args.append(accu)

    return args


P = TypeVar("P")
P2 = TypeVar("P2")
CB_Args = ParamSpec("CB_Args")

class System(Generic[P]):

    def __init__(self) -> None:
        from typing import Callable
        self.__system : set[P] = set()
        self.__population : set[P] = set()
        self.__at_collapse : list[tuple[Callable[..., None], tuple, dict[str, Any]]] = []
        collapse = self.__at_collapse
        population = self.__population
        system = self.__system

        class Particule(Generic[P2]):

            __slots__ = {"__particule"}

            def __init__(self, particule : P2) -> None:
                self.__particule = particule

            def __enter__(self):
                if self.__particule in system:
                    raise RuntimeError("Trying to entangle Particule with itself : cannot copy quantum information.")
                population.discard(self.__particule)    # type: ignore
                system.add(self.__particule)            # type: ignore
           
            def __exit__(self, exc_type, exc_value, traceback):
                if self.__particule not in system:
                    raise RuntimeError("Trying to collapse non-quantum object.")
                system.remove(self.__particule)         # type: ignore
                if not system:  # The system has fully collapsed : time for callbacks
                    for cb, args, kwargs in collapse:
                        cb(*args, **kwargs)
                    collapse.clear()
        
        self.Entangled : type[Particule[P]] = Particule

    def __contains__(self, p : P) -> bool:
        return p in self.__system
    
    def __len__(self) -> int:
        return len(self.__system)
    
    @property
    def population(self) -> set[P]:
        """
        A set of elements that can be included in the system.
        """
        return self.__population
    
    @population.setter
    def population(self, v : Iterable[P]):
        from typing import Iterable
        if not isinstance(v, Iterable):
            raise TypeError("Expected iterable, got " + repr(type(v).__name__))
        self.__population.clear()
        self.__population.update(k for k in v if k not in self)

    def include(self) -> Iterator[P]:
        """
        Yields all successives items of the population to be added to the system.
        """
        while self.__population:
            yield self.__population.pop()
    
    def add_callback(self, cb : Callable[CB_Args, None], *args : CB_Args.args, **kwargs : CB_Args.kwargs):
        """
        Adds a callable to be called with given arguments when the system completely resolves (i.e. when all entangled wave functions have collapsed).
        """
        if not self.__system:
            raise RuntimeError("Cannot program a callback before the experiment has started. Add at least one particle first.")
        self.__at_collapse.append((cb, args, kwargs))
    
    def remove_callback(self, cb : Callable[CB_Args, None]):
        """
        Removes all callbacks to the given function.
        """
        to_pop = []
        for i, (cbi, argsi, kwargsi) in enumerate(self.__at_collapse):
            if cb == cbi:
                to_pop.append(i)
        for i in reversed(to_pop):
            self.__at_collapse.pop(i)





del pathlib, cache, Any, Callable, Iterable, Iterator, ParamSpec, Set, TypeVar, Chrono, Edge, Vertex, CB_Args