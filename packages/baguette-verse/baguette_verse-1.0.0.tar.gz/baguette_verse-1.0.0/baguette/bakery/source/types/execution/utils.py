"""
This module holds the CallHandler class of the execution behavioral package.
"""

from typing import Any, Callable

from Viper.meta.iterable import InstancePreservingClass

from ...utils import chrono
from .entities import Call


class CallHandler(metaclass = InstancePreservingClass):

    """
    The class for all handlers of system calls.
    Upon creation, a system call vertex will look into the instances of this class to find all valid handlers and execute its integration function.
    
    To make a handler, give an integration function (performs whatever you want with the Call vertex) and as many api names as you want to match them.
    """

    __sorted : dict[str, list["CallHandler"]] = {}
    __dynamic : dict[Callable[[str], bool], list["CallHandler"]] = {}
    __scanned : set[str] = set()

    @staticmethod
    def handlers(c : Call) -> list["CallHandler"]:
        """
        The list of all the CallHandlers to call in order to integrate this Call vertex.
        """
        if c.name not in CallHandler.__scanned:
            if c.name not in CallHandler.__sorted:
                CallHandler.__sorted[c.name] = []
            for d, l in CallHandler.__dynamic.items():
                if d(c.name):
                    CallHandler.__sorted[c.name].extend(l)
        return CallHandler.__sorted[c.name]
    
    @chrono
    @staticmethod
    def integrate_chain(c : Call):
        """
        Automatically calls all handlers responsible of this Call vertex.
        """
        for h in CallHandler.handlers(c):
            h.integrate(c)

    def __init__(self, integrator : Callable[[Call], None], *names : str | Callable[[str], bool]) -> None:
        if not callable(integrator) or any(not callable(n) and not isinstance(n, str) for n in names):
            types : list[str] = [type(integrator).__name]
            types.extend(type(n).__name__ for n in names)
            raise TypeError("Expected callable, one or more str, got " + ", ".join(types[:-1]) + " and " + types[-1])
        self.__names = names
        self.__integrator = integrator
        for n in self.__names:
            if isinstance(n, str):
                if n not in CallHandler.__sorted:
                    CallHandler.__sorted[n] = []
                CallHandler.__sorted[n].append(self)
            else:
                if n not in CallHandler.__dynamic:
                    CallHandler.__dynamic[n] = []
                CallHandler.__dynamic[n].append(self)
    

    def __repr__(self) -> str:
        """
        Implements repr(self).
        """
        return "CallHandler(" + repr(self.__integrator) + ", " + ", ".join(str(n) for n in self.__names) + ")"
    

    def match(self, c : Call) -> bool:
        """
        Returns True if given Call c should be handled by this CallHandler
        """
        if c.name in self.__names:
            return True
        return False
    

    def integrate(self, c : Call):
        """
        Integrates Call c into the graph
        """
        self.__integrator(c)
    

    def __contains__(self, c : Any) -> bool:
        """
        Implements c in self.
        Equivalent to self.match(c).
        """
        if not isinstance(c, Call):
            return False
        return self.match(c)
    
    
    def __call__(self, c : Call):
        """
        Implements self(c).
        Equivalent to self.integrate(c)
        """
        self.integrate(c)