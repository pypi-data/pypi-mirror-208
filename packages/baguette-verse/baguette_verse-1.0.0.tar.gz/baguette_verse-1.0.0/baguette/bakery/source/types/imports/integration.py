"""
This module contains integration protocols for this behavioral package.
"""

from ....logger import logger
from ...utils import chrono
from ..filesystem.integration import NewFile
from . import entities, relations

__all__ = []





logger.info("Loading integrations from {} library.".format(__name__.rpartition(".")[0].rpartition(".")[2]))

@chrono
def link(e : NewFile):
    from ...graph import find_or_create
    from .entities import Import
    from .relations import IsFile
    if e.file.path.suffix.lower().endswith(".dll"):
        I, ok = find_or_create(Import, path = e.file.name)
        if not ok:
            import re
            expr1 = re.compile(r"([a-zA-Z0-9_.]+)(\..*?)$")
            match = expr1.search(e.file.name)
            if match:
                I.name = match.group(1).lower()
            else:
                I.name = e.file.name
        IsFile(I, e.file)

NewFile.add_callback(link)





del NewFile, chrono, entities, link, logger, relations