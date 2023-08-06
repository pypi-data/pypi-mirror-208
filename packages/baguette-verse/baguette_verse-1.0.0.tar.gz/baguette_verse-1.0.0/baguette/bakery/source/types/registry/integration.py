"""
This module contains integration protocols for this behavioral package.
"""

from ....logger import logger
from ...build import BuildingPhase
from ...utils import chrono
from ..execution.entities import Call
from ..execution.utils import CallHandler
from . import entities, relations

__all__ = []





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

__existing_keys : dict[str, entities.Key] = {}
__inverted_handles : dict[str, entities.Handle] = {}
__active_handles : dict[entities.Handle, str] = {}
__existing_entries : dict[entities.Key, dict[str, entities.KeyEntry]] = {}
__deleted_entries : dict[entities.Key, dict[str, entities.KeyEntry]] = {}

@chrono
def __create_key_tree(key : str) -> entities.Key:
    """
    Creates all the missing keys in leading to the final key and returns the leaf Key node.
    """
    from ...graph import find_or_create
    from ..network import Host
    from .entities import Key
    from .relations import HasSubKey

    k = None
    last = find_or_create(Host, domain = "host")[0]
    for name in key.replace("\x00", "\uFFFD").split("\\"):
        name = name.lower().title()
        k = None
        for e in last.edges:
            if isinstance(e, HasSubKey) and e.source is last and e.destination.name == name:
                k = e.destination
                break
        if not k:
            k = Key()
            k.name = name
            HasSubKey(last, k)
            __existing_keys[k.path.lower()] = k
        last = k
    
    if not k:
        raise RuntimeError("Trying to create an unnamed registry key!")

    return k

@chrono
def __split_key_and_entry_names(path : str) -> tuple[str, str]:       # Might evolve later
    """
    Splits the given key entry path into the path of the last subkey and the name of the entry.
    """
    i = None
    for j, c in enumerate(reversed(path)):
        if c == "\\":
            i = -j - 1
            break
    if i == None:
        raise ValueError("Expected at least one '\\', got " + repr(path))
    return path[:i], path[i + 1:]

@chrono
def __find_last_key_entry(key : entities.Key, name : str) -> entities.KeyEntry | None:
    """
    Given a registry key and an entry name, returns the last entry known with this name.
    """
    if key in __existing_entries and name in __existing_entries[key]:
        return __existing_entries[key][name]

    



@chrono
def integrate_key_opening(c : Call):
    """
    Creates a new Key node if necessary when a key is opened.
    """
    from ....logger import logger
    from .entities import Handle
    from .relations import HasHandle, UsesKey
    if c.status == 1:
        logger.debug("Opening registry key.")
        if c.arguments.regkey.lower() in __existing_keys:
            k = __existing_keys[c.arguments.regkey.lower()]
        else:
            k = __create_key_tree(c.arguments.regkey)
        h = Handle()
        UsesKey(h, k)
        HasHandle(c.thread.process, h)
        if c.arguments.key_handle.lower() in __inverted_handles:
            logger.warning("Opening an already existing registry key handle.")
            return
        __inverted_handles[c.arguments.key_handle.lower()] = h
        __active_handles[h] = c.arguments.key_handle.lower()
        
@chrono
def integrate_key_enumeration(c : Call):
    """
    Finds the enumerated Key and sub-Key. Creates the sub-Key if it does not exist. Links the sub-Key to the Handle.
    """
    from ....logger import logger
    from .entities import Key
    from .relations import Discovered
    if c.status == 1:
        logger.debug("Enumerating from registry key.")
        k : Key
        sk : Key
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to enumerate a registry key with no known handle.")
            return
        h = __inverted_handles[c.arguments.key_handle.lower()]
        k = h.key
        if c.name != "NtEnumerateKey":
            sk = __create_key_tree(k.path + "\\" + c.arguments.key_name)
        else:
            sk = __create_key_tree(k.path + "\\" + c.arguments.buffer.encode("utf-8").decode("utf-16", errors="replace"))     # Cuckoo tried its best...which is quite bad!
        Discovered(h, sk)

@chrono
def integrate_key_closing(c : Call):
    """
    Closes a Handle associated with a Key.
    """
    from ....logger import logger
    if c.status == 1:
        logger.debug("Closing key handle.")
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to close unseen key handle.")
            return
        h = __inverted_handles.pop(c.arguments.key_handle.lower())
        __active_handles.pop(h)

@chrono 
def integrate_key_deleting(c : Call):
    """
    Marks a registry Key as deleted.
    """
    from ....logger import logger
    if c.status == 1:
        logger.debug("Deleting registry key.")
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to delete key from unseen handle.")
            return
        k = __create_key_tree(c.arguments.regkey)
        k.color = k.deleted_key_color
        __existing_keys.pop(k.path.lower())
        if k not in __deleted_entries:
            __deleted_entries[k] = {}
        if k in __existing_entries:
            __deleted_entries[k].update(__existing_entries.pop(k))

