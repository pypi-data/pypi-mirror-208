"""
This module contains integration protocols for this behavioral package.
"""

from ....logger import logger
from ...build import BuildingPhase
from ...utils import chrono
from ..filesystem.entities import File, Handle
from ..network.entities import Connection, Socket
from . import entities, relations

__all__ = ["register_read_operation", "register_write_operation"]





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def register_read_operation(target : File | Connection, vector : Handle | Socket, content : bytes | bytearray | memoryview | str, offset : int | None = None):
    """
    Registers a read operation to be added to the corresponding DiffNodes.
    """
    from .entities import Diff
    from .relations import IsDiffOf
    from .utils import Read
    if isinstance(content, str):
        content = content.encode("utf-8")
    if target not in Diff._active_target_diff:
        t = Diff()
        IsDiffOf(t, target)
        Diff._active_target_diff[target] = t
    else:
        t = Diff._active_target_diff[target]
    if vector not in Diff._active_vector_diff:
        v = Diff()
        IsDiffOf(v, vector)
        Diff._active_vector_diff[vector] = v
    else:
        v = Diff._active_vector_diff[vector]
    
    if offset == None:
        t.add_operation(Read(t.last_pos(), content))
        v.add_operation(Read(v.last_pos(), content))
    else:
        t.add_operation(Read(offset, content))
        v.add_operation(Read(offset, content))

@chrono
def register_write_operation(target : File | Connection, vector : Handle | Socket, content : bytes | bytearray | memoryview | str, offset : int | None = None):
    """
    Registers a write operation to be added to the corresponding DiffNodes.
    """
    from .entities import Diff
    from .relations import IsDiffOf
    from .utils import Write
    if isinstance(content, str):
        content = content.encode("utf-8")
    if target not in Diff._active_target_diff:
        t = Diff()
        IsDiffOf(t, target)
        Diff._active_target_diff[target] = t
    else:
        t = Diff._active_target_diff[target]
    if vector not in Diff._active_vector_diff:
        v = Diff()
        IsDiffOf(v, vector)
        Diff._active_vector_diff[vector] = v
    else:
        v = Diff._active_vector_diff[vector]
    
    if offset == None:
        t.add_operation(Write(t.last_pos(), content))
        v.add_operation(Write(v.last_pos(), content))
    else:
        t.add_operation(Write(offset, content))
        v.add_operation(Write(offset, content))

__N_diff_comparison_phase = BuildingPhase.request_finalizing_phase()
__N_diff_normalization_phase = BuildingPhase.request_finalizing_phase()
__N_diff_fusion_phase = BuildingPhase.request_finalizing_phase()
        

@chrono
def finalize_diff_nodes(e : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all Diff nodes to compute their data attributes.
    """
    from time import time_ns

    from Viper.format import duration

    from ....logger import logger
    from ...config import CompilationParameters
    from .entities import Diff
    if e.major == "Finalizer" and e.minor == __N_diff_comparison_phase:
        logger.debug("Finalizing{} {} Diff nodes.".format(" and comparing" if not CompilationParameters.SkipLevenshteinForDiffNodes else "",len(Diff)))
        n = len(Diff)
        t0 = time_ns()
        t = t0
        for i, d in enumerate(Diff):
            d.compute_data()
            if (time_ns() - t) / 1000000000 > 15:
                t = time_ns()
                logger.debug("Finalizing {} Diff nodes : {:.2f}%. ETA : {}".format(len(Diff), (i + 1) / n * 100, duration(round((t - t0) / (i + 1) * (n - i - 1)))))

@chrono
def normalize_diff_nodes(e : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all Diff nodes to compare their diff file sizes and change their size accordingly.
    """
    from typing import Type

    from ....logger import logger
    from ...colors import Color
    from ...graph import Vertex
    from ..filesystem import File, Handle
    from ..network import Connection, Socket
    from .entities import Diff

    def project_range(x : float, sa : float, sb : float, da : float, db : float) -> float:
        if sa == sb:
            return (da + db) / 2
        p = (x - sa) / (sb - sa)
        return p * (db - da) + da

    def normalize_neighbor(cls : Type[Vertex]):
        if len(cls) > 0:
            logger.debug("Normalizing {} {} nodes.".format(len(cls), cls.__name__))
            a, b = min(sum(v.size for v in u.neighbors() if isinstance(v, Diff)) for u in cls), max(sum(v.size for v in u.neighbors() if isinstance(v, Diff)) for u in cls)
            minsize = Diff.min_size
            maxsize = Diff.max_size
            for u in cls:
                u.size = project_range(sum(v.size for v in u.neighbors() if isinstance(v, Diff)), a, b, minsize, maxsize)

    if e.major == "Finalizer" and e.minor == __N_diff_normalization_phase:
        logger.debug("Normalizing sizes of {} Diff nodes.".format(len(Diff)))
        if len(Diff) == 0:
            return
        a, b = min(len(d.glob) for d in Diff), max(len(d.glob) for d in Diff)
        minsize = 0.5
        maxsize = 3.0
        for d in Diff:
            d.size = project_range(len(d.glob), a, b, minsize, maxsize)
    
        for cls in (File, Handle, Socket, Connection):
            normalize_neighbor(cls)
        
        logger.debug("Normalizing colors of {} Diff nodes.".format(len(Diff)))
        a, b = min(d.glob_entropy for d in Diff), max(d.glob_entropy for d in Diff)
        for d in Diff:
            d.color = Color.linear((Diff.diff_low_entropy_color, Diff.diff_high_entropy_color), (1 - d.glob_entropy / 8, d.glob_entropy / 8))

@chrono
def fuse_diff_nodes(e : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all identical Diff nodes to be merged with their size increasing.
    """
    from ....logger import logger
    from ...graph import Graph
    from .entities import Diff

    groups : dict[Diff, int] = {}

    def merge(u : Diff, v : Diff):
        """
        Merges vertex v into vertex u (v gets deleted at the end).
        """
        for e in v.edges:
            if e.source is v:
                e.source = u
            if e.destination is v:
                e.destination = u
        v.edges.clear()
        for g in Graph.active_graphs():
            g.remove(v)
        groups[u] += 1

    if e.major == "Finalizer" and e.minor == __N_diff_fusion_phase:
        logger.debug("Fusing {} Diff nodes.".format(len(Diff)))
        for u in Diff:
            merged = False
            for v in filter(lambda v : v in groups, Diff):
                if u.content == v.content:
                    merge(v, u)
                    merged = True
                    break
            if not merged:
                groups[u] = 1
        
        resize_work = [u for u, n in groups.items() if n > 1]
        if resize_work:
            logger.debug("Resizing {} fused Diff nodes. Actually lost {} Diff nodes.".format(len(resize_work), len(Diff) - len(groups)))
            for u in resize_work:
                u.size *= groups[u] ** 0.5

        
BuildingPhase.add_callback(finalize_diff_nodes)
BuildingPhase.add_callback(normalize_diff_nodes)
BuildingPhase.add_callback(fuse_diff_nodes)





del BuildingPhase, Connection, File, Handle, Socket, chrono, entities, finalize_diff_nodes, fuse_diff_nodes, logger, normalize_diff_nodes, relations