"""
This module contains integration protocols for this behavioral package.
"""

from typing import Type

from ....logger import logger
from ...build import BuildingPhase
from ...event import Event
from ...graph import Arrow, Edge
from ...utils import chrono
from ..execution.entities import Call
from ..execution.utils import CallHandler
from . import entities, relations

__all__ = ["NewFile", "declare_existing_file"]





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

class NewFile(Event):

    """
    This is an Event thrown when a File Vertex is created.
    """

    __slots__ = {
        "file" : "The File Vertex of the file that was created"
    }

    def __init__(self, file : entities.File) -> None:
        self.file = file





namespace = {name : getattr(relations, name) for name in dir(relations)}
__file_to_dir_cls_table : dict[Type[Arrow | Edge], Type[Arrow | Edge]] = {}
for name, cls in filter(lambda c : isinstance(c[1], type) and issubclass(c[1], Arrow), namespace.items()):
    if name.endswith("File") and name[:-4] + "Directory" in namespace:
        __file_to_dir_cls_table[cls] = namespace[name[:-4] + "Directory"]
    del name, cls

__active_handles : dict[entities.Handle, str] = {}
__inverted_handles : dict[str, entities.Handle] = {}
__existing_files : dict[str, entities.File] = {}
__all_files : dict[str, list[entities.File]] = {}

def declare_existing_file(path : str):
    """
    Declares an existing file in the execution environment.
    """
    from ...utils import is_path
    from .entities import File
    if not isinstance(path, str):
        raise TypeError("Expected str, got " + repr(type(path).__name__))
    if not is_path(path):
        raise ValueError("Expected a valid file path for the execution platform, got " + repr(path))
    f = File()
    f.path = path
    if path not in __all_files:
        __all_files[path] = []
    __all_files[path].append(f)
    __existing_files[path] = f
    NewFile(f).throw()
    




@chrono
def integrate_file_creation(c : Call):
    """
    Creates a File/Directory vertex if it does not exists.
    """
    from ....logger import logger
    from .entities import File, Handle
    from .relations import CreatesFile, HasHandle, UsesFile
    if c.status == 1:
        logger.debug("File created.")
        if c.arguments.file_handle in __inverted_handles:
            h = __inverted_handles[c.arguments.file_handle]
        else:
            h = Handle()
            HasHandle(c.thread.process, h)
        if c.arguments.filepath in __existing_files:
            f = __existing_files[c.arguments.filepath]
            existed = True
        else:
            f = File()
            f.path = c.arguments.filepath
            existed = False
        CreatesFile(c, h)
        if not f in set(h.neighbors()):
            UsesFile(h, f)
        __inverted_handles[c.arguments.file_handle] = h
        __active_handles[h] = c.arguments.file_handle
        __existing_files[c.arguments.filepath] = f
        if c.arguments.filepath not in __all_files:
            __all_files[c.arguments.filepath] = []
        if not existed:
            __all_files[c.arguments.filepath].append(f)
        
        NewFile(f).throw()
        # if "FILE_LIST_DIRECTORY"
        # if "DELETE"
        # if "WRITE_DAC"
        # if "FILE_WRITE_ATTRIBUTES"
        # if "READ_CONTROL"
        # if "FILE_READ_EA"
        # if "FILE_WRITE_DATA"
        # if "FILE_WRITE_EA"
        # if "FILE_APPEND_DATA"
        # if "FILE_READ_ATTRIBUTES"
        # if "GENERIC_WRITE"
        # if "SYNCHRONIZE"
        # if "GENERIC_ALL"
        # if "FILE_READ_DATA" in c.flags.desired_access.split("|"):
        #     h.read = True
        # if "FILE_READ"