@chrono
def integrate_key_value_querying(c : Call):
    """
    Creates a KeyEntry node and marks it as read by thea key Handle.
    """
    from ....logger import logger
    from ...graph import Graph
    from .entities import KeyEntry
    from .relations import ChangesTowards, HasEntry, QueriesEntry
    if c.status == 1:
        logger.debug("Querying key entry.")
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to query value with unseen key handle.")
            return
        
        # Finding the open key handle :
        h = __inverted_handles[c.arguments.key_handle.lower()]
        k = h.key

        # Finding the last key in the path to the entry :
        if c.name == "NtEnumerateValueKey":
            sk_path, name = __split_key_and_entry_names(c.arguments.regkey + "\\" + c.arguments.key_name)
        else:
            sk_path, name = __split_key_and_entry_names(c.arguments.regkey)
        sk = __create_key_tree(sk_path)

        skp = sk
        while skp:
            if skp is k:
                break
            skp = skp.parent_key
            if not skp:
                logger.warning("There might be an unkown symbolic link in the registry or there is a problem:\nQuerying key '{}' from open key '{}'.".format(sk.path, k.path))

        # Creating a new KeyEntry object
        nv = KeyEntry[c.flags.reg_type]()
        nv.process_value(c.arguments.value)
        nv.name = name

        # Looking for an olod value for this entry
        ov = __find_last_key_entry(sk, nv.name)
        if not ov or ov.py_type != nv.py_type or ov.value != nv.value or (k in __deleted_entries and ov.name in __deleted_entries[k] and __deleted_entries[k][ov.name] is ov):    # New value is the first or is different : link to previous if there is one.
            v = nv
            if ov:
                ChangesTowards(ov, nv)
        else:                                                       # Old value is still good : delete new value.
            v = ov
            for g in Graph.active_graphs():
                g.remove(nv)
        
        if k not in __existing_entries:
            __existing_entries[k] = {}
        __existing_entries[k][v.name] = v
        if v not in sk.neighbors():
            HasEntry(sk, v)
        QueriesEntry(v, h)

@chrono
def integrate_key_value_setting(c : Call):
    """
    Creates a KeyEntry node and marks it as written by a key Handle.
    """
    from ....logger import logger
    from ...graph import Graph
    from .entities import KeyEntry
    from .relations import ChangesTowards, HasEntry, SetsEntry
    if c.status == 1:
        logger.debug("Setting key entry.")
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to set value with unseen key handle.")
            return
        
        # Finding the open key handle :
        h = __inverted_handles[c.arguments.key_handle.lower()]
        k = h.key

        # Finding the last key in the path to the entry :
        sk_path, name = __split_key_and_entry_names(c.arguments.regkey)
        sk = __create_key_tree(sk_path)

        skp = sk
        while skp:
            if skp is k:
                break
            skp = skp.parent_key
            if not skp:
                logger.warning("There might be an unkown symbolic link in the registry or there is a problem:\nSetting key '{}' from open key '{}'.".format(sk.path, k.path))

        # Creating a new KeyEntry object
        nv = KeyEntry[c.flags.reg_type]()
        nv.process_value(c.arguments.value)
        nv.name = name

        # Looking for an olod value for this entry
        ov = __find_last_key_entry(sk, nv.name)
        if not ov or ov.py_type != nv.py_type or ov.value != nv.value or (k in __deleted_entries and ov.name in __deleted_entries[k] and __deleted_entries[k][ov.name] is ov):    # New value is the first or is different : link to previous if there is one.
            v = nv
            if ov:
                ChangesTowards(ov, nv)
        else:                                                       # Old value is still good : delete new value.
            v = ov
            for g in Graph.active_graphs():
                g.remove(nv)
        
        if k not in __existing_entries:
            __existing_entries[k] = {}
        __existing_entries[k][v.name] = v
        if v not in sk.neighbors():
            HasEntry(sk, v)
        SetsEntry(h, v)

