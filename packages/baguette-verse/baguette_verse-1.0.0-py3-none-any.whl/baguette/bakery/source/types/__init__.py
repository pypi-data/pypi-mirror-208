"""
This package defines all the node types for building the graph. It contains multiple sub-packages that are behavioral models that BAGUETTE understands.
Each sub-package contains three modules : entities, relations and integration.
    - Entities modules contain all the Vertex subclasses defined for each behavioral model.
    - Relations modules contain all the Edge and Arrow subclasses defined for each behavioral model.
    - Integration modules contain special functions used by the compiler to integrate these entities and relations to BAGUETTES graphs.
Furthermore, for each sub-package, all entities and relations are also stored at package level.
"""

# Ground rules:
# - for each type package, define entities, relations and integration modules.
# - You should not reference relations or integrations globally in entities modules.
# - You should not reference integrations globally in relation modules.
# - Indeed these modules should be loaded in the order entities - relations - integrations globally (all entities first, then all relations, etc.)

from pathlib import Path
from importlib import import_module
modules = Path(__file__).parent.glob("*")

__all__ = [p.name for p in modules if p.is_dir() and "__init__.py" in [c.name for c in p.iterdir()]]

for m in __all__:
    import_module("." + m + ".entities", "baguette.bakery.source.types")
for m in __all__:
    import_module("." + m + ".relations", "baguette.bakery.source.types")
for m in __all__:
    import_module("." + m + ".integration", "baguette.bakery.source.types")
    del m

del Path, modules, import_module