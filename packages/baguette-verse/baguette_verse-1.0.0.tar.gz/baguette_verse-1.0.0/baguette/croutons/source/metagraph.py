"""
This module defines MetaGraphs, MetaVertices, MetaEdges and MetaArrows.
"""

from typing import Any, Callable, Iterable, Iterator, Optional, Self
from ...bakery.source.graph import Arrow, Edge, Graph, UniqueVertex, Vertex
from ...bakery.source.colors import Color
from ...bakery.source.types.execution import *
from ...bakery.source.types.network import *
from ...bakery.source.types.filesystem import *





class MetaVertex(UniqueVertex):

    """
    This class describes a type vertex. One or multiple Vertex subclasses can be associated to it.
    """

    @classmethod
    def __class_getitem__(cls, cls_init):
        try:
            Mv = cls()
            Mv.cls = cls_init
            return Mv
        except BaseException as E:
            raise E from None

    __slots__ = {
        "__class" : "The class that this MetaVertex represents.",
        "__condition" : "An additional condition function. Takes a Vertex as an input and tells whether or not it can be a valid match (does not need to check type)",
        "__color" : "The Color forcefully set to this MetaVertex."
    }

    __pickle_slots__ = {
        "cls",
        "condition"
    }

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        from ...bakery.source.colors import Color
        super().__init__(parent=parent)
        self.__class : tuple[type[Vertex], ...] = (Vertex, )
        self.__condition : Callable[[Vertex], bool] | bool = True
        self.__color : Color | None = None
        self.edges : set[MetaEdge]

    @property
    def color(self) -> Color:
        """
        The color of this MetaVertex. Defaults to the average of the colors of all its Vertex classes.
        """
        from ...bakery.source.colors import Color
        if self.__color is not None:
            return self.__color
        return Color.average(*[(cls.default_color) for cls in self.cls])
    
    @color.setter
    def color(self, c : Color):
        from ...bakery.source.colors import Color
        if not isinstance(c, Color):
            raise TypeError("Expected Color, got " + repr(type(c).__name__))
        self.__color = c

    @color.deleter
    def color(self):
        self.__color = None
    
    @property
    def cls(self) -> tuple[type[Vertex], ...]:
        """
        The classes that this vertex represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Vertex] | tuple[type[Vertex], ...]):
        """
        Sets the class(es) associated with this vertex.
        """
        from ...bakery.source.graph import Vertex
        if isinstance(cls, type) and issubclass(cls, Vertex):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Vertex):
                    raise TypeError("Expected subclass of Vertex or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Vertex or tuple of subclasses, got " + repr(cls))
    
    @cls.deleter
    def cls(self):
        from ...bakery.source.graph import Vertex
        self.__class = (Vertex, )

    @property
    def condition(self) -> Callable[[Vertex], bool] | bool:
        """
        An additional condition to check when trying to match a Vertex to this MetaVertex.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Callable[[Vertex], bool] | bool):
        """
        Sets the additional condition function for this MetaVertex.
        """
        if not callable(cond) and not isinstance(cond, bool):
            raise TypeError("Expected callable or bool, got " + repr(type(cond).__name__))
        self.__condition = cond

    @condition.deleter
    def condition(self):
        self.__condition = True
    
    def match(self, v : Vertex) -> bool:
        """
        Returns True if the Vertex v has a matching type.
        """
        return isinstance(v, self.__class) and (self.__condition(v) if callable(self.__condition) else self.__condition)
    
    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaVertex.
        """
        return " | ".join(c.__name__ for c in self.__class)

    @property
    def label(self) -> str:
        return "Vertex[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")

    def __str__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("*" if callable(self.__condition) else "")
    
    def __repr__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")
    




class MetaEdge(Edge):

    """
    This class describes a type edge. One or multiple Edge subclasses can be associated to it.
    Note that a MetaEdge can represent a subclass of Arrow and in this case, the match can be made in both directions.
    """

    __slots__ = {
        "__class" : "The class that this MetaEdge represents.",
        "__condition" : "An additional condition function. Takes an Edge as an input and tells whether or not it can be a valid match (does not need to check type)",
        "__color" : "The Color forcefully set to this MetaEdge."
    }

    __pickle_slots__ = {
        "cls",
        "condition"
    }

    def __init__(self, source: MetaVertex, destination: MetaVertex, *, auto_write: bool = True) -> None:
        from ...bakery.source.colors import Color
        if not isinstance(source, MetaVertex) or not isinstance(destination, MetaVertex):
            raise TypeError("Expected two MetaVertices, got " + repr(type(source).__name__) + " and " + repr(type(destination).__name__))
        super().__init__(source, destination, auto_write=auto_write)
        self.__class : tuple[type[Edge], ...] = (Edge, )
        self.__condition : Callable[[Edge], bool] | bool = True
        self.__color : Color | None = None
        self.source : MetaVertex
        self.destination : MetaVertex

    @property
    def color(self) -> Color:
        """
        The color of this MetaEdge. Defaults to the average of the colors of all its Edge classes.
        """
        from ...bakery.source.colors import Color
        if self.__color != None:
            return self.__color
        edge_colors = [cls.default_color for cls in self.cls if not cls.blend_vertices_colors]
        if edge_colors:
            return Color.average(*edge_colors)
        else:
            return Color.average(self.source.color, self.destination.color)
    
    @color.setter
    def color(self, c : Color):
        from ...bakery.source.colors import Color
        if not isinstance(c, Color):
            raise TypeError("Expected Color, got " + repr(type(c).__name__))
        self.__color = c

    @color.deleter
    def color(self):
        self.__color = None
    
    @property
    def cls(self) -> tuple[type[Edge], ...]:
        """
        The classes that this edge represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Edge] | tuple[type[Edge], ...]):
        """
        Sets the class(es) associated with this edge.
        """
        from ...bakery.source.graph import Edge
        if isinstance(cls, type) and issubclass(cls, Edge):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Edge):
                    raise TypeError("Expected subclasses of Edge or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Edge or tuple of subclasses, got " + repr(cls))
        
    @cls.deleter
    def cls(self):
        from ...bakery.source.graph import Edge
        self.__class = (Edge, )
        
    @property
    def condition(self) -> Callable[[Edge], bool] | bool:
        """
        An additional condition to check when trying to match an Edge to this MetaEdge.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Callable[[Edge], bool] | bool):
        """
        Sets the additional condition function for this MetaEdge.
        """
        if not callable(cond) and not isinstance(cond, bool):
            raise TypeError("Expected callable or bool, got " + repr(type(cond).__name__))
        self.__condition = cond
    
    @condition.deleter
    def condition(self):
        self.__condition = True
    
    def match(self, e : Edge) -> bool:
        """
        Returns True if the Egde e has a matching type.
        """
        return isinstance(e, self.__class) and (self.__condition(e) if callable(self.__condition) else self.__condition)
    
    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaEdge.
        """
        return " | ".join(c.__name__ for c in self.cls)

    @property
    def label(self) -> str:
        return "Edge[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")

    def __str__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("*" if callable(self.__condition) else "")
    
    def __repr__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")

    def __getitem__(self, cls : type[Edge] | tuple[type[Edge], ...]) -> Self:
        try:
            self.cls = cls
            return self
        except BaseException as E:
            raise E from None




