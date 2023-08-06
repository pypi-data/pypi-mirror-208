from ....logger import logger





__proc__.init = ""
__proc__.term = "__init__"          # This is to trick most IDEs into thinking that the init code will be executed first, but it is only done at the end to avoid circular imports

__all__ = ["entities", "relations", "integration"]





logger.info("Initializing {} library.".format(__name__.rpartition(".")[2]))