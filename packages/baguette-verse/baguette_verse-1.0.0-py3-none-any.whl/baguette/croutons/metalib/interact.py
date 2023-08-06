"""
This module can be launched to run an interactive session to work with MetaGraphs.
"""

from ...bakery.logger import set_level
import logging
set_level(logging.WARNING)
from ..metalib.utils import *
from ..metalib.evaluator import Evaluator

import_env(globals())

env = globals().copy()
env.pop("import_env")

from Viper.interactive import InteractiveInterpreter

InteractiveInterpreter(env).interact("MetaLib interactive console.\nUse save(MG, name) and load(name) to save and load MetaGraphs.\nUse entries() to get a list of all MetaGraphs available in the library.\nUse remove(name) to delete a MetaGraph from the library.\nAll useful types are loaded, including Graph and MetaGraph related types, as well as Evaluators.")