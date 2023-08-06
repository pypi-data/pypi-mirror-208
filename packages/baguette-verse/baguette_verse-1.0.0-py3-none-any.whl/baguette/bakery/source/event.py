"""
The event library. An event can be created by anyone, specifying any kind of data. Anybody can wait for any type of events.
"""

from typing import Callable, Generic, Type, TypeVar
from Viper.better_threading import Future
from threading import Lock
from .utils import chrono

__all__ = ["Event"]





T = TypeVar("T", bound="Event")

class Event(Generic[T]):

    """
    The base event class. Use its static methods to react to Events created.
    """

    __waiting : dict[Type[T], list[Future[T]]] = {}
    __callbacks : dict[Type[T], list[Callable[[T], None]]] = {}
    __locks : dict[Type[T], Lock] = {}

    __slots__ = {}

    def __str__(self) -> str:
        """
        Implements str(self).
        """
        return type(self).__name__ + "(" + ", ".join(str(name) + " = " + repr(getattr(self, name)) for name in self.__slots__) + ")"

    @chrono
    def throw(self : T) -> bool:
        """
        Triggers the Event. Everyone waiting for it will be awaken, and corresponding callbacks will be called.
        Returns True if anybody reacted to the event. Returns False otherwise.
        """
        from ..logger import logger

        def raise_multiple_exceptions(exceptions : list[BaseException]):
            """
            Raises all the exceptions in the given list, in order.
            """
            if not exceptions:
                return
            try:
                raise exceptions.pop() from None
            finally:
                raise_multiple_exceptions(exceptions)

        classes = {type(self)}
        done = set()
        ok = False
        logger.debug("Throwing {}.".format(self))
        while classes:
            cls = classes.pop()

            with Event.__locks[cls]:

                for fut in Event.__waiting[cls]:
                    fut.set(self)
                    ok = True
                Event.__waiting[cls].clear()
                
                exceptions : list[BaseException] = []
                for cb in Event.__callbacks[cls]:
                    try:
                        cb(self)
                        ok = True
                    except BaseException as e:
                        exceptions.append(e)
                raise_multiple_exceptions(exceptions)

            done.add(cls)
            classes.update(cls.__subclasses__())
            classes.difference_update(done)
        
        return ok

    @classmethod
    def __init_subclass__(cls : Type[T]) -> None:
        from threading import Lock
        Event.__locks[cls] = Lock()
        Event.__callbacks[cls] = []
        Event.__waiting[cls] = []

    @classmethod
    def wait(cls : Type[T]) -> T:
        """
        Waits for an Event of this class or of any subclasses to occur. Returns the Event object when it happens.
        """
        from Viper.better_threading import Future
        fut : Future[T] = Future()
        with Event.__locks[cls]:
            Event.__waiting[cls].append(fut)
        return fut.result()
    
    @classmethod
    def add_callback(cls : Type[T], callback : Callable[[T], None]):
        """
        Adds a callback to be performed after a realization of an event of this class or of any of its subclasses. The callback will persist until it is removed.
        """
        with Event.__locks[cls]:
            Event.__callbacks[cls].append(callback)
    
    @classmethod
    def remove_callback(cls : Type[T], callback : Callable[[T], None]) -> bool:
        """
        Removes a callback to be performed after a realization of an event with the given name. Returns True if a callback was indeed deleted.
        """
        with Event.__locks[cls]:
            try:
                Event.__callbacks[cls].remove(callback)
                return True
            except ValueError:
                return False





Event.__init_subclass__()       # It must initialize itself, as if it was one of its own subclasses.

del Callable, Type, Future, Lock