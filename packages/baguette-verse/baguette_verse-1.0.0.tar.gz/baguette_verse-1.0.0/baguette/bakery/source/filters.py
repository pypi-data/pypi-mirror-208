"""
This module defines basic graph filters. Use them to reduce the size of the graph by only keeping specific edges.
To be used with compile.py, all custom Filters must be defined in this file!
"""

from typing import Callable, Iterable
from .graph import Edge, Vertex, Graph
from Viper.meta.iterable import InstanceReferencingClass
from .utils import chrono, System
from .types.registry import Key, KeyEntry, Handle
from functools import cache

__all__ = ["Filter", "significant_call_only", "no_data_nodes", "no_simple_imports", "no_handle_nodes", "injected_threads_only", "significant_processes_only", "modified_registry_only"]





class Filter(metaclass = InstanceReferencingClass):

    """
    A filter object for graphs.
    """

    def __init__(self, edge_filter_function : Callable[[Edge], bool], vertex_filter_function : Callable[[Vertex], bool]) -> None:
        self.__edge_filter = edge_filter_function
        self.__vertex_filter = vertex_filter_function
    
    def test_vertex(self, u : Vertex) -> bool:
        """
        Tests if a given vertex should be kept in the graph.
        """
        from .graph import Vertex
        if not isinstance(u, Vertex):
            raise TypeError("Expected Vertex, got " + repr(type(u).__name__))
        return self.__vertex_filter(u)
    
    def test_edge(self, e : Edge) -> bool:
        """
        Tests if a given edge should be kept in the graph.
        """
        from .graph import Edge
        if not isinstance(e, Edge):
            raise TypeError("Expected Edge, got " + repr(type(e).__name__))
        return self.__edge_filter(e)
    
    def __call__(self, iterable : Iterable[Edge | Vertex]) -> Iterable[Edge | Vertex]:
        """
        Implements self(iterable). Filters the given Egde | Vertex iterable.
        """
        from .graph import Edge, Vertex
        from typing import Iterable
        if not isinstance(iterable, Iterable):
            raise TypeError("Expected iterable, got " + repr(type(iterable).__name__))
        for x in iterable:
            if isinstance(x, Edge):
                if self.test_edge(x):
                    yield x
            elif isinstance(x, Vertex):
                if self.test_vertex(x):
                    yield x
            else:
                raise TypeError("Expected iterable of Edges or Vertices, got a " + repr(type(x).__name__))
    
    @chrono
    def apply(self, g : Graph):
        """
        Applies the filter to the given graph, modifying it.
        """
        from .graph import Graph
        if not isinstance(g, Graph):
            raise TypeError("Expected Graph, got " + repr(type(g).__name__))
        edges_to_remove = {e for e in g.edges if not self.__edge_filter(e)}
        vertices_to_remove = {u for u in g.vertices if not self.__vertex_filter(u)}
        for e in edges_to_remove:
            g.remove(e)
        for u in vertices_to_remove:
            g.remove(u)





# Here we will define some basic filters:

def important_call_filter(u : Vertex) -> bool:
    from .types.execution import Call
    if not isinstance(u, Call):
        return True
    else:
        for v in u.neighbors():
            if not isinstance(v, Call):
                return True
        return False

def data_filter(u : Vertex) -> bool:
    from .types.data import Data
    return not isinstance(u, Data)

def simple_imports(u : Vertex) -> bool:
    from .types.imports import Import
    from .types.execution import Process
    return not isinstance(u, Import) or bool([v for v in u.neighbors() if not isinstance(v, Process)])

def no_handles(u : Vertex) -> bool:
    from .types.filesystem import Handle as Handle
    from .types.network import Socket
    from .types.execution import Process
    if not isinstance(u, Handle | Socket):
        return True
    if isinstance(u, Socket):
        return False
    if u.file:
        for v in u.file.neighbors():
            if isinstance(v, Process):
                return True
    return False

def single_threads(u : Vertex) -> bool:
    from .types.execution import Thread, Process
    return not isinstance(u, Thread) or len([v for v in u.neighbors() if isinstance(v, Process)]) > 1

