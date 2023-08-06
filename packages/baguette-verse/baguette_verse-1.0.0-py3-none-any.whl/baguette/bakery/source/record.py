from typing import Any, Dict, Iterable, Union
# from Viper.frozendict import frozendict

_hashing = set()

class record:

    """
    A class to hold key-values informations. Similar to dict but works with attributes instead.
    """

    __slots__ = ("_record",)
    _depth = 0

    def __init__(self, **kwargs : Any) -> None:
        super().__setattr__("_record", None)

        def transform(v):
            if isinstance(v, list):
                return tuple(v)
            if isinstance(v, set):
                return frozenset(v)
            if isinstance(v, dict):
                return record(**v)
            return v

        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except:
                pass

    def __setattr__(self, name: str, value: Any) -> None:
        # if name in super().__getattribute__("__dict__"):
        #     raise ValueError("Cannot change attribute '{}' for this object.".format(name))
        try:
            hash(value)
        except:
            raise TypeError("record object can only hold hashable types, not " + repr(value.__class__.__name__))
        # from graph import vertex, edge, graph
        # if isinstance(value, (vertex, edge, graph)):
        #     raise TypeError("Cannot hold vertex, edge or graphs in record objects")
        if super().__getattribute__("_record") == None:
            super().__setattr__("_record", {})
        super().__getattribute__("_record")[name] = value
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if super().__getattribute__("_record") != None and name in super().__getattribute__("_record"):
                return super().__getattribute__("_record")[name]
            else:
                raise AttributeError("No such entry : " + repr(name))
    
    def __delattr__(self, name: str) -> None:
        # if name in super().__getattribute__("__dict__"):
        #     raise ValueError("Cannot delete attribute '{}' for this object.".format(name))
        if super().__getattribute__("_record") != None and name in super().__getattribute__("_record"):
            super().__getattribute__("_record").pop(name)
            if not super().__getattribute__("_record"):
                super().__setattr__("_record", None)
    
    def __dir__(self) -> Iterable[str]:
        if super().__getattribute__("_record") == None:
            return ()
        return super().__getattribute__("_record").keys()

    def __repr__(self) -> str:
        if super().__getattribute__("_record") == None:
            return "record()"
        return "record(" + ", ".join(str(k) + " = " + repr(v) for k, v in super().__getattribute__("_record").items()) + ")"

    def __str__(self) -> str:
        if super().__getattribute__("_record") == None:
            return "record{}"
        return "record{\n\t" + "\n\t".join(str(k) + " : " + repr(v) for k, v in super().__getattribute__("_record").items()) + "\n}"
    
    def __reduce__(self) -> Union[str, tuple[Any, ...]]:
        return self.__class__, (), super().__getattribute__("_record") or {}
    
    def __copy__(self) -> "record":
        return record(**super().__getattribute__("_record"))
    
    def __deepcopy__(self, memo : Dict[int, Any]) -> "record":
        from copy import deepcopy
        return record(**{name : deepcopy(value, memo) for name, value in (super().__getattribute__("_record") or {}).items()})
    
    def __setstate__(self, state : Dict[str, Any]) -> None:
        for k, v in state.items():
            setattr(self, k, v)
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, record):
            return False
        return super().__getattribute__("_record") == super(record, o).__getattribute__("_record")
    
    def __hash__(self) -> int:
        if super().__getattribute__("_record") == None:
            return hash(0)
        h = 0
        for k, v in (super().__getattribute__("_record") or {}).items():
            if id(k) in _hashing:
                hk = -1
            else:
                _hashing.add(id(k))
                hk = hash(k)
                _hashing.remove(id(k))
            if id(v) in _hashing:
                hv = -1
            else:
                _hashing.add(id(v))
                hv = hash(v)
                _hashing.remove(id(v))            
            h += hk - hv
        return hash(h)


del Any, Dict, Iterable, Union