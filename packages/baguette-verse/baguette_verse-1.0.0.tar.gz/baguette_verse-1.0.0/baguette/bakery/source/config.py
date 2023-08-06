"""
This module contains configuration objects for execution graphs.
"""

from abc import abstractmethod
from typing import Any, Generic, Self, TypeVar
from .colors import Color
from Viper.meta.decorators import hybridmethod, staticproperty

__all__ = ["Setting", "ColorSetting", "SizeSetting", "SwitchSetting", "WeightSetting", "CompilationParameters", "ajust_for_background_color"]





T = TypeVar("T")

class Setting(Generic[T]):

    """
    Just a class to hold settings for BAGUETTE. Cannot be used as such, you need to specialize it as a generic class of the type of object the setting will hold:

    >>> s = Setting(Color.white)
    ValueError: Cannot instanciate unspecialized Setting class
    >>> ColorMap = Setting[Color]
    >>> s = ColorMap(Color.white)
    >>> class A:
    ...     x = ColorMap(Color.red)
    ... 
    >>> a = A()
    >>> a.x
    Color.red
    >>> a.x = 1
    TypeError: Expected Color, got 'int'
    >>> a.x = Color.yellow
    >>> a.x
    Color.yellow
    >>> A.x         # Note that settings are actually affected at a class level.
    Color.yellow
    >>> del a.x
    >>> a.x
    Color.red
    
    The advantage of Settings over simple properties is that references are hold at the class level to all the settings declared in all class namespaces:

    >>> Setting.list()
    {(<class '__main__.A'>, 'x'): <baguette.bakery.source.config.Setting[Color] object at 0x0000016345399590>}
    >>> IntMap = Setting[int]
    >>> IntMap.list()
    {}
    >>> ColorMap.list()
    {(<class '__main__.A'>, 'x'): <baguette.bakery.source.config.Setting[Color] object at 0x0000016345399590>}
    >>> a.x = Color.yellow
    >>> Setting.list()[A, "x"].value = Color.black
    >>> a.x
    Color.black
    """

    __slots__ = {
        "__default" : "The default value of this Setting",
        "__current" : "The current value set for this Setting",
    }

    __per_class : dict[tuple[type, str], "Setting"] = {}

    @classmethod
    def __class_getitem__(cls, key : type) -> type["Setting"]:
        if not isinstance(key, type):
            raise TypeError(f"Expected type, got '{type(key).__name__}'")
        from Viper.meta.decorators import staticproperty
        return type(cls)(f"Setting[{key.__name__}]", (Setting, ), {"cls" : staticproperty(lambda : key)})

    def __new__(cls, default : T) -> Self:
        if not issubclass(cls, Setting):
            raise TypeError("Cannot use Setting.__new__ on something that is not a subclass of Setting")
        res : Setting = super().__new__(cls)
        try:
            res.cls
        except NotImplementedError:
            raise ValueError("Cannot instanciate unspecialized Setting class") from None
        return res

    def __init__(self, default : T) -> None:
        self.__default = default
        self.__current = default
        if not isinstance(default, self.cls):
            raise TypeError(f"Expected {self.cls.__name__}, got '{type(default).__name__}'")

    @staticproperty
    @abstractmethod
    def cls() -> type[T]:
        """
        The type of value expected for this Setting.
        """
        raise NotImplementedError

    @property
    def value(self) -> T:
        """
        The value that this Setting currently points to.
        """
        return self.__current
    
    @value.setter
    def value(self, value : T):
        if not isinstance(value, self.cls):
            raise TypeError(f"Expected {self.cls.__name__}, got '{type(value).__name__}'")
        self.__current = value
    
    @value.deleter
    def value(self):
        self.__current = self.__default

    @classmethod
    def list(cls, namespace : type | None = None) -> dict[tuple[type, str], "Setting[T]"]:
        """
        Lists all the available settings in a dict object.
        Keys are tuples in the form (<class>, <name>) for each Vertex or Edge subclass with the name of the attribute which holds the Setting.
        Values are the Setting objects themselves.
        A filter class can be given to filter only the settings present in this class and its subclasses.
        """
        if namespace is not None and not isinstance(namespace, type):
            raise TypeError(f"Expected type or None, got '{type(namespace).__name__}")
        if namespace:
            if cls is Setting:
                return {(c, n) : s for (c, n), s in Setting.__per_class.items() if issubclass(c, namespace)}
            else:
                return {(c, n) : s for (c, n), s in Setting.__per_class.items() if s.cls is cls.cls and issubclass(c, namespace)}
        else:
            if cls is Setting:
                return {(c, n) : s for (c, n), s in Setting.__per_class.items()}
            else:
                return {(c, n) : s for (c, n), s in Setting.__per_class.items() if s.cls is cls.cls}
    
    def specialize_subclass(self, cls : type) -> Self:
        """
        Copies the setting to a subclass, allowing the subclass to have a different value for this setting.
        Returns the newly created setting.
        """
        if not isinstance(cls, type):
            raise TypeError(f"Expected type, got '{type(cls).__name__}'")
        target_cls = None
        name = None
        for (c, n), s in Setting.__per_class.items():
            if s is self:
                target_cls = c
                name = n
                break
        if target_cls is None or name is None:
            raise ValueError("Cannot specialize anonymous setting (This setting is not in the code of any known class)")
        if not issubclass(cls, target_cls):
            raise ValueError("Expected subclass of the class this setting is registered in.")
        cp = type(self)(self.__default)
        setattr(cls, name, cp)
        cp.__set_name__(cls, name)
        return cp

    def __set_name__(self, owner : type, name : str):
        from ..logger import logger
        logger.debug(f"New '{self.cls.__name__}' setting registered for class '{owner.__name__}' with name '{name}'.")
        Setting.__per_class[(owner, name)] = self

    def __get__(self, instance : Any, owner : type | None = None) -> T:
        return self.__current
    
    def __set__(self, instance : Any, value : T):
        if not isinstance(value, self.cls):
            raise TypeError(f"Expected {self.cls.__name__}, got '{type(value).__name__}'")
        self.__current = value

    def __delete__(self, instance : Any):
        self.__current = self.__default





ColorSetting = Setting[Color]
SizeSetting = Setting[float]
WeightSetting = Setting[float]
SwitchSetting = Setting[bool]
FlagSetting = Setting[bool]





def ajust_for_background_color(background_color : Color, tolerance : float = 0.15):
    """
    This function will change the values of the Color Settings to ajust those that would not be visible for a background of the given color.
    """
    from ..logger import logger

    for (cls, name), color_setting in ColorSetting.list().items():
        if sum((a - b) ** 2 for a, b in zip(color_setting.value, background_color)) ** 0.5 < tolerance:
            logger.info(f"Changing color setting '{cls.__name__}.{name}'.")
            color_setting.value = color_setting.value.negative_to(background_color)






class __CompilationParameters:

    """
    This class holds some compilations parameters that some modules may want to use.
    """

    SkipLevenshteinForDataNodes = FlagSetting(False)
    SkipLevenshteinForDiffNodes = FlagSetting(False)

CompilationParameters = __CompilationParameters()





del abstractmethod, Any, Generic, Self, TypeVar, Color, hybridmethod, staticproperty        # type: ignore