class MetaArrow(Arrow, MetaEdge):

    """
    This class describes a type arrow. One or multiple Arrow subclasses can be associated to it.
    """

    __slots__ = {
        "__class" : "The class that this MetaArrow represents.",
        "__condition" : "An additional condition function. Takes an Arrow as an input and tells whether or not it can be a valid match (does not need to check type)"
    }

    __pickle_slots__ = {
        "cls",
        "condition"
    }

    def __init__(self, source: MetaVertex, destination: MetaVertex, *, auto_write: bool = True) -> None:
        from ...bakery.source.graph import Arrow
        super().__init__(source, destination, auto_write=auto_write)
        self.__class : tuple[type[Arrow], ...] = (Arrow, )
        self.__condition : Callable[[Arrow], bool] | bool = True

    @property
    def cls(self) -> tuple[type[Arrow], ...]:
        """
        The classes that this arrow represents.
        """
        return self.__class
    
    @cls.setter
    def cls(self, cls : type[Arrow] | tuple[type[Arrow], ...]):
        """
        Sets the class(es) associated with this arrow.
        """
        from ...bakery.source.graph import Arrow
        if isinstance(cls, type) and issubclass(cls, Arrow):
            self.__class = (cls, )
        elif isinstance(cls, tuple):
            for c in cls:
                if not isinstance(c, type) or not issubclass(c, Arrow):
                    raise TypeError("Expected subclasses of Arrow or tuple of subclasses, got a " + repr(c))
            self.__class = cls
        else:
            raise TypeError("Expected subclass of Arrow or tuple of subclasses, got " + repr(cls))
        
    @cls.deleter
    def cls(self):
        from ...bakery.source.graph import Arrow
        self.__class = (Arrow, )
        
    @property
    def condition(self) -> Callable[[Arrow], bool] | bool:
        """
        An additional condition to check when trying to match an Edge to this MetaEdge.
        """
        return self.__condition
    
    @condition.setter
    def condition(self, cond : Callable[[Arrow], bool] | bool):
        """
        Sets the additional condition function for this MetaEdge.
        """
        if not callable(cond) and not isinstance(cond, bool):
            raise TypeError("Expected callable or bool, got " + repr(type(cond).__name__))
        self.__condition = cond
    
    @condition.deleter
    def condition(self):
        self.__condition = True
    
    def match(self, a : Arrow) -> bool:
        """
        Returns True if the Arrow a has a matching type.
        """
        return isinstance(a, self.__class) and (self.__condition(a) if callable(self.__condition) else self.__condition)

    def __get_cls_str(self) -> str:
        """
        Returns a string to display the class of a MetaArrow.
        """
        return " | ".join(c.__name__ for c in self.cls)

    @property
    def label(self) -> str:
        return "Arrow[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")
    
    def __str__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("*" if callable(self.__condition) else "")
    
    def __repr__(self) -> str:
        return type(self).__name__ + "[" + self.__get_cls_str() + "]" + ("{" + str(self.__condition) + "}" if callable(self.__condition) else "")
    
    def __getitem__(self, cls : type[Arrow] | tuple[type[Arrow], ...]) -> Self:
        return super().__getitem__(cls)
    




