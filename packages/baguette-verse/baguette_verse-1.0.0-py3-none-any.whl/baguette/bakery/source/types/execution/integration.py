"""
This module contains integration protocols for this behavioral package.
"""

from ....logger import logger
from ...build import BuildingPhase
from ...utils import chrono
from . import entities, relations
from .utils import CallHandler

__all__ = []





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def integrate_thread_creation(c : entities.Call):
    """
    Links a Thread vertex to the Call vertex (from another thread) that created it.
    """
    from ....logger import logger
    from ...graph import find_or_create
    from .entities import Thread
    from .relations import InjectedThread, StartedThread
    if c.arguments.thread_identifier != 0:      # Should indicate that the call failed
        logger.debug("New thread detected.")
        t : Thread
        t, ok = find_or_create(Thread, TID = c.arguments.thread_identifier)
        l = StartedThread(c, t)
        if c.name in {"CreateRemoteThread", "CreateRemoteThreadEx"}:
            logger.info("Detected thread injection.")
            l.remote = True
            p = c.thread.process
            InjectedThread(p, t)

@chrono
def integrate_process_creation(c : entities.Call):
    """
    Links a Process vertex to the Call vertex (from another process) that created it.
    """
    from ....logger import logger
    from ...graph import find_or_create
    from .entities import Process
    from .relations import StartedProcess
    if c.arguments.process_identifier != 0:
        logger.debug("New process detected.")
        p : Process
        p, ok = find_or_create(Process, PID = c.arguments.process_identifier)
        l = StartedProcess(c, p)
        




# Thread creation handlers
CallHandler(integrate_thread_creation, "CreateThread")          # Basic thread creation
CallHandler(integrate_thread_creation, "CreateRemoteThread", "CreateRemoteThreadEx")    # Remote thread creation (into another process)

# Process creation handlers
CallHandler(integrate_process_creation, lambda name : "CreateProcess" in name)





__N_phase = BuildingPhase.request_finalizing_phase()

@chrono
def remove_cuckoo_phantom_processes(ev : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause Process nodes which represent Cuckoo process (inital processes with no info available) to be erased.
    """
    from ....logger import logger
    from ...graph import Graph
    from ..network import Host, SpawnedProcess
    from .entities import Process
    if ev.major == "Finalizer" and ev.minor == __N_phase:
        logger.debug("Erasing Cuckoo phantom processes.")
        n = 0
        h = Host.current
        for e in h.edges.copy():
            p = e.destination
            if isinstance(p, Process) and not p.parent_process and not p.executable:
                for pi in p.children_processes:
                    SpawnedProcess(h, pi)
                for ei in p.edges.copy():
                    if isinstance(e, SpawnedProcess):
                        h = e.source
                    ei.delete()
                    for g in Graph.active_graphs():
                        g.remove(ei)
                for g in Graph.active_graphs():
                    g.remove(p)
                n += 1
        if n:
            logger.debug("Actually removed {} Cuckoo process{}.".format(n, "es" if n > 1 else ""))





BuildingPhase.add_callback(remove_cuckoo_phantom_processes)





del BuildingPhase, CallHandler, chrono, entities, integrate_process_creation, integrate_thread_creation, logger, relations, remove_cuckoo_phantom_processes