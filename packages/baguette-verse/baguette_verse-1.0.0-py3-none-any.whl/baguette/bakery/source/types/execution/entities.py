"""
This module contains Vertex subclasses for this behavioral package.
"""

from typing import Optional

from ....logger import logger
from ...colors import Color
from ...config import ColorSetting, SizeSetting
from ...graph import UniqueVertex, Vertex
from ...utils import chrono

__all__ = ["Process", "Thread", "Call"]





logger.info("Loading entities from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

CommandTree = list[tuple[str, "CommandTree"]]

class Process(UniqueVertex):

    """
    A process vertex. Holds information to identify a process.
    """

    __slots__ = {
        "PID" : "The PID of the process during its execution",
        "__command" : "The command that this process is running",
        "executable" : "The file system path that the process was started in",
        "start" : "The time at which the process was started",
        "stop" : "The time at chich the process was stopped",
        "__sub_commands" : "The tree of commands executed by all chile processes"
    }

    __pickle_slots__ = {
        "PID",
        "command",
        "executable",
        "start",
        "stop",
        "sub_commands"
    }

    default_color = ColorSetting(Color(255, 255, 50))
    default_size = SizeSetting(5.0)

    def __init__(self, *, parent: Vertex | None = None) -> None:
        super().__init__(parent=parent)
        self.PID : int = 0
        self.__command : tuple[str] = tuple()
        self.executable : str = ""
        self.start : float = 0.0
        self.stop : float = 0.0
        self.__sub_commands : CommandTree | None = None

        from argparse import ArgumentParser
        from pathlib import PurePath

        from ...utils import is_path, path_factory
        from ..filesystem.integration import NewFile
        from .relations import Runs, UsesAsArgument

        def to_absolute(p : PurePath, cwd : PurePath) -> PurePath:
            if p.is_absolute():
                return p
            return cwd / p
        
        p = ArgumentParser()
        
        def link(e : NewFile):
            from ..filesystem import File
            f = e.file
            if not f.name:
                return
            # print("New file :", repr(f.path))
            # # print("Process :", repr(self.command))
            # print("Process #{} : '{}'".format(self.PID, self.executable))
            # print("Splitting command : {}".format(self.__command))
            for i, arg in enumerate(self.__command):
                if not i:
                    arg = self.executable
                while arg.endswith(" "):
                    arg = arg[:-1]
                while arg.startswith(" "):
                    arg = arg[1:]
                if arg.startswith("\"") and arg.endswith("\""):
                    arg = arg[1:-1]
                if arg.startswith("'") and arg.endswith("'"):
                    arg = arg[1:-1]
                # print(">>>", f.name.lower(), arg.lower())
                if (is_path(arg) and f.name.lower() == to_absolute(path_factory(arg), path_factory(self.executable)).name.lower()) or f.name.lower() in arg.lower():
                # if (f.name in arg and len(f.name) / len(arg) > 0.9) or (str(f.path) in arg and len(str(f.path)) / len(arg) > 0.9):        # You need to work with a process cwd
                    if i > 0:
                        UsesAsArgument(self, f)
                        break
                    else:
                        Runs(self, f)

        NewFile.add_callback(link)

    @property
    def label(self) -> str:
        """
        Returns a label for the Process node.
        """
        return "Process #" + str(self.PID)
        
    @property
    def threads(self) -> list["Thread"]:
        """
        List of all the threads that this process had.
        """
        from .relations import HasThread
        return [e.destination for e in self.edges if isinstance(e, HasThread)] 
    
    @property
    def children_processes(self) -> list["Process"]:
        """
        List of all the children processes that this process created.
        """
        from .relations import HasChildProcess
        return [e.destination for e in self.edges if isinstance(e, HasChildProcess) and e.source is self]
    
    @property
    def parent_process(self) -> Optional["Process"]:
        """
        Returns the parent process node if one exists in the graph.
        """
        from .relations import HasChildProcess
        for e in self.edges:
            if isinstance(e, HasChildProcess) and e.destination is self:
                return e.source
            
    @property
    def command(self) -> str:
        """
        The command ran by this Process.
        """
        return " ".join(self.__command)
    
    @command.setter
    def command(self, cmd : str):
        from ...utils import parse_command_line
        if not isinstance(cmd, str):
            raise TypeError("Expected str, got " + repr(type(cmd).__name__))
        self.__command = tuple(parse_command_line(cmd))
        if not self.__command and self.executable:
            self.__command = (self.executable, )
        
    def parsed_command(self) -> list[str]:
        """
        Returns the argument vector used for starting this process.
        """
        return list(self.__command)

    @property
    def sub_commands(self) -> CommandTree:
        """
        Returns a dict structure that represents the commands executed by all child processes.
        """
        from .relations import HasChildProcess
        if self.__sub_commands != None:
            return self.__sub_commands
        sc = []
        for e in self.edges:
            if isinstance(e, HasChildProcess) and e.source is self:
                sc.append((e.destination.command, e.destination.sub_commands))
        self.__sub_commands = sc
        return sc
    
    @sub_commands.setter
    def sub_commands(self, value : CommandTree):
        self.__sub_commands = value





class Thread(UniqueVertex):

    """
    A thread vertex. Holds information to identify a thread.
    """

    __slots__ = {
        "TID" : "The TID of the thread during its execution",
        "Ncalls" : "The number of system calls that the thread made",
        "first" : "The first system call that this thread made",
        "last" : "the last system call that this thread made",
        "start" : "The time at which the thread was started",
        "stop" : "The time at chich the thread was stopped"
    }

    __pickle_slots__ = {
        "TID",
        "Ncalls",
        "first",
        "last",
        "start",
        "stop"
    }

    default_color = ColorSetting(Color(255, 204, 0))
    default_size = SizeSetting(2.0)

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        super().__init__(parent=parent)
        self.TID : int = 0
        self.Ncalls : int = 0
        self.first : Call | None = None
        self.last : Call | None = None
        self.start : float = 0.0
        self.stop : float = 0.0

    @property
    def label(self) -> str:
        """
        Returns a label for the Thread node.
        """
        return "Thread #" + str(self.TID)
    
    @property
    def process(self) -> Process:
        """
        The Process Vertex that runs this Thread.
        """
        from .relations import HasThread
        for e in self.edges:
            if isinstance(e, HasThread):
                return e.source
        raise RuntimeError("Got a Thread without a parent Process.")





class Call(UniqueVertex):

    """
    A system call vertex. Holds information about a specific system call.
    Don't forget to call c.integrate() after setup of Call c is finished to integrate the call in the graph.
    """

    __slots__ = {
        "name" : "The name of the system call",
        "category" : "The family of the system call",
        "stacktrace" : "The stacktrace of the call",
        "status" : "Indicates if the call ran succesfully",
        "arguments" : "The arguments that the call received",
        "return_value" : "The value that the call returned",
        "time" : "The timestamp at which the call was detected",
        "flags" : "The flags of the call",
        "__thread" : "A shortcut to the Thread vertex that made this call"
    }

    __pickle_slots__ = {
        "name",
        "category",
        "stacktrace",
        "status",
        "arguments",
        "return_value",
        "time",
        "flags",
        "thread"
    }

    default_color = ColorSetting(Color(255, 153, 0))
    default_size = SizeSetting(0.3)

    def __init__(self, *, parent: Optional[Vertex] = None) -> None:
        from typing import Any

        from ...record import record
        super().__init__(parent=parent)
        self.name : str = ""
        self.category : str = ""
        self.stacktrace : tuple = ()
        self.status : int = 0
        self.arguments : record = record()
        self.return_value : Any = None
        self.time : float = 0.0
        self.flags : record = record()
        self.__thread : Thread | None = None
    
    @property
    def thread(self) -> Thread:
        """
        The Thread that made this Call.
        """
        if self.__thread is None:
            raise RuntimeError("Got a Call without a calling Thread.")
        return self.__thread
    
    @thread.setter
    def thread(self, value : Thread):
        if not isinstance(value, Thread):
            raise TypeError("Expected Thread, got " + repr(type(value).__name__))
        self.__thread = value

    @property
    def label(self) -> str:
        """
        The label for this node.
        """
        return self.name
    




del Color,ColorSetting, SizeSetting, CommandTree, Optional, UniqueVertex, Vertex, chrono, logger