class MetaGraph(Graph):

    """
    This particular type of graph can only contain MetaVertices, MetaEdges or MetaArrows. It can be used for normal graph exploration.
    """

    __slots__ = {
        "__named_objects" : "A dict holding named vertices and edges."
    }

    vertices : set[MetaVertex]
    edges : set[MetaEdge | MetaArrow]

    def __init__(self, g : Graph = Graph()) -> None:
        if not isinstance(g, Graph):
            raise TypeError("Exepcted Graph, got " + repr(type(g).__name__))
        super().__init__()
        self.__named_objects : dict[str, MetaEdge | MetaVertex] = {}
        vertex_translation_table : dict[Vertex, MetaVertex] = {}
        edge_translation_table : dict[Edge, MetaEdge] = {}
        for v, e, u in g.pairs():
            if v in vertex_translation_table:
                Mv = vertex_translation_table[v]
            else:
                Mv = MetaVertex()
                Mv.cls = type(v)
                vertex_translation_table[v] = Mv
                self.append(Mv)
            if u in vertex_translation_table:
                Mu = vertex_translation_table[u]
            else:
                Mu = MetaVertex()
                Mu.cls = type(u)
                vertex_translation_table[u] = Mu
                self.append(Mu)
            if e in edge_translation_table:
                Me = edge_translation_table[e]
            else:
                Me = MetaEdge(Mv, Mu)
                Me.cls = type(e)
                edge_translation_table[e] = Me
                self.append(Me)
    
    @property
    def names(self) -> list[str]:
        """
        Returns the list of names for named Meta{Vertices, Edges, Arrows} available in this MetaGraph.
        """
        return list(self.__named_objects)

    def add_vertex(self, v: MetaVertex, explore: bool = True) -> None:
        if not isinstance(v, MetaVertex):
            raise TypeError("Expected MetaVertex, got " + repr(type(v).__name__))
        return super().add_vertex(v, explore)

    def pairs(self) -> Iterator[tuple[MetaVertex, MetaEdge, MetaVertex]]:
        for u, e, v in super().pairs():
            if not isinstance(u, MetaVertex) or not isinstance(e, MetaEdge) or not isinstance(v, MetaVertex):
                raise TypeError("Got a normal Vertex/Edge in a MetaGraph")
            yield u, e, v
    
    def append(self, value: MetaVertex | MetaEdge, explore: bool = False):
        if not isinstance(value, MetaVertex | MetaEdge | MetaArrow):
            raise TypeError("Expected MetaVertex, MetaEdge or MetaArrow, got " + repr(type(value).__name__))
        return super().append(value, explore)
    
    def extend(self, values: Iterable[MetaVertex | MetaEdge], explore: bool = False):
        from typing import Iterable
        if not isinstance(explore, bool):
            raise TypeError("Expected bool for explore, got " + repr(explore.__class__.__name__))
        if not isinstance(values, Iterable):
            raise TypeError("Expected iterable, got " + repr(values.__class__.__name__))
        def __checked():
            for v in values:
                if not isinstance(v, MetaVertex | MetaEdge | MetaArrow):
                    raise TypeError("Expected iterable of MetaVertex, MetaEdge or MetaArrow, got " + repr(type(v).__name__))
                yield v
        return super().extend(__checked(), explore)

    def __dir__(self) -> list[str]:
        return list(super().__dir__()) + self.names
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name not in self.__named_objects:
                raise e from None
            return self.__named_objects[name]
    
    def __getstate__(self) -> dict[str, Any]:
        d = super().__getstate__()
        d["__named_objects"] = self.__named_objects
        return d
    
    def __setstate__(self, state: dict[str, Any]):
        names = state.pop("__named_objects")
        self.__named_objects = names
        return super().__setstate__(state)
    
    def __setattr__(self, name: str, value: Any) -> None:
        try:
            super().__getattribute__(name)
        except AttributeError:
            if isinstance(value, MetaEdge | MetaVertex):
                self.__named_objects[name] = value
                self.append(value)
            else:
                return super().__setattr__(name, value)
    
    def __delattr__(self, name: str) -> None:
        if name in self.__named_objects:
            v = self.__named_objects.pop(name)
            if v not in self.__named_objects.values():
                self.remove(v)
        else:
            return super().__delattr__(name)
    
    def remove(self, value : MetaVertex | MetaEdge):
        for name, v in self.__named_objects.copy().items():
            if v == value:
                self.__named_objects.pop(name)
        super().remove(value)
    
    def __neighborhood_mapper(self, g : Graph) -> dict[Vertex, set[MetaVertex]]:
        """
        Searches the given graph for matches of the metagraph.
        """

        mapping : dict[Vertex, set[MetaVertex]] = {}

        for v in g.vertices:
            for Mv in self.vertices:
                if Mv.match(v):
                    if v not in mapping:
                        mapping[v] = set()
                    mapping[v].add(Mv)
        
        return mapping
    
    def __clear_mapper_deadends(self, mapping : dict[Vertex, set[MetaVertex]]):
        """
        Clears the deadends in a mapping returned by self.__neighborhood_mapper():
        (Operates on the mapping itself)
        """

        work = mapping.copy()

        while work:

            v, sMv = work.popitem()

            to_check_again : set[tuple[Vertex, MetaVertex]] = set()

            for Mv in sMv.copy():

                ok = False
                edge_possibilities : dict[MetaEdge, set[Edge]] = {}     # For all MetaNeighbors. If any of them has an empty 

                for Me in Mv.edges:

                    edge_possibilities[Me] = set()

                    for e in v.edges:

                        if Me.match(e) and (not isinstance(Me, MetaArrow) or (e.source is v) == (Me.source is Mv)):     # MetaEdge or well-oriented MetaArrow
                            edge_possibilities[Me].add(e)
                                    
                all_ok = True
                decisive_neighbors : set[tuple[Vertex, MetaVertex]] = set()

                for Me in edge_possibilities:

                    ok = False

                    for e in edge_possibilities[Me]:

                        u = e.source if e.source is not v else e.destination
                        Mu = Me.source if Me.source is not Mv else Me.destination
                        decisive_neighbors.add((u, Mu))
                        
                        if u in mapping and Mu in mapping[u]:
                            ok = True
                
                    if not ok:
                        all_ok = False
                
                if not all_ok:
                    mapping[v].discard(Mv)
                    to_check_again.update(decisive_neighbors)
            
            new_work : dict[Vertex, set[MetaVertex]] = {}

            for v, Mv in to_check_again:
                sMv = work.pop(v, set())
                if v not in new_work:
                    new_work[v] = sMv
                new_work[v].add(Mv)

            work.update({v : sMv.intersection(mapping[v] if v in mapping else set()) for v, sMv in new_work.items()})
                    
        # for v, sMv in list(mapping.items()):
        #     if not sMv:
        #         mapping.pop(v)
            
    def __expand_subgraph(self, g : Graph, mapping : dict[Vertex, set[MetaVertex]], sub : dict[MetaVertex | MetaEdge, Vertex | Edge], Mv : MetaVertex) -> Iterator[dict[MetaVertex | MetaEdge, Vertex | Edge]]:
        """
        Yields all the next steps of the subgraph sub of Graph g in construction by adding all possible vertices that can fit the role of Mv.
        """
        from itertools import product

        existing : dict[Vertex, MetaVertex] = {sub[Mu] : Mu for Mu in Mv.neighbors() if Mu in sub}      # The neighbors of Mv that have already been chosen

        if not existing:        # We are starting from zero or we reached a new component
            
            used_Mvs = set(v for v in sub.values() if v in mapping and Mv in mapping[v])        # The candidates for Mv that are already part of the subgraph

            for v in mapping:
                if Mv in mapping[v] and v not in used_Mvs:
                    subv = sub.copy()
                    subv[Mv] = v
                    yield subv
            
            return

        existing_iter = iter(existing)

        u = next(existing_iter)

        vertex_possibilities : set[Vertex] = {v for v in u.neighbors() if v in mapping and Mv in mapping[v]}

        for u in existing_iter:
            vertex_possibilities.intersection_update({v for v in u.neighbors() if v in mapping and Mv in mapping[v]})
        
        vertex_possibilities.difference_update(sub.values())

        for v in vertex_possibilities:
            edge_possibilities : dict[MetaEdge, set[Edge]] = {}

            for u, Mu in existing.items():

                edges = u.edges & v.edges
                Medges = Mu.edges & Mv.edges
                for Me in Medges:
                    edge_possibilities[Me] = set()
                    for e in edges:
                        if Me.match(e) and (not isinstance(Me, MetaArrow) or (e.source is v) == (Me.source is Mv)):
                            edge_possibilities[Me].add(e)
            
            Me_list = list(edge_possibilities)
            for e_list in product(*[edge_possibilities[Me] for Me in Me_list]):
                if len(set(e_list)) == len(e_list):     # No edge was used as two different MetaEdges between v and one of its neighbors
                    subv = sub.copy()
                    subv[Mv] = v
                    for Me, e in zip(Me_list, e_list):
                        subv[Me] = e
                    yield subv

    def __discover(self) -> Iterator[MetaVertex]:
        """
        Yields successive MetaVertices by exploring the MetaGraph. The next MetaVertex yielded is either a neighbor of one of the previously yielded ones or is the first of a new connected component.
        """
        
        to_do : set[MetaVertex] = self.vertices.copy()
        done : set[MetaVertex] = set()
        component_explorable : set[MetaVertex] = set()

        while to_do:
            if not component_explorable:
                Mu = to_do.pop()
                component_explorable.add(Mu)

            else:
                component_done = True
                for Mv in component_explorable.copy():
                    sMu = set(Mv.neighbors()) - done
                    if sMu:
                        component_done = False
                        Mu = sMu.pop()
                        to_do.discard(Mu)
                        break
                    else:
                        component_explorable.remove(Mv)

                if component_done:
                    continue
                    
            component_explorable.add(Mu)
            yield Mu
            done.add(Mu)
         
    def search_iter(self, g : Graph) -> Iterator[Graph]:
        """
        Searches through g for all occurences of a subgraph that matches the metagraph.
        """
        from ...bakery.source.graph import Graph
        from typing import Iterator

        # subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = [{}]
        # next_subgraphs : list[dict[MetaVertex | MetaEdge, Vertex | Edge]] = []

        mapping = self.__neighborhood_mapper(g)

        self.__clear_mapper_deadends(mapping)

        order = list(self.__discover())

        # print("Got {} vertices with openings.".format(len([v for v, sMv in mapping.items() if sMv])))

        def build_iter(g : Graph, mapping : dict[Vertex, set[MetaVertex]], sub : dict[MetaVertex | MetaEdge, Vertex | Edge], i : int) -> Iterator[Graph]:
            if i == len(order) - 1:     # Last MetaVertex to append
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    gi = Graph()
                    gi.extend(subi.values())
                    yield gi
            else:
                for subi in self.__expand_subgraph(g, mapping, sub, order[i]):
                    yield from build_iter(g, mapping, subi, i + 1)
        
        yield from build_iter(g, mapping, {}, 0)

        # for i, Mv in enumerate(self.__discover()):
        #     for sub in subgraphs:
        #         next_subgraphs.extend(self.__expand_subgraph(g, mapping, sub, Mv))
        #     subgraphs = next_subgraphs
        #     next_subgraphs = []
        
        # for dg in subgraphs:
        #     g = Graph()
        #     g.extend(dg.values())
        #     yield g