@chrono
def integrate_key_value_deleting(c : Call):
    """
    Creates a KeyEntry node and marks it as deleted by a key Handle.
    """
    from ....logger import logger
    from ...graph import Graph
    from .entities import KeyEntry
    from .relations import ChangesTowards, DeletesEntry, HasEntry
    if c.status == 1:
        logger.debug("Deleting key entry.")
        if c.arguments.key_handle.lower() not in __inverted_handles:
            logger.warning("Trying to set value with unseen key handle.")
            return
        
        # Finding the open key handle :
        h = __inverted_handles[c.arguments.key_handle.lower()]
        k = h.key

        # Finding the last key in the path to the entry :
        sk_path, name = __split_key_and_entry_names(c.arguments.regkey)
        sk = __create_key_tree(sk_path)

        skp = sk
        while skp:
            if skp is k:
                break
            skp = skp.parent_key
            if not skp:
                logger.warning("There might be an unkown symbolic link in the registry or there is a problem:\nDeleting key '{}' from open key '{}'.".format(sk.path, k.path))

        # Creating a new KeyEntry object

        # Looking for an old value for this entry
        ov = __find_last_key_entry(sk, name)
        if not ov:                                                  # New value is the first.
            raise RuntimeError("Here is what you got " + repr(c))
        else:                                                       # Old value : link to new value and delete new.
            nv = KeyEntry[ov.reg_type]()                            # type: ignore      Indeed the type-checker is too dump to know about __class_getitem__...
            ChangesTowards(ov, nv)
            v = nv
            nv.process_value(ov.value)
            for g in Graph.active_graphs():
                g.remove(nv)
        
        if k not in __existing_entries:
            __existing_entries[k] = {}
        __existing_entries[k][v.name] = v
        if k not in __deleted_entries:
            __deleted_entries[k] = {}
        __deleted_entries[k][v.name] = v
        v.color = v.deleted_key_entry_color
        if v not in sk.neighbors():
            HasEntry(sk, v)
        DeletesEntry(h, v)





# Key opening
CallHandler(integrate_key_opening, "RegOpenKeyExA", "NtOpenKeyEx", "NtOpenKey", "RegOpenKeyExW")

# Key creation
CallHandler(integrate_key_opening, "NtCreateKey", "RegCreateKeyExW", "RegCreateKeyExA")

# Key enumeration
CallHandler(integrate_key_enumeration, 'RegEnumKeyW', 'NtEnumerateKey', 'RegEnumKeyExW', 'RegEnumKeyExA')

# Key closing
CallHandler(integrate_key_closing, 'RegCloseKey')

# Key deleting
CallHandler(integrate_key_deleting, 'NtDeleteKey', 'RegDeleteKeyW', 'RegDeleteKeyA')

# Key entry querying
CallHandler(integrate_key_value_querying, 'NtQueryValueKey', 'RegQueryValueExW', 'RegQueryValueExA', "RegEnumValueW", 'RegEnumValueA', 'NtEnumerateValueKey')

# Key entry setting
CallHandler(integrate_key_value_setting, 'RegSetValueExW', 'RegSetValueExA', 'NtSetValueKey')

# Key entry deleting
CallHandler(integrate_key_value_deleting, 'RegDeleteValueW', 'RegDeleteValueA', 'NtDeleteValueKey')





__N_referencing_phase = BuildingPhase.request_finalizing_phase()

def find_filesystem_references(ev : BuildingPhase):
    """
    When called with the right finalizing phase event, will cause all KeyEntry nodes to link to File or Folder nodes that their value reference if these entries were modified.
    """
    from ....logger import logger
    from ...utils import is_path, parse_command_line, path_factory
    from ..filesystem import Contains, Directory, File, HasDrive
    from ..network import Host
    from .entities import KeyEntry, Key_SZ_Entry, Key_MULTI_SZ_Entry
    from .relations import DeletesEntry, ReferencesFileSystem, SetsEntry
    if ev.major == "Finalizer" and ev.minor == __N_referencing_phase:
        logger.debug("Finding references to filesystem in {} registry key entries.".format(len(KeyEntry)))
        for ke in KeyEntry:

            if not isinstance(ke, Key_SZ_Entry | Key_MULTI_SZ_Entry):
                continue

            ok = False

            for e in ke.edges:
                if isinstance(e, SetsEntry | DeletesEntry):
                    ok = True
                    break
            if not ok:
                continue

            ok = False
            
            if isinstance(ke, Key_SZ_Entry):
                base_possibilities : list[str] = [ke.value]
            else:
                base_possibilities : list[str] = ke.value

            possibilities = []
            for p in base_possibilities:
                try:
                    args = parse_command_line(p)
                    possibilities.extend(args)
                except KeyboardInterrupt:
                    raise
                finally:
                    possibilities.append(p)
            
            for p in possibilities:
                if is_path(p) and p:
                    p = path_factory(p)
                    current : Host | Directory | File = Host.current
                    next : Directory | File | None
                    parts = list(p.parts)
                    if ":" in parts[0]:
                        parts[0] = parts[0].replace("\\", "")
                    for pi in parts:
                        next = None
                        for e in current.edges:
                            if isinstance(e, HasDrive | Contains) and e.source is current and e.destination.name.lower() == pi.lower():
                                next = e.destination
                                break
                        if next is None:
                            break
                        current = next
                    else:
                        ReferencesFileSystem(ke, current)
        
        logger.debug("Got {} references to filesystem nodes.".format(len(ReferencesFileSystem)))

BuildingPhase.add_callback(find_filesystem_references)





del BuildingPhase, Call, CallHandler, chrono, entities, find_filesystem_references, integrate_key_closing, integrate_key_deleting, integrate_key_enumeration, integrate_key_opening, integrate_key_value_deleting, integrate_key_value_querying, integrate_key_value_setting, logger, relations