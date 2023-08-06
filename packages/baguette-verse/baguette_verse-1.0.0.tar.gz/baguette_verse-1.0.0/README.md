# BAGUETTE-VERSE

This is the BAGUETTE framework. BAGUETTE stands for **Behavioral Analysis Graph Using Execution Traces Towards Explanability**.
BAGUETTE is a **heterogeneous graph** data structure used to represent the **behavior of malware samples**.

The BAGUETTE-VERSE is a framework to build and analyze BAGUETTE graphs.

BAGUETTE requires Python >= 3.10 as well as three Python modules: viper_lib, python-magic and Levenshtein. You can install all these dependencies by hand, but the easiest way is just to use `pip` in the Python installation you want to use:

```$ pip install baguette-verse```

BAGUETTE is a pure Python project, meaning that a BAGUETTE graph is a Python data structure and for now can only be manipulated using the Python interface described below.

## Bakery

**Bakery** is the package used to bake (compile) BAGUETTE graphs. For now, BAGUETTEs can only be made from Cuckoo execution reports. From that, the baker will create a BAGUETTE packaging:
Inside of a ".bag" folder, you may find :
- the "baguette.pyt" file which contains the **pickle** of the BAGUETTE graph
- the "visual.gexf" file, which is a **visualizable** graph format to use with **[Gephi](https://gephi.org/)**
- a "index.pyt" file which holds **metadata** about the given BAGUETTE.

The process of baking a baguette is done throught the 'bake' command:

```
$ bake --help
usage: bake [-h] [--baguettes [BAGUETTES ...]] [--visuals [VISUALS ...]] [-o [OUTPUTS ...]] [--pool POOL] [--maxtime MAXTIME]
            [-f [{injected_threads_only,modified_registry_only,no_data_nodes,no_handle_nodes,no_simple_imports,significant_call_only,significant_processes_only} ...]] [--perf] [-v] [--skip_data_comparison]
            [--skip_diff_comparison]
            reports [reports ...]

Bakes Cuckoo reports into baguettes (gexf and pyt graphs).
[...]

$ ls
sample.json
$ bake sample.json
All 1 are well-baked!
$ ls
sample.bag
sample.json
$ ls sample.bag
baguette.pyt
index.pyt
visual.gexf
```

Use the help to see all the options of this command and have more information.

BAGUETTE graphs are **heterogeneous graphs**, meaning that their vertices, edges and arrows all have **types** (actual Python classes). To explore the possiblities of these graphs, you can list all these classes from the package `bakery.source.types`. Just open an interactive Python interpreter, import them and explore!
```
>>> from baguette.bakery.source import types

>>> dir(types)
['__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', 'data', 'execution', 'filesystem', 'imports', 'network', 'registry']

>>> dir(types.filesystem)
['Closes', 'Contains', 'Conveys', 'CreatesDirectory', 'CreatesFile', 'DeletesDirectory', 'DeletesFile', 'Directory', 'Edge', 'File', 'Handle', 'HasDrive', 'HasHandle', 'Host', 'IsCopyiedInto', 'NewFile', 'Opens', 'Process', 'Reads', 'Type', 'UsesDirectory', 'UsesFile', 'Writes', '_N_phase', '__all__', '__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_active_handles', '_all_files', '_existing_files', '_file_to_dir_cls_table', '_inverted_handles', 'cls', 'declare_existing_file', 'name', 'namespace']
>>> from baguette.bakery.source.graph import *  # This imports the base graph-related classes

>>> [name for name in dir(types.filesystem) if isinstance(getattr(types.filesystem, name), type) and issubclass(getattr(types.filesystem, name), (Vertex, Edge))]
['Closes', 'Contains', 'Conveys', 'CreatesDirectory', 'CreatesFile', 'DeletesDirectory', 'DeletesFile', 'Directory', 'Edge', 'File', 'Handle', 'HasDrive', 'HasHandle', 'Host', 'IsCopyiedInto', 'Opens', 'Process', 'Reads', 'UsesDirectory', 'UsesFile', 'Writes', 'cls']
```

All types defined in this version of BAGUETTE can be found here:

![Alt Text](https://gitlab.inria.fr/vraulin/baguette-verse/-/raw/992c3bec53d703c488759464a3c1b3ff3746025f/BAGUETTE_ingredients_with_bg.png "The types of vertices, edges and arrows available in BAGUETTE (most of them)")

To study a BAGUETTE sample "by hand", you can just open your Python interactive interpreter and load the sample from the "baguette.pyt" file with **pickle**:

```
>>> from pickle import load

>>> with open("sample.bag/baguette.pyt", "rb") as f:
...     bag = load(f)

>>> len(bag.vertices)   # Number of vertices
38900

>>> len(bag.edges)      # Number of edges
43757

>>> {type(v).__name__ for v in bag.vertices}    # All the vertex types in this sample
{'Thread', 'Host', 'Import', 'Handle', 'Directory', 'Process', 'Diff', 'Data', 'Call', 'File', 'Key', 'KeyEntry'}
```

Note that a heterogeneous graph stores a lot of information in many different forms. For instance, each vertex/edge/arrow class can have its own attributes (for example, each 'File' vertex has a 'name' and a 'path' attribute) and these changes for each class. Use `help(cls)` to discover the available attributes and function for a given class in a Python script.

## Croutons

**Croutons** is a system to extract small refined parts of BAGUETTEs. It uses **metagraphs**, which are **pattern graphs** for heterogeneous graphs, to search through datasets of BAGUETTEs for particular behaviors.

Metagraphs are stored in the metalib, and they can be created and manipulated using the interactive metalib prompt. For example, here is how to create your first metagraph which represent the action of writing high-entropy data into a file:
```
$ metalib
MetaLib interactive console.
Use save(MG, name) and load(name) to save and load MetaGraphs.
Use entries() to get a list of all MetaGraphs available in the library.
Use remove(name) to delete a MetaGraph from the library.
All useful types are loaded, including Graph and MetaGraph related types, as well as Evaluators.
>>> entries()   # metalib is empty for now
[]

>>> MG = MetaGraph()    # Empty metagraph
>>> MG.file = MetaVertex[filesystem.File]   # First vertex
>>> MG.diff = MetaVertex[data.Diff]         # Second vertex
>>> MG.writes = MetaEdge(MG.file, MG.diff)[data.IsDiffOf]   # Edge between them
>>> MG.diff.condition = Evaluator("x.written_entropy >= 6") # Condition on one vertex. Must be a string with "x" treated as a single parameter of a lambda expression

>>> save(MG, "HE-writing")  # Save metagraph
>>> entries()
['HE-writing']
```

Once you have defined the metagraphs you can use `toast` to search for those MetaGraph patterns in BAGUETTE graphs which will add one file to the BAGUETTE packaging ("extracted.pyt"):

```
$ toast --help
usage: toast [-h] [--extracted [EXTRACTED ...]] [--pool POOL] [--maxtime MAXTIME] [-p {-,HE-writing} [{-,HE-writing} ...]] [--perf] [-v]
             inputs [inputs ...]

Toasts Baguettes picking up interesting slices as defined with MetaGraphs patterns.
[...]

$ toast sample.bag
All 1 are well-toasted!

$ ls sample.bag
baguette.pyt
extracted.pyt
index.pyt
visual.gexf
```

You can then analyze the extracted matches by opening the "extracted.pyt" file using pickle:

```
>>> from pickle import load

>>> with open("sample.bag/extracted.pyt", "rb") as f:
...     matches = load(f)

>>> matches
{'HE-writing': [<baguette.bakery.source.graph.Graph object at 0x0000015F2D00DE80>, <baguette.bakery.source.graph.Graph object at 0x0000015F2D4AF900>, <baguette.bakery.source.graph.Graph object at 0x0000015F2D4AFF80>]}

>>> g = matches["HE-writing"][0]        # First matching subgraph found

>>> g.vertices
{Diff(read = b'-\xc2\x94[...]\xaeu', glob_type = ['data'], read_total = 1526, read_space = 1526, written_total = 1511, written_space = 1511, glob_space = 1526, read_entropy = 6.185727716928551, written_entropy = 6.228092608679166, glob_entropy = 6.2308720778528395, printable_rate = 0.3564875491480996, encoding = raw), File()}
```

Finally, you can always use the BAGUETTE classes to expand the functionnalities of BAGUETTE. For that, you can clone the repository at https://gitlab.inria.fr/vraulin/baguette-verse. Classes, modules and packages are documented, so if you want to dig deeper, use Python's `help` function to explore the core functionnalities of BAGUETTE.