"""
This module contains utilities to manage BAGUETTE data.
"""

from pathlib import Path
from traceback import TracebackException
from typing import Any, Literal, TypeVar

from .croutons.source.metagraph import MetaGraph
from .bakery.source.filters import Filter
from .bakery.source.colors import Color

__all__ = ["BaguetteRack", "TimeoutExit"]





class TimeoutExit(SystemExit):
    """
    This exception means that a critical timeout has been reached, causing interpreter exit when raised.
    """

T = TypeVar("T", bound="BaguetteRack")

class BaguetteRack:

    """
    Baguette racks are just a utility to organize baguettes easily.
    Remember to export() them before deleting them, as this will write the index file.
    """

    __slots__ = {
        "__working_directory" : "The absolute path to the working directory",
        "__index" : "The path to the index file. Can be relative to __working_directory",
        "__report" : "The path to the Cuckoo report file. Can be relative to __working_directory",
        "__baguette" : "The path to the baguette file. Can be relative to __working_directory",
        "__visual" : "The path to the Gephi file. Can be relative to __working_directory",
        "__extracted" : "The path to the results of the metagraph search. Can be relative to __working_directory",
        "__perf" : "A boolean indicating if a performance report should be returned",
        "__filters" : "The list if filters applied during the compilation phase",
        "__patterns" : "The list of MetaGraphs to search for during the extraction phase",
        "__skip_data_comparison" : "A boolean indicating if Data nodes were compared during compilation",
        "__skip_diff_comparison" : "A boolean indicating if Diff nodes were compared during compilation",
        "__exception" : "The last caught exception",
        "__baked" : "Indicates if the baguette has been successfully baked",
        "__toasted" : "Indicates if the baguette has been successfully toasted",
        "__verbosity" : "The verbosity level to apply when baking or toasting", 
        "__maxtime" : "The maximum amount of time to spend on this baguette",
        "__paint_color" : "The color to use to paint MetaGraph matches in the visual file",
        "__suppressed" : "Indicates if an exception should suppress the index file output",
        "__background_color" : "The color of the background for the visual graph"
    }

    names = {
        "working_directory" : "BAGUETTE Directory",
        "index" : "BAGUETTE Index File",
        "report" : "Cuckoo Report File",
        "baguette" : "Python BAGUETTE File",
        "visual" : "Gephi File",
        "extracted" : "Extracted MetaGraphs Python File",
    }

    def __init__(self, working_directory : str | Path | None = None) -> None:
        from pathlib import Path
        from traceback import TracebackException
        from typing import Literal
        from .bakery.source.colors import Color
        self.__working_directory : Path | None = None
        self.__index : Path | None = None
        self.__report : Path | None = None
        self.__baguette : Path | None = None
        self.__visual : Path | None = None
        self.__extracted : Path | None = None
        self.__perf : bool = False
        self.__filters : list[str] = []
        self.__patterns : list[str] = []
        self.__skip_data_comparison : bool = False
        self.__skip_diff_comparison : bool = False
        self.__exception : TracebackException | None = None
        self.__baked : bool = False
        self.__toasted : bool = False
        self.__verbosity : Literal[0, 1, 2, 3] = 0
        self.__maxtime : float = float("inf")
        self.__paint_color : list[Color] | None = None
        if working_directory is not None and not isinstance(working_directory, str | Path):
            raise TypeError("Expected Path, got " + repr(type(working_directory).__name__))
        if working_directory is not None:
            self.set_defaults(Path(working_directory))
        
    def set_defaults(self, working_directory : Path):
        """
        Sets the default values for parameters given the new working directory.
        """
        working_directory = working_directory.expanduser().resolve()
        self.__working_directory = working_directory
        self.__index = working_directory / "index.pyt"
        self.__baguette = working_directory / "baguette.pyt"
        self.__visual = working_directory / "visual.gexf"
        self.__extracted = working_directory / "extracted.pyt"
        self.check()

    @property
    def suppressed(self) -> bool:
        """
        Indicates if a raised exception should suppress the output file writing.
        """
        return self.__suppressed

    @suppressed.setter
    def suppressed(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got '{type(value).__name__}'")
        self.__suppressed = value

    @property
    def paint_color(self) -> list[Color] | None:
        """
        The Colors in which to paint the MetaGraph matches found during toasting.
        The index of the color correspond to the index of the MetaGraph in the "patterns" attribute.
        None indicates no painting.
        """
        return self.__paint_color
    
    @paint_color.setter
    def paint_color(self, value : list[Color] | None):
        from .bakery.source.colors import Color
        if value is not None and not isinstance(value, list):
            raise TypeError("Expected None or list of Colors, got " + repr(type(value).__name__))
        if isinstance(value, list):
            for c in value:
                if not isinstance(c, Color):
                    raise TypeError("Expected list of Colors, got a " + repr(type(c).__name__))
        self.__paint_color = value

    @property
    def background_color(self) -> Color:
        """
        The background color that will be used for the visual file.
        This is used to change the color settings which are too close from the background color in order to make the visual sharper.
        """
        return self.__background_color
    
    @background_color.setter
    def background_color(self, value : Color):
        from .bakery.source.colors import Color
        if not isinstance(value, Color):
            raise TypeError(f"Expected Color, got '{type(value).__name__}'")
        self.__background_color = value

    @property
    def maxtime(self) -> float:
        """
        The maximum amount of time (in seconds) to spend on the baking or toasting process of this baguette.
        Defaults to infinity.
        """
        return self.__maxtime

    @maxtime.setter
    def maxtime(self, value : float):
        from math import isnan
        if not isinstance(value, float):
            raise TypeError("Expected float, got " + repr(type(value).__name__))
        if value <= 0 or isnan(value):
            raise ValueError("Expected positive value for timeout, got {}".format(value))
        self.__maxtime = value

    @property
    def verbosity(self) -> Literal[0, 1, 2, 3]:
        """
        The verbosity level that should be applied when baking or toasting this baguette.
        0 : Errors only (default)
        1 : Warnings
        2 : Info
        3 : Debug
        """
        return self.__verbosity

    @verbosity.setter
    def verbosity(self, value : Literal[0, 1, 2, 3]):
        if not isinstance(value, int):
            raise TypeError("Expected int, got " + repr(type(value).__name__))
        if value not in {0, 1, 2, 3}:
            raise ValueError("Verbosity should be in range(4), got {}".format(value))
        self.__verbosity = value

    @property
    def baked(self) -> bool:
        """
        Indicates if the baguette has been successfully baked.
        """
        return self.__baked
    
    @baked.setter
    def baked(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__baked = value
    
    @property
    def toasted(self) -> bool:
        """
        Indicates if the baguette has been successfully toasted.
        """
        return self.__toasted
    
    @toasted.setter
    def toasted(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__toasted = value
    
    @property
    def exception(self) -> TracebackException | None:
        """
        The last caught exception in the baking or toasting process if any.
        """
        return self.__exception
    
    @exception.setter
    def exception(self, value : TracebackException | None):
        from traceback import TracebackException
        if value is not None and not isinstance(value, TracebackException):
            raise TypeError("Expected TracebackException or None, got " + repr(type(value).__name__))
        self.__exception = value
        
    @property
    def perf(self) -> bool:
        """
        Indicates if the current baguette should be baked or toasted with a performance report.
        """
        return self.__perf
    
    @perf.setter
    def perf(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__perf = value

    @property
    def patterns(self) -> list[MetaGraph]:
        """
        The MetaGraph patterns to search for during the baking of this baguette.
        """
        from .croutons import metalib
        from .croutons.source.metagraph import MetaGraph
        l = []
        for name in self.__patterns:
            p = getattr(metalib, name)
            if isinstance(p, MetaGraph):
                l.append(p)
        return l
    
    def add_pattern(self, name : str):
        """
        Adds a MetaGraph pattern from its name in the metalib.
        """
        if not isinstance(name, str):
            raise TypeError("Expected str, got " + repr(type(name).__name__))
        from .croutons import metalib
        if name not in dir(metalib):
            raise NameError("No MetaGraph named '{}'".format(name))
        self.__patterns.append(name)

    def clear_patterns(self):
        """
        Clears the MetaGraph patterns set for this baguette.
        """
        self.__patterns.clear()
    
    @property
    def pattern_names(self) -> list[str]:
        """
        The list of MetaGraphs applied to this baguette as named in the metalib.
        """
        return self.__patterns.copy()

    @pattern_names.setter
    def pattern_names(self, value : list[str]):
        if not isinstance(value, list):
            raise TypeError("Expected list, got " + repr(type(value).__name__))
        for name in value:
            if not isinstance(name, str):
                raise TypeError("Expected list of str, got a " + repr(type(name).__name__))
            
        old, self.__patterns = self.__patterns, []
        try:
            for name in value:
                self.add_pattern(name)
        except:
            self.__patterns = old
            raise

    @property
    def filters(self) -> list[Filter]:
        """
        The filters to apply/applied during the baking of this baguette.
        """
        from .bakery.source import filters
        l = []
        for name in self.__filters:
            f = getattr(filters, name)
            if isinstance(f, filters.Filter):
                l.append(f)
        return l

    def add_filter(self, name : str):
        """
        Adds a baguette filter from its name in the filters module.
        """
        if not isinstance(name, str):
            raise TypeError("Expected str, got " + repr(type(name).__name__))
        from .bakery.source import filters
        if name not in dir(filters):
            raise NameError("No Filter named '{}'".format(name))
        self.__filters.append(name)
    
    def clear_filters(self):
        """
        Clears the filters set for this baguette.
        """
        self.__filters.clear()
    
    @property
    def filter_names(self) -> list[str]:
        """
        The list of Filters applied to this baguette as named in the module filters.
        """
        return self.__filters.copy()

    @filter_names.setter
    def filter_names(self, value : list[str]):
        if not isinstance(value, list):
            raise TypeError("Expected list, got " + repr(type(value).__name__))
        for name in value:
            if not isinstance(name, str):
                raise TypeError("Expected list of str, got a " + repr(type(name).__name__))
            
        old, self.__filters = self.__filters, []
        try:
            for name in value:
                self.add_filter(name)
        except:
            self.__filters = old
            raise

    @property
    def skip_data_comparison(self) -> bool:
        """
        Indicates if Data nodes should be compared during the baking process.
        Useful for performance increase, but some information may be missing.
        """
        return self.__skip_data_comparison
    
    @skip_data_comparison.setter
    def skip_data_comparison(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__skip_data_comparison = value

    @property
    def skip_diff_comparison(self) -> bool:
        """
        Indicates if Diff nodes should be compared during the baking process.
        Useful for performance increase, but some information may be missing.
        """
        return self.__skip_diff_comparison
    
    @skip_diff_comparison.setter
    def skip_diff_comparison(self, value : bool):
        if not isinstance(value, bool):
            raise TypeError("Expected bool, got " + repr(type(value).__name__))
        self.__skip_diff_comparison = value
    
    def check(self, index : Path | None = None, working_directory : Path | None = None, report : Path | None = None, baguette : Path | None = None, visual : Path | None = None, extracted : Path | None = None):
        """
        Checks if the current baguette is well configured.
        Raises the appropriate exception if it is not.
        """
        working_directory = self.working_directory if working_directory is None else working_directory

        index = self.index if index is None else index
        report = self.report if report is None else report
        baguette = self.baguette if baguette is None else baguette
        visual = self.visual if visual is None else visual
        extracted = self.extracted if extracted is None else extracted

        index = index if index.is_absolute() else working_directory / index
        report = report if report.is_absolute() else working_directory / report
        baguette = baguette if baguette.is_absolute() else working_directory / baguette
        visual = visual if visual.is_absolute() else working_directory / visual
        extracted = extracted if extracted.is_absolute() else working_directory / extracted

        if working_directory.exists() and not working_directory.is_dir():
            raise FileExistsError("The given working directory already exists and is not a directory.")
        if index.exists() and not index.is_file():
            raise FileExistsError("The given index file path exists and is not a file.")
        if index.parent != working_directory:
            raise ValueError("The index file must be located directly in the working directory.")
    
    @property
    def working_directory(self) -> Path:
        """
        The path that contains the index file and all other baguette files by default.
        """
        if not self.__working_directory:
            raise RuntimeError("Working directory path has not been set yet.")
        return self.__working_directory

    @working_directory.setter
    def working_directory(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        old = self.__working_directory
        index, report, baguette, visual, extracted = None, None, None, None, None
        if old:
            if self.__index and self.__index.is_relative_to(old):
                index = value / self.__index.relative_to(old)
            if self.__report and self.__report.is_relative_to(old):
                report = value / self.__report.relative_to(old)
            if self.__baguette and self.__baguette.is_relative_to(old):
                baguette = value / self.__baguette.relative_to(old)
            if self.__visual and self.__visual.is_relative_to(old):
                visual = value / self.__visual.relative_to(old)
            if self.__extracted and self.__extracted.is_relative_to(old):
                extracted = value / self.__extracted.relative_to(old)
        self.check(working_directory = value, index = index, report = report, baguette = baguette, visual = visual, extracted = extracted)
        if old and old.is_dir():
            from os import renames
            renames(old, value)
        self.__working_directory = value
        if index:
            self.index = index
        if report:
            self.report = report
        if baguette:
            self.baguette = baguette
        if visual:
            self.visual = visual
        if extracted:
            self.extracted = extracted

    @property
    def index(self) -> Path:
        """
        The path to the index file which stores the paths to all parts of the baguette.
        """
        if not self.__index:
            return self.working_directory / "index.json"
        return self.__index
    
    @index.setter
    def index(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        if not self.__working_directory:
            self.working_directory = value.parent
        self.check(index = value)
        if self.__index and self.__index.is_file():
            from os import renames
            renames(self.__index, value)
        self.__index = value
    
    @property
    def report(self) -> Path:
        """
        The path to the Cuckoo report of this baguette (.json).
        """
        if self.__report is None:
            self.__report = self.working_directory / "report.json"
        return self.__report

    @report.setter
    def report(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        self.check(report = value)
        if self.__report and self.__report.is_file():
            from os import renames
            renames(self.__report, value)
        self.__report = value

    @property
    def baguette(self) -> Path:
        """
        The path to the baguette file itself (the pickle of the baguette graph) (.pyt).
        """
        if self.__baguette is None:
            self.__baguette = self.working_directory / "baguette.pyt"
        return self.__baguette

    @baguette.setter
    def baguette(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        self.check(baguette = value)
        if self.__baguette and self.__baguette.is_file():
            from os import renames
            renames(self.__baguette, value)
        self.__baguette = value

    @property
    def visual(self) -> Path:
        """
        The path to the visual representation file of the baguette (.gexf).
        """
        if self.__visual is None:
            self.__visual = self.working_directory / "visual.gexf"
        return self.__visual

    @visual.setter
    def visual(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        self.check(visual = value)
        if self.__visual and self.__visual.is_file():
            from os import renames
            renames(self.__visual, value)
        self.__visual = value
    
    @property
    def extracted(self) -> Path:
        """
        The path to the metagraph search results file for this baguette (.pyt).
        """
        if self.__extracted is None:
            self.__extracted = self.working_directory / "extracted.pyt"
        return self.__extracted

    @extracted.setter
    def extracted(self, value : str | Path):
        from pathlib import Path
        if not isinstance(value, str | Path):
            raise TypeError("Expected Path, got " + repr(type(value).__name__))
        if isinstance(value, str):
            try:
                value = Path(value)
            except BaseException as e:
                raise e from None
        value = value.expanduser().resolve().absolute()
        self.check(extracted = value)
        if self.__extracted and self.__extracted.is_file():
            from os import renames
            renames(self.__extracted, value)
        self.__extracted = value
    
    def export(self):
        """
        Writes the information of this baguette to the index file.
        Does nothing if the path to the index file has not been set yet.
        """
        from pickle import dump
        if not self.__working_directory:
            return
        self.index.parent.mkdir(parents = True, exist_ok = True)
        with open(self.index, "wb") as f:
            dump(self, f)
    
    @classmethod
    def import_from(cls : type[T], path : str | Path) -> T:
        """
        Loads the information on a baguette from the given index path.
        """
        from pathlib import Path
        from pickle import load
        if not isinstance(path, str | Path):
            raise TypeError("Expected Path, got " + repr(type(path).__name__))
        if isinstance(path, str):
            try:
                path = Path(path)
            except BaseException as e:
                raise e from None
        path = path.expanduser().resolve()
        with path.open("rb") as f:
            return load(f)
    




del Path, T, TypeVar, Any, TracebackException