# N = 0

# class Square(UniqueVertex):
#     def __init__(self, *, c: Color = Color.blue, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class Triangle(UniqueVertex):
#     def __init__(self, *, c: Color = Color.red, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class Circle(UniqueVertex):
#     def __init__(self, *, c: Color = Color.green, parent: Optional["Vertex"] = None) -> None:
#         global N
#         super().__init__(c=c, parent=parent)
#         self.label = type(self).__name__[0]+str(N)
#         N += 1

# class TriangleToTriangle(Arrow):
#     pass

# class TriangleToCircle(Arrow):
#     pass

# class CircleToSquare(Arrow):
#     pass

# class SquareToTriangle(Arrow):
#     pass



# print("Building and exporting MetaGraph.")
# MG = MetaGraph()

# T0 = MetaVertex[Triangle]
# T1 = MetaVertex[Triangle]
# C2 = MetaVertex[Circle]
# S3 = MetaVertex[Square]
# T4 = MetaVertex[Triangle]

# print(repr(T0), repr(T1), repr(C2), repr(S3), repr(T4))

# MetaArrow(T0, T1).cls = TriangleToTriangle
# MetaArrow(T1, C2).cls = TriangleToCircle
# MetaArrow(C2, S3).cls = CircleToSquare
# MetaArrow(S3, T4).cls = SquareToTriangle
# MetaArrow(T4, T1).cls = TriangleToTriangle
# MetaArrow(T1, T4).cls = TriangleToTriangle

