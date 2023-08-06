from io import IOBase
from ..logger import logger
from typing import Any, Dict, Iterator, TypeVar
from .utils import *
from .graph import Graph
from .event import Event
from .types.execution.entities import Process, Call
import os
from threading import Lock





class BuildingPhase(Event):
    
    """
    This class of event is made to notify the system that we are entering a new buidling phase.
    The major attribute is the name of the phase.
    The minor attribute indicates the iteration number of this phase.
    """

    __lock = Lock()
    __extra_phases = 0

    __slots__ = {
        "major" : "The name of the phase of which the execution is starting.",
        "minor" : "The iteration number of this phase."
    }

    def __init__(self, major : str, minor : int) -> None:
        self.major = major
        self.minor = minor
    
    @staticmethod
    def request_finalizing_phase() -> int:
        """
        Requests a new finalizing phase to be performed by the Builder.
        Returns the integer assigned to the minor of the scheduled finalizer phase.
        """
        with BuildingPhase.__lock:
            n = BuildingPhase.__extra_phases
            BuildingPhase.__extra_phases += 1
            return n
    
    @staticmethod
    def finalizing_steps() -> int:
        """
        Returns the number of finalizing steps tp be performed.
        """
        with BuildingPhase.__lock:
            return BuildingPhase.__extra_phases