@chrono
def integrate_file_opening(c : Call):
    """
    Creates an File/Directory vertex.
    """
    from ....logger import logger
    from .entities import File, Handle
    from .relations import HasHandle, Opens, UsesFile
    if c.status == 1:
        logger.debug("File opened.")
        if c.arguments.file_handle in __inverted_handles:
            h = __inverted_handles[c.arguments.file_handle]
        else:
            h = Handle()
            HasHandle(c.thread.process, h)
        if c.arguments.filepath in __existing_files:
            f = __existing_files[c.arguments.filepath]
            existed = True
        else:
            f = File()
            f.path = c.arguments.filepath
            existed = False
        Opens(c, h)
        if not f in set(h.neighbors()):
            UsesFile(h, f)
        __inverted_handles[c.arguments.file_handle] = h
        __active_handles[h] = c.arguments.file_handle
        __existing_files[c.arguments.filepath] = f
        if c.arguments.filepath not in __all_files:
            __all_files[c.arguments.filepath] = []
        if not existed:
            __all_files[c.arguments.filepath].append(f)

        NewFile(f).throw()

@chrono
def integrate_file_closing(c : Call):
    """
    Connects a closing system call to the corresponding Handle.
    """
    from ....logger import logger
    from .relations import Closes
    if c.status == 1 and c.arguments.handle in __inverted_handles:
        logger.debug("File closed.")
        h = __inverted_handles.pop(c.arguments.handle)
        __active_handles.pop(h)
        Closes(c, h)

@chrono
def integrate_file_reading(c : Call):
    """
    Creates a Data vertex, and links it to the Handle and Call vertices.
    """
    from ....logger import logger
    from ..data import Data
    from ..data.integration import register_read_operation
    from .entities import File
    from .relations import Conveys, Reads
    if c.status == 1 and c.arguments.file_handle in __inverted_handles:
        logger.debug("Reading from file.")
        h = __inverted_handles[c.arguments.file_handle]
        d = Data()
        d.time = c.time
        d.set_data(c.arguments.buffer)
        f = h.file
        Reads(d, c)
        Conveys(h, d)
        if isinstance(f, File):
            register_read_operation(f, h, d.data, c.arguments.offset)

@chrono
def integrate_file_writing(c : Call):
    """
    Creates a Data vertex, and links it to the Handle and Call vertices.
    """
    from ....logger import logger
    from ..data import Data
    from ..data.integration import register_write_operation
    from .entities import File
    from .relations import Conveys, Writes
    if c.status == 1 and c.arguments.file_handle in __inverted_handles:
        logger.debug("Writing to file.")
        h = __inverted_handles[c.arguments.file_handle]
        d = Data()
        d.time = c.time
        d.set_data(c.arguments.buffer)
        f = h.file
        Writes(c, d)
        Conveys(d, h)
        if isinstance(f, File):
            register_write_operation(f, h, d.data, c.arguments.offset)
    
@chrono
def integrate_file_copying(c : Call):
    """
    Creates a File vertex, and links it to the original file it was copied from.
    """
    from ....logger import logger
    from .entities import File
    from .relations import IsCopyiedInto
    if c.status == 1:
        logger.debug("Copying file.")
        if c.arguments.oldfilepath in __existing_files:
            fs = __existing_files[c.arguments.oldfilepath]
        else:
            fs = File()
            fs.path = c.arguments.oldfilepath
            __existing_files[c.arguments.oldfilepath] = fs
            if c.arguments.oldfilepath not in __all_files:
                __all_files[c.arguments.oldfilepath] = []
            __all_files[c.arguments.oldfilepath].append(fs)
            NewFile(fs).throw()
        if c.arguments.newfilepath in __existing_files:
            fd = __existing_files[c.arguments.newfilepath]
        else:
            fd = File()
            fd.path = c.arguments.newfilepath
            __existing_files[c.arguments.newfilepath] = fd
            if c.arguments.newfilepath not in __all_files:
                __all_files[c.arguments.newfilepath] = []
            __all_files[c.arguments.newfilepath].append(fd)
            NewFile(fd).throw()
        IsCopyiedInto(fs, fd)

@chrono
def integrate_file_deleting(c : Call):
    # You need to make it possible to have multiple times the same file name...
    from ....logger import logger
    from .entities import File
    if c.status == 1:
        logger.debug("Deleting file.")
        if c.arguments.filepath not in __existing_files:
            f = File()
            f.path = c.arguments.filepath
            __existing_files[c.arguments.filepath] = f
            if c.arguments.filepath not in __all_files:
                __all_files[c.arguments.filepath] = []
            __all_files[c.arguments.filepath].append(f)
            NewFile(f).throw()
        else:
            f = __existing_files[c.arguments.filepath]
        f.color = f.deleted_file_color
        __existing_files.pop(c.arguments.filepath)





