"""
This is a *magic* script to bake baguettes. Use -h/--help for usage.
"""





def main():
    """
    Command line function to bake Cuckoo report(s). Use -h/--help for more info.
    """

    if __name__ in ("__main__", "bake"):        # One for when started with Python, the other for when started with package command...

        import logging
        from baguette.bakery.logger import logger, set_level
        set_level(logging.ERROR)

        import argparse
        from os import environ
        import pathlib
        from typing import Literal, Iterator
        from baguette.bakery.compiler import compile
        from baguette.bakery.source import filters
        from baguette.bakery.source.colors import Color
        from baguette.rack import BaguetteRack, TimeoutExit

        parser = argparse.ArgumentParser(
            description = 'Bakes Cuckoo reports into baguettes (gexf and pyt graphs).',
            add_help = True,
            conflict_handler = 'resolve',
            epilog = """
            Note that the format of input and outputs is quite flexible. Indeed you can :
            give output folders for each output file, which will make all input have their output in these folders
            - give a set of outputs for each input file, as long as they are given in the same place in the parameter sequences
            - do the same with input folders and output folders, as long as they also come in the same order
            - mix these options, again, as long as it has a meaning in the order they come.
            - Note that if a given path does not exists, it is interpreted as a folder.
            - Also, if an input path has the appropriate extension, it will be considered as a single input.
            """
            )

        class PathSorter:

            def __init__(self, pool : list[pathlib.Path | Literal["-"]], name : str) -> None:
                self.pool = pool
                self.name = name
            
            def __call__(self, arg : str):
                if arg == "-":
                    self.pool.append(arg)
                    return
                from glob import iglob
                import re
                magic_check = re.compile('([*?[])')
                try:
                    if magic_check.search(arg) is not None:
                        self.pool.extend(pathlib.Path(path) for path in iglob(arg))
                    else:
                        self.pool.append(pathlib.Path(arg))
                except:
                    parser.error("invalid {} path : '{}'".format(self.name, arg))

        reports : list[pathlib.Path | Literal["-"]] = []
        baguettes : list[pathlib.Path | Literal["-"]] = []
        visuals : list[pathlib.Path | Literal["-"]] = []
        outputs : list[pathlib.Path | Literal["-"]] = []

        def pool_size(arg : str) -> int:
            """
            Transforms a numeric argument in a number of process to use as a process pool.
            It can be absolute, negative (relative to the number of CPUs) or 
            """
            from os import cpu_count
            N = cpu_count()
            if not N:
                N = 1
            try:
                v = int(arg)
                if v < 0:
                    v = N - v
                if v <= 0:
                    parser.error("got a (too) negative value for process pool size : '{}'".format(arg))
            except:
                try:
                    v = float(arg)
                    if v <= 0:
                        parser.error("got a negative relative process pool size : '{}'".format(arg))
                    v = round(v * N)
                except:
                    parser.error("not a process pool size : '{}'".format(arg))
            return v

        def time(arg : str) -> float:
            from math import isnan
            try:
                v = float(arg)
                if v <= 0 or isnan(v):
                    parser.error("got a negative, null or nan maxtime")
                return v
            except:
                parser.error("expected positive float for maxtime, got : '{}'".format(arg))

        def paint_color(c : str) -> Color:
            if c in dir(Color):
                color = getattr(Color, c)
                if not isinstance(color, Color):
                    parser.error(f"not a valid color name : '{c}'")
                return color
            else:
                # We can match colors in ALLL LANGUAGES!!!!
                import re
                color_re = r"([\d\.eE-]+|\d+|0[xX][\daAbBcCdDeEfF]+)"
                sep_re = r"(?:[ ,;:\|\&]+)"
                inner_expr = r"(?:" + color_re + sep_re + color_re + sep_re + color_re + r")"
                fmatch = re.compile(inner_expr).fullmatch(c) or re.compile(r"\(" + inner_expr + r"\)").fullmatch(c) or re.compile(r"\[" + inner_expr + r"\]").fullmatch(c) or re.compile(r"\{" + inner_expr + r"\}").fullmatch(c)
                if not fmatch:
                    parser.error(f"could not understand color format : '{c}'")
                r, g, b = fmatch.groups()

                def is_float(s : str) -> bool:
                    try:
                        f = float(s)
                        if not 0 <= f <= 1:
                            return False
                        return True
                    except:
                        return False
                
                def is_int(s : str) -> bool:
                    try:
                        i = int(s)
                        if not 0 <= i <= 255:
                            return False
                        return True
                    except:
                        return False
                
                def is_hex(s : str) -> bool:
                    try:
                        i = int(s, base=16)
                        if not 0 <= i <= 255:
                            return False
                        return True
                    except:
                        return False
                    
                if all(is_float(x) for x in (r, g, b)):
                    r, g, b = float(r), float(g), float(b)
                elif all(is_int(x) for x in (r, g, b)):
                    r, g, b = int(r), int(g), int(b)
                elif all(is_hex(x) for x in (r, g, b)):
                    r, g, b = int(r, 16), int(g, 16), int(b, 16)
                else:
                    parser.error(f"could not understand color format : '{c}'")

                return Color(r, g, b)

        parser.add_argument("reports", type=PathSorter(reports, "report"), default=None, nargs="*" if "BAGUETTE_REPORTS" in environ else "+", help="Cuckoo report files (.json) to bake baguettes from. Can also be folders containing reports. Defaults to environment variable 'BAGUETTE_REPORTS' if set.")
        parser.add_argument("--baguettes", type=PathSorter(baguettes, "baguette"), default=None, action="extend", nargs="*", help="the path(s) to the output baguette files (.pyt). Use '-' to leave it to the automatic destination. Defaults to environment variable 'BAGUETTE_BAGUETTES' or '-' if not set.")
        parser.add_argument("--visuals", type=PathSorter(visuals, "visual"), default=None, action="extend", nargs="*", help="the path(s) to the output visual (Gephi) files (.gexf). Use '-' to leave it to the automatic destination. Defaults to environment variable 'BAGUETTE_VISUALS' or '-' if not set.")
        parser.add_argument("-o", "--outputs", type=PathSorter(outputs, "output"), default=None, action="extend", nargs="*", help="the path to the result index folders (which end in .bag). They contain the index file (.pyt) which stores all the information about a given baguette. Use '-' to leave it to the automatic destination. Defaults to environment variable 'BAGUETTE_OUTPUTS' or '.' if not set.")
        parser.add_argument("--pool", type=pool_size, default=pool_size("0.5"), help="the size of the process pool to use to bake in parallel.")
        parser.add_argument("--maxtime", type=time, default=time("inf"), help="the maximum amount of time spent baking a single baguette. No maxtime by default.")
        parser.add_argument("-f", "--filters", type=str, default=[], choices=[name for name in dir(filters) if isinstance(getattr(filters, name), filters.Filter)], nargs="*", help="a list of filters that can be used when exporting the baguette to the visual file (.gexf).")
        parser.add_argument("--perf", action="store_true", default=False, help="if this is enabled, a performance report will be printed at the end of the baking process.")
        parser.add_argument("-v", "--verbosity", action="count", default=0, help="increases the verbosity of the output.")
        parser.add_argument("--skip_data_comparison", action="store_true", default=False, help="if enabled, the computation of the Levenshtein similarity between all Data nodes will be skipped.")
        parser.add_argument("--skip_diff_comparison", action="store_true", default=False, help="same as skip_data_comparison but for Diff nodes.")
        parser.add_argument("--background", type=paint_color, default=Color.black, help="If a color is given for background, the color settings which are close to the background color will be change to be more visible on background. Must be a valid color name or RGB values.")


        args = parser.parse_args()

        # Setting logging level

        levels = {
            0 : logging.ERROR,
            1 : logging.WARNING,
            2 : logging.INFO,
            3 : logging.DEBUG
        }
        verbosity : Literal[0, 1, 2, 3] = min(3, args.verbosity)
        set_level(levels[verbosity])

        logger.info("Arguments parsed. Discovering jobs.")

        # Parsing jobs

        if not reports:
            try:
                reports = [pathlib.Path(environ["BAGUETTE_REPORTS"])]
            except KeyError:
                raise RuntimeError("Environment variable 'BAGUETTE_REPORTS' not found and there is no input...")
            except:
                parser.error("invalid report path in environment variable : '{}'".format(environ["BAGUETTE_REPORTS"]))
        if not baguettes:
            if "BAGUETTE_BAGUETTES" in environ:
                try:
                    baguettes = [pathlib.Path(environ["BAGUETTE_BAGUETTES"])]
                except:
                    parser.error("invalid baguettes path in environment variable : '{}'".format(environ["BAGUETTE_BAGUETTES"]))
            else:
                baguettes = ["-"]
        if not visuals:
            if "BAGUETTE_VISUALS" in environ:
                try:
                    visuals = [pathlib.Path(environ["BAGUETTE_VISUALS"])]
                except:
                    parser.error("invalid visuals path in environment variable : '{}'".format(environ["BAGUETTE_VISUALS"]))
            else:
                visuals = ["-"]
        if not outputs:
            if "BAGUETTE_OUTPUTS" in environ:
                try:
                    outputs = [pathlib.Path(environ["BAGUETTE_OUTPUTS"])]
                except:
                    parser.error("invalid outputs path in environment variable : '{}'".format(environ["BAGUETTE_OUTPUTS"]))
            else:
                outputs = [pathlib.Path(".")]

        class JobQueue:

            """
            These objects hold a series of grouped jobs.
            """

            def __init__(self, groups : list[pathlib.Path | Literal["-"] | list[pathlib.Path]] = []) -> None:
                from copy import deepcopy
                self.__groups : list[pathlib.Path | Literal["-"] | list[pathlib.Path]] = deepcopy(groups)
                self.__last_group : list[pathlib.Path] = []
                self.__active : bool = False
            
            def insert_group(self, group : list[pathlib.Path] | pathlib.Path | Literal["-"]):
                """
                Creates an independant work group with given content, also creating a new active group for later use.
                """
                if self.__active:
                    self.__groups.append(self.__last_group)
                self.__groups.append(group)
                self.__last_group = []
                self.__active = False
            
            def append_to_active_group(self, path : pathlib.Path):
                """
                Appends a file to the current group.
                """
                self.__last_group.append(path)
                self.__active = True
            
            def new_group(self):
                """
                Adds the active group to the queue and creates a new empty active group.
                """
                if self.__active:
                    self.__groups.append(self.__last_group)
                self.__last_group = []
                self.__active = True

            def finalize(self):
                """
                Finalizes the queue, adding the currently active group to the queue if necessary.
                """
                if self.__active and self.__last_group:
                    self.__groups.append(self.__last_group)
            
            def __iter__(self) -> Iterator[pathlib.Path | Literal["-"] | list[pathlib.Path]]:
                """
                Yields all the jobs in the queue.
                """
                yield from self.__groups
            
            def __len__(self) -> int:
                """
                Implements len(self).
                """
                return len(self.__groups)

            def __getitem__(self, index : int) -> pathlib.Path | Literal["-"] | list[pathlib.Path]:
                """
                Implements self[index].
                """
                return self.__groups[index]


        report_groups : JobQueue = JobQueue()
        baguette_groups : JobQueue = JobQueue()
        visual_groups : JobQueue = JobQueue()
        output_groups : JobQueue = JobQueue()

        def determine_type(path : pathlib.Path | Literal["-"], ext : str) -> Literal["folder", "file"]:
            """
            Determines if the given path should be interpreted as a folder or file path.
            If it ends with the given extension and does not exist, it well be considered a file.
            """
            if path == "-":
                return "folder"
            elif ext and path.suffix == ext:
                return "file"
            if path.is_file():
                return "file"
            elif path.is_dir():
                return "folder"
            elif path.exists():
                parser.error("given path exists and is neither a file or folder : '{}'".format(path))
            else:
                return "folder"
        
        def create_name(folder : pathlib.Path) -> pathlib.Path:
            """
            Given a path, this will return a (possibly) modified path that does not exist in the same folder.
            """
            if not folder.exists():
                return folder
            n = 0
            ext = folder.suffix
            if ext:
                sfolder = str(folder)[:-len(ext)]
            else:
                sfolder = str(folder)
            new_folder = pathlib.Path(sfolder + "({})".format(n) + ext)
            while new_folder.exists():
                n += 1
                new_folder = pathlib.Path(sfolder + "({})".format(n) + ext)
            return new_folder
            

        for r in reports:
            if r == "-":
                parser.error("cannot use automatic destination operator for input files.")
            if determine_type(r, ".json") == "folder":
                if r.exists():
                    report_groups.insert_group([p for p in r.iterdir()])
                else:
                    parser.error("input folder/file does not exist : '{}'".format(r))
            else:
                if r.exists():
                    report_groups.append_to_active_group(r)
                else:
                    parser.error("input file does not exist : '{}'".format(r))
        report_groups.finalize()
        
        for b in baguettes:
            if determine_type(b, ".pyt") == "folder":
                baguette_groups.insert_group(b)
            else:
                if b == "-":
                    raise RuntimeError("How?")
                baguette_groups.append_to_active_group(b)
        baguette_groups.finalize()
        if len(baguette_groups) == 1 and len(report_groups) > 1 and (isinstance(baguette_groups[0], pathlib.Path) or baguette_groups[0] == "-"):
            baguette_groups = JobQueue([baguette_groups[0]] * len(report_groups))

        for v in visuals:
            if determine_type(v, ".gexf") == "folder":
                visual_groups.insert_group(v)
            else:
                if v == "-":
                    raise RuntimeError("How?")
                visual_groups.append_to_active_group(v)
        visual_groups.finalize()
        if len(visual_groups) == 1 and len(report_groups) > 1 and (isinstance(visual_groups[0], pathlib.Path) or visual_groups[0] == "-"):
            visual_groups = JobQueue([visual_groups[0]] * len(report_groups))
        
        for o in outputs:
            if determine_type(o, ".bag") == "folder":
                output_groups.insert_group(o)
            else:
                if o == "-":
                    raise RuntimeError("How?")
                output_groups.append_to_active_group(o)
        output_groups.finalize()
        if len(output_groups) == 1 and len(report_groups) > 1 and (isinstance(output_groups[0], pathlib.Path) or output_groups[0] == "-"):
            output_groups = JobQueue([output_groups[0]] * len(report_groups))

        # def printable_format(l) -> str:
        #     return str(l) if not isinstance(l, list) else (str(l) if len(l) < 2 else "[...]")

        # print("Sizes: {}, {}, {}, {}".format(len(report_groups), len(baguette_groups), len(visual_groups), len(output_groups)))
        # print(list(printable_format(r) for r in report_groups))
        # print(list(printable_format(b) for b in baguette_groups))
        # print(list(printable_format(v) for v in visual_groups))
        # print(list(printable_format(o) for o in output_groups))
        # l1 = list(report_groups)
        # l2 = list(baguette_groups) + [None] * (len(report_groups) - len(baguette_groups))
        # l3 = list(visual_groups) + [None] * (len(report_groups) - len(visual_groups))
        # l4 = list(output_groups) + [None] * (len(report_groups) - len(output_groups))
        # for r, b, v, o in zip(l1, l2, l3, l4):
        #     print("Work group:")
        #     print("reports :", printable_format(r))
        #     print("baguettes :", printable_format(b))
        #     print("visuals :", printable_format(v))
        #     print("outputs :", printable_format(o))
        #     print("\n")

        if len(report_groups) != len(baguette_groups) or len(report_groups) != len(visual_groups) or len(report_groups) != len(output_groups):
            parser.error("different number of work groups in inputs/outputs.")
        
        for r, b, v, o in zip(report_groups, baguette_groups, visual_groups, output_groups):
            if not isinstance(r, list):
                raise RuntimeError("How did we get here?")
            n = len(r)
            if isinstance(b, list) and len(b) != n:
                parser.error("got a work group with different numbers of inputs and outputs.")
            if isinstance(v, list) and len(v) != n:
                parser.error("got a work group with different numbers of inputs and outputs.")
            if isinstance(o, list) and len(o) != n:
                parser.error("got a work group with different numbers of inputs and outputs.")

        work : list[BaguetteRack] = []

        def stripname(p : pathlib.Path) -> str:
            """
            Returns the name of the path without the exetension if it has one.
            """
            ext = p.suffix
            if ext:
                return p.name[:-len(ext)]
            return p.name

        for rgroup, bgroup, vgroup, ogroup in zip(report_groups, baguette_groups, visual_groups, output_groups):

            if rgroup == "-":
                parser.error("cannot use automatic destination operator for input files.")
            elif isinstance(rgroup, pathlib.Path):      # Folder input
                rgroup = list(rgroup.iterdir())         # Transform in file inputs

            if ogroup == "-":
                parser.error("cannot use automatic destination operator for output folders.")
            elif isinstance(ogroup, pathlib.Path):      # Folder output
                ogroup = [create_name(pathlib.Path(ogroup, stripname(r) + ".bag")) for r in rgroup]
            
            if bgroup == "-":                           # Magic destination:
                bgroup = [None for _ in rgroup]         # To be determined later
            elif isinstance(bgroup, pathlib.Path):      # Folder baguette destination
                bgroup = [create_name(pathlib.Path(bgroup, stripname(r) + ".pyt")) for r in rgroup]       # Pre-compute the baguette paths with report names

            if vgroup == "-":                           # Magic destination:
                vgroup = [None for _ in rgroup]         # To be determined later
            elif isinstance(vgroup, pathlib.Path):      # Folder visual destination
                vgroup = [create_name(pathlib.Path(vgroup, stripname(r) + ".gexf")) for r in rgroup]       # Pre-compute the visual paths with report names
            
            for r, b, v, o in zip(rgroup, bgroup, vgroup, ogroup):
                bg = BaguetteRack(o)
                bg.report = r
                bg.baguette = b if b is not None else (bg.working_directory / "baguette.pyt")
                bg.visual = v if v is not None else (bg.working_directory / "visual.gexf")
                bg.verbosity = verbosity
                bg.skip_data_comparison = args.skip_data_comparison
                bg.skip_diff_comparison = args.skip_diff_comparison
                bg.filter_names = args.filters
                bg.maxtime = args.maxtime
                bg.perf = args.perf
                bg.background_color = args.background
                work.append(bg)
        
        
        # Compile now...

        from multiprocessing.pool import Pool
        from threading import Lock, Thread

        # All of this is because multiprocessing was coded with feet... Pool's async methods may freeze (deadlock maybe) on some platforms.

        lock = Lock()
        failed, timed_out, total = 0, 0, len(work)
        def execute_single_job(P : Pool) -> bool:
            nonlocal failed, timed_out
            with lock:
                if not work: 
                    return False
                br = work.pop()
            try:
                br = P.apply(compile, (br, ))
            except KeyboardInterrupt as e:
                from traceback import TracebackException
                br.exception = TracebackException.from_exception(e)
            if br.exception is None or not br.suppressed:
                br.export()
            if br.exception is not None and issubclass(br.exception.exc_type, KeyboardInterrupt):
                return False
            elif br.exception is not None and not issubclass(br.exception.exc_type, TimeoutExit):
                with lock:
                    failed += 1
                logger.error("Got a '{}' error during the baking of '{}'.".format(br.exception.exc_type.__name__, br.report.name))
            elif br.exception is not None and issubclass(br.exception.exc_type, TimeoutExit):
                with lock:
                    timed_out += 1
            return True

        def executor(P : Pool):
            while execute_single_job(P):
                pass
        
        threads : list[Thread] = []
        try:
            with Pool(args.pool, maxtasksperchild = 1) as P:
                for _ in range(args.pool):
                    t = Thread(target = executor, args = (P, ), daemon = True)
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join()
            
            success = total - failed - timed_out
            if failed and success and timed_out:
                print("{} failed baguettes, {} took too long and {} well-baked.".format(failed, timed_out, success))
            elif failed and success:
                print("{} failed baguettes, {} baked correctly.".format(failed, success))
            elif timed_out and success:
                print("{} baguettes took too long to bake, {} baked correctly.".format(timed_out, success))
            elif failed and timed_out:
                print("{} baguettes are failed and the {} others took too long to bake...".format(failed, timed_out))
            elif failed:
                print("All {} baguettes did not bake correctly...".format(failed))
            elif timed_out:
                print("All {} baguettes took too long to bake...".format(timed_out))
            elif success:
                print("All {} are well-baked!".format(success))
        except KeyboardInterrupt:
            print("Exiting.")
            




if __name__ == "__main__":
    main()