class Builder:

    def __init__(self, data : str | IOBase | dict) -> None:
        if isinstance(data, str):
            try:
                data = open(data, "r")
            except:
                raise 
        if isinstance(data, IOBase):
            from json import load, JSONDecodeError
            try:
                data = load(data)
                logger.info("File loaded and structured.")
            except JSONDecodeError:
                raise
        if not isinstance(data, dict):
            raise TypeError("Expected dict or json file, got " + repr(data.__class__.__name__))
        self.data = data
        self._progress = 0
        self._target = 1
    
    @property
    def progress(self) -> float:
        """
        Returns the progress (between 0.0 and 1.0) of the current task.
        """
        return self._progress / self._target

    def calls(self) -> Iterator[Dict[str, Any]]:
        """
        Yields all the calls' data.
        """
        for process in self.data["behavior"]["processes"]:
            for call in process["calls"]:
                yield call

    def machines(self) -> Iterator[Dict[str, str]]:
        """
        Yields all the machines' data.
        """
        if "domains" not in self.data["network"]:
            return
        for machine in self.data["network"]["domains"]:
            yield machine

    def hostIP(self) -> str:
        """
        Returns the host machine's IP address.
        """
        import re
        expr = re.compile(r"\[cuckoo.core.resultserver\] DEBUG: Now tracking machine (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) for task #\d+\n")
        for line in self.data["debug"]["cuckoo"]:
            if expr.search(line):
                match = expr.search(line)
                if match:
                    return match.group(1)
        logger.warning("Could not find the host's IP address.")
        return ""
    
    def sample_file_path(self) -> str:
        """
        Finds the name of the sample file in the report and returns its absolute path in the execution environment.
        """
        from ..source.types.execution import Process
        from ..source.utils import parse_command_line
        fname = self.data["target"]["file"]["name"]
        pid = None
        for p in self.data["behavior"]["processtree"]:      # Look only at the processes that Cuckoo started itself.
            for arg in parse_command_line(p["command_line"]):
                if arg.endswith(fname):
                    pid = p["pid"]
        if pid != None:
            for p in Process:
                if p.PID == pid:
                    return p.executable
        raise RuntimeError("Could not find malware process")
        

    @chrono
    def build(self) -> None:
        BuildingPhase("Initialization", 0).throw()
        from .graph import Graph
        from .types.execution import Thread, Call, FollowedBy, Process, NextSignificantCall
        from .types.network import Host, SpawnedProcess
        from .types.filesystem.integration import declare_existing_file
        from .graph import find_or_create
        from .types.execution.utils import CallHandler
        self.graph = Graph()

        with self.graph:

            BuildingPhase("Network Discovery", 0).throw()
            logger.info("Identifying machines.")

            for machine in self.machines():
                h = Host()
                h.address = machine["ip"]
                h.domain = machine["domain"]
            
            logger.info("Identifying host machine.")
            
            self.host = find_or_create(Host, address = self.hostIP())[0]
            Host.current = self.host
            self.host.domain = "host"
            self.host.platform = self.data["info"]["platform"]
            self.graph.data["platform"] = self.data["info"]["platform"]

            BuildingPhase("Input Parsing", 0).throw()
            logger.debug("Discovering work on calls.")

            self._target = 0
            for process in self.data["behavior"]["processes"]:
                self._target += len(process["calls"])
            
            N_calls = self._target
            logger.info("{} Calls to find.".format(self._target))

            # Building the basic execution graph
            BuildingPhase("Graph Building", 0).throw()
            logger.info("Building execution star.")
            for process in self.data["behavior"]["processes"]:
                self.graph.add_vertex(self.process_to_vertex(process), False)

            # Creating a file node for the sample file.
            logger.debug("Creating sample file.")
            try:
                path = self.sample_file_path()
                declare_existing_file(path)
            except RuntimeError:
                logger.error("Could not find the process executing the sample.")

            # Discovering calls
            logger.info("Discovering {} calls.".format(N_calls))
            calls : list[Call] = []
            self._target += len(Call) * 2
            seen = set()
            for t in Thread:
                a = t.first
                while a != None:
                    if a in seen:
                        logger.warning("A call has been seen twice while listing.")
                        break
                    seen.add(a)
                    calls.append(a)
                    _target = None
                    for l in a.edges:
                        if isinstance(l, FollowedBy) and l.destination is not a:
                            _target = l.destination
                            break
                    a = _target
            if len(calls) < N_calls:
                logger.warning("{} calls have been forgotten!".format(N_calls - len(calls)))
            
            # Sorting calls based on time
            logger.info("Sorting calls based on time.")
            calls.sort(key = lambda a : a.time)

            # Interpreting each Call
            BuildingPhase("Call Interpretation", 0).throw()
            logger.info("Integrating {} calls.".format(N_calls))
            for a in calls:
                CallHandler.integrate_chain(a)
                self._progress += 1
            
            # Linking processes to host
            BuildingPhase("Process Attribution", 0).throw()
            logger.info("Linking root processes to host machine.")
            p : Process
            for p in Process:
                if not p.parent_process:
                    SpawnedProcess(self.host, p)
            
            # Making skip links
            BuildingPhase("Call Skip-Linking", 0).throw()
            logger.info("Adding skip links in system call sequences")
            for t in Thread:
                last = t.first
                new = last
                while new and last:
                    if new is not last:
                        for l in new.edges:
                            if not isinstance(l, FollowedBy):
                                NextSignificantCall(last, new)
                                last = new
                                break
                    next_call = None
                    for l in new.edges:
                        if isinstance(l, FollowedBy) and l.destination is not new:
                            next_call = l.destination
                            break
                    new = next_call
            
            # Extra building phases
            for i in range(BuildingPhase.finalizing_steps()):
                logger.info("Running finalization phase #{}.".format(i + 1))
                BuildingPhase("Finalizer", i).throw()

    @chrono
    def flush_graph(self):

        logger.info("Flushing graph.")

        from ..source.graph import Vertex, UniqueVertex, Edge, Arrow
        Self = TypeVar("Self", bound = type)

        def subclass_iterator(cls : Self) -> Iterator[Self]:
            for c in cls.__subclasses__():
                yield c
                for ci in subclass_iterator(c):
                    yield ci
        
        for cls in subclass_iterator(Vertex):
            if cls != UniqueVertex:
                logger.debug("Adding {} {} vertices to the graph.".format(len(cls), cls.__name__))
                cls.add_vertices_to_graph(self.graph)
        for cls in subclass_iterator(Edge):
            if cls != Arrow:
                logger.debug("Adding {} {} edges to the graph.".format(len(cls), cls.__name__))
                cls.add_edges_to_graph(self.graph)

    @chrono
    def process_to_vertex(self, process : dict) -> Process:
        from ..source.graph import find_or_create
        from ..source.types.execution import Process, Thread, Call, HasChildProcess, HasThread, HasFirstCall, FollowedBy
        from ..source.types.imports import Import, HasImport
        p : Process
        t : Thread
        a : Call
        p, _ = find_or_create(Process, PID = process["pid"])
        p.executable = process["process_path"]
        p.command = process["command_line"]
        p.start = process["first_seen"]
        p2, _ = find_or_create(Process, PID = process["ppid"])
        e = HasChildProcess(p2, p)

        for imp in process["modules"]:
            basename : str = imp["basename"]
            length : int = imp["imgsize"]
            path : str = imp["filepath"]
            if basename.lower().endswith(".dll"):
                imp, _ = find_or_create(Import, name = basename.lower()[:-4], path = path, length = length)
                HasImport(p, imp)

        for i, ci in enumerate(process["calls"]):
            t, existed = find_or_create(Thread, TID = ci["tid"])
            if not existed:
                HasThread(p, t)
            a = self.api_to_vertex(ci)
            a.thread = t
            if t.first == None:
                t.first = a
                t.last = a
                t.Ncalls = 1
                HasFirstCall(t, a)
            elif t.last:
                FollowedBy(t.last, a)
                t.last = a
                t.Ncalls += 1
            self._progress += 1

        for t in p.threads:
            if t.first and t.last:
                t.start = t.first.time
                t.stop = t.last.time
        
        p.start = min((t.start for t in p.threads), default=p.start)
        p.stop = max((t.stop for t in p.threads), default=p.start)

        return p

    @chrono
    def api_to_vertex(self, call : dict) -> Call:
        from ..source.record import record
        from ..source.types.execution import Call
        a = Call()
        a.name = call["api"]
        a.category = call["category"]
        a.stacktrace = tuple(call["stacktrace"])
        a.status = call["status"]
        a.arguments = record(**call["arguments"])
        a.return_value = call["return_value"]
        a.time = call["time"]
        a.flags = record(**call["flags"])
        return a





def build(file : str | IOBase) -> "Graph":
    if isinstance(file, str):
        file = open(file, "rb")
    try:
        b = Builder(file)
    except:
        raise TypeError("Expected file, got " + repr(file.__class__.__name__))
    b.build()
    return b.graph


__all__ = ["Builder", "build"]