# File creation
CallHandler(integrate_file_creation, "NtCreateFile")

# File closing
CallHandler(integrate_file_opening, "NtOpenFile")

# File closing
CallHandler(integrate_file_closing, "NtClose")

# File reading
CallHandler(integrate_file_reading, "NtReadFile")

# File writing
CallHandler(integrate_file_writing, "NtWriteFile")

# File copying
CallHandler(integrate_file_copying, "CopyFileA", "CopyFileExW", "CopyFileW")

# File deleting
CallHandler(integrate_file_deleting, "DeleteFileW", "NtDeleteFile")





__N_phase = BuildingPhase.request_finalizing_phase()

def build_fs_tree(e : BuildingPhase):
    """
    When all File nodes have been created, this will replace those which are actually directories into Directory nodes and build the file system tree.
    """
    # TODO : You will need to make a version of this which keeps track of when files/directories exists to make sure your file system tree is indeed a tree !!!
    from pathlib import PurePath
    from typing import Type

    from ....logger import logger
    from ...graph import Edge, Graph, find_or_create
    from ..execution import Runs
    from ..network import Host
    from .entities import Directory, File
    from .relations import Contains, HasDrive

    disappearing : set[Type[Edge]] = {Runs}


    def mutate(f : File):
        d = Directory()
        d.path = str(f.path)
        d.size = f.size
        graphs = Graph.active_graphs()
        for e in f.edges.copy():
            src, dst = e.source if e.source is not f else d, e.destination if e.destination is not f else d
            e.delete()
            for g in graphs:
                g.remove(e)
            if type(e) in __file_to_dir_cls_table:
                T = __file_to_dir_cls_table[type(e)]
            else:
                T = type(e)
            if T not in disappearing:
                T(src, dst)
        for g in graphs:
            g.remove(f)
            g.append(d)
        return d
    

    if e.major == "Finalizer" and e.minor == __N_phase:
        logger.debug("Mutating up to {} File nodes.".format(len(File)))

        directories : dict[PurePath, list[Directory]] = {}
        files : dict[PurePath, list[File]] = {}
        for filelist in __all_files.values():
            path = filelist[0].path
            for file in filelist:
                paths = [path] + list(path.parents)
                p = paths.pop(0)
                if p not in files:
                    files[p] = []
                files[p].append(file)
                for dpath in paths:
                    if dpath not in directories:
                        directories[dpath] = []
                
        n = 0
        for path in files.copy():
            if path in directories:
                l = list(mutate(file) for file in files.pop(path))
                directories[path].extend(l)
                n += len(l)
        logger.debug("Actually mutated {} File nodes into Directory Nodes.".format(n))
    
        logger.debug("Creating missing directory nodes.")
        for path, filelist in directories.items():
            if not filelist:
                d = Directory()
                d.path = str(path)
                filelist.append(d)
            
        logger.debug("Building file system graph.")
        work : set[File | Directory] = {f for filelist in files.values() for f in filelist}

        while work:
            node = work.pop()
            path = node.path
            parent = path.parent
            if parent != path:
                for parent_node in directories[parent]:
                    Contains(parent_node, node)
                    work.add(parent_node)
            else:
                HasDrive(find_or_create(Host, domain = "host")[0], node)
        
        # Deleting references to irrelevent (mutated) File nodes
        __existing_files.clear()
        __all_files.clear()
                




# TODO : Add a backtracking phase for actual successive copies of files (those without modifications in between)!!!

BuildingPhase.add_callback(build_fs_tree)





del Arrow, BuildingPhase, Call, CallHandler, Edge, Event, Type, build_fs_tree, chrono, entities, integrate_file_closing, integrate_file_copying, integrate_file_creation, integrate_file_deleting, integrate_file_opening, integrate_file_reading, integrate_file_writing, logger, namespace, relations