# MG.append(T0, explore=True)

# MG.export("meta.gexf")

# print("Building Graph.")
# g = Graph()

# C0 = Circle()
# T1 = Triangle()
# S2 = Square()
# T3 = Triangle()
# T4 = Triangle()
# T5 = Triangle()
# S6 = Square()
# T7 = Triangle()
# T8 = Triangle()
# C9 = Circle()
# C10 = Circle()
# C11 = Circle()
# S12 = Square()
# T13 = Triangle()
# S14 = Square()
# C15 = Circle()
# C16 = Circle()
# S17 = Square()
# T18 = Triangle()
# T19 = Triangle()
# T20 = Triangle()
# T21 = Triangle()

# TriangleToCircle(T3, C0)
# CircleToSquare(C0, S2)
# TriangleToTriangle(T1, T3)
# TriangleToTriangle(T4, T1)
# SquareToTriangle(S2, T3)
# TriangleToTriangle(T5, T3)
# SquareToTriangle(S6, T4)
# TriangleToTriangle(T3, T8)
# TriangleToTriangle(T8, T3)
# TriangleToCircle(T3, C9)
# TriangleToCircle(T8, C9)
# TriangleToCircle(T5, C11)
# CircleToSquare(C11, S6)
# CircleToSquare(C11, S17)
# CircleToSquare(C9, S12)
# SquareToTriangle(S12, T8)
# CircleToSquare(C15, S12)
# CircleToSquare(C15, S17)
# TriangleToCircle(T7, C10)
# TriangleToTriangle(T7, T13)
# TriangleToTriangle(T13, T7)
# CircleToSquare(C10, S14)
# SquareToTriangle(S14, T13)
# CircleToSquare(C16, S12)
# CircleToSquare(C16, S14)
# SquareToTriangle(S17, T18)
# TriangleToCircle(T19, C15)
# TriangleToCircle(T20, C16)
# TriangleToCircle(T21, C16)
# SquareToTriangle(S14, T20)
# SquareToTriangle(S14, T21)
# TriangleToTriangle(T18, T19)
# TriangleToTriangle(T19, T18)
# TriangleToTriangle(T19, T20)
# TriangleToTriangle(T20, T21)
# TriangleToTriangle(T21, T20)
# TriangleToTriangle(T19, T21)

# g.append(T5, explore=True)

# print("Matching...")

# for i, subi in enumerate(MG.search_iter(g)):
#     if i == 3:
#         for v in subi.vertices:
#             v.color = color.white
#         for e in subi.edges:
#             e.color = color.white

# print("Exporting Graph.")
# g.export("graph.gexf")