@cache
def single_processes(u : Vertex) -> bool:
    from .types.execution import Process
    from .types.network import Host

    if not isinstance(u, Process):
        return True

    def test_process_vertex(u : Process) -> bool:
        return bool([v for v in u.neighbors() if not isinstance(v, (Process, Host))]) or u.parent_process == None
        
    return test_process_vertex(u) or any(single_processes(v) for v in u.children_processes)
    


Key_KeyEntry_Model : System[Key | KeyEntry | Handle] = System()
_strong_keys : set[Key] = set()

@cache
def changed_registry(u : Vertex) -> bool:           # This filter is so fucking complicated!!!
    from .types.registry import Key, KeyEntry, Handle, ChangesTowards, SetsEntry, DeletesEntry, HasSubKey
    from .config import ColorSetting

    if not isinstance(u, Key | KeyEntry | Handle):
        return True
    
    if isinstance(u, Handle):
        with Key_KeyEntry_Model.Entangled(u):
            return any(changed_registry(v) for v in u.neighbors() if isinstance(v, KeyEntry) if v not in Key_KeyEntry_Model) or any(changed_registry(v) for v in u.neighbors() if isinstance(v, Key) and v not in Key_KeyEntry_Model)
    
    if isinstance(u, KeyEntry):
        with Key_KeyEntry_Model.Entangled(u):              # Checking this Entry: do not do it twice!

            if u.key in _strong_keys:               # We are actually propagating the collapse of the wave function!
                return True
            
            if u.color == u.deleted_key_entry_color:        # This is an important Entry : it collapses the wave function!
                _strong_keys.add(u.key)
                Key_KeyEntry_Model.add_callback(_strong_keys.remove, u.key)
                return True

            for e in u.edges:
                if isinstance(e, SetsEntry | DeletesEntry):     # This is an important Entry : it collapses the wave function!
                    _strong_keys.add(u.key)
                    Key_KeyEntry_Model.add_callback(_strong_keys.remove, u.key)
                    return True
            
            for e in u.edges:                   # We got another particle that will probably collapse the wave function nearby : entangle with it!
                if isinstance(e, ChangesTowards) and e.source is u and e.destination not in Key_KeyEntry_Model:
                    return changed_registry(e.destination)
                
            if u.key not in Key_KeyEntry_Model:     # The Key has not been tested yet. Pass on to it!
                return changed_registry(u.key)

            if Key_KeyEntry_Model.population:   # No clue: pass on to someone else...
                return changed_registry(Key_KeyEntry_Model.population.pop())
            else:       # No clue and there is no one else: it means we are on a weak Key and we can start the collapse.
                return False
    
    if isinstance(u, Key):
    
        with Key_KeyEntry_Model.Entangled(u):
            Key_KeyEntry_Model.population = u.entries       # Set the populations of entries to entangle with.

            if u.color == u.deleted_key_color:        # This is an important Key : it collapses the wave function!
                _strong_keys.add(u)
                Key_KeyEntry_Model.add_callback(_strong_keys.remove, u)

            if Key_KeyEntry_Model.population and all(changed_registry(v) for v in Key_KeyEntry_Model.include()):       # If it is a strong key, positive collapse will start in one of the entries and propagate to all others.
                return True
            
            if u in _strong_keys:       # It was a strong Key due to its own color.
                return True
            
            for h in u.neighbors():         # A handle that might have worked on important values might be working on this key because of a symbolic link.
                if isinstance(h, Handle) and h not in Key_KeyEntry_Model and changed_registry(h) and h.key is u:
                    return True
        
        if any(changed_registry(e.destination) for e in u.edges if isinstance(e, HasSubKey) and e.source is u and e.destination not in Key_KeyEntry_Model):     # If not a strong key, at least it has strong heirs?
            return True
        
        return False


significant_call_only = Filter(lambda e : True, important_call_filter)
no_data_nodes = Filter(lambda e : True, data_filter)
no_simple_imports = Filter(lambda e : True, simple_imports)
no_handle_nodes = Filter(lambda e : True, no_handles)
injected_threads_only = Filter(lambda e : True, single_threads)
significant_processes_only = Filter(lambda e : True, single_processes)
modified_registry_only = Filter(lambda e : True, changed_registry)

del important_call_filter, data_filter, simple_imports, no_handles, single_threads, Callable, Iterable, Edge, Vertex, Graph, InstanceReferencingClass, Key, KeyEntry