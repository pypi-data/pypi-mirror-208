"""
This module defines an evaluator class, which is a pickable Python function.
"""

from typing import Any, Generic, TypeVar, ParamSpec




X = TypeVar("X")
R = TypeVar("R")

class Evaluator(Generic[X, R]):

    """
    Allows you to define simple Python functions that can be pickled without existing in a static module.
    To create one, you must give an evaluable expression containing a single global variable x.
    """
    
    def __init__(self, code : str) -> None:
        from typing import Callable
        self.__code = ""
        self.__compiled : Callable[[X], R] | None = None
        self.code = code

    def __compile(self):
        """
        Compiles the function with the associated evaluable code.
        """
        try:
            compile(self.__code, "test_compile", "eval")
        except Exception as E:
            raise E from None
        code = "def evaluator_func(x):\n\treturn " + self.__code
        env = {}
        exec(code, env)
        self.__compiled = env["evaluator_func"]
    
    @property
    def code(self) -> str:
        """
        The evaluable code of function (Python code).
        """
        return self.__code
    
    @code.setter
    def code(self, code : str):
        if not isinstance(code, str):
            raise TypeError("Expected str, got " + repr(type(code).__class__))
        old_code = self.__code
        try:
            self.__code = code
            self.__compile()
        except SyntaxError as E:
            self.__code = old_code
            raise SyntaxError("Cannot set function code as it contains a syntax error.") from E
        self.__code = code
    
    def __str__(self) -> str:
        return "lambda x : " + self.__code
    
    def __repr__(self) -> str:
        return "Evaluator(" + repr(self.__code) + ")"
    
    def __call__(self, x : X) -> R:
        if not self.__compiled:
            raise RuntimeError("Tried to call an empty Evaluator")
        try:
            return self.__compiled(x)
        except BaseException as E:
            raise E from None
    
    def __getstate__(self) -> dict[str, Any]:
        return {"code" : self.__code}
    
    def __setstate__(self, state : dict[str, Any]):
        self.__code = ""
        self.__compiled = None
        for name, value in state.items():
            setattr(self, name, value)