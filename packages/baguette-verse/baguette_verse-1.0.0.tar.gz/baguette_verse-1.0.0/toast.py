"""
This is a *magic* script to toast baguettes. Use -h/--help for usage.
"""





def main():
    """
    Command line function to toast baguettes. Use -h/--help for more info.
    """

    if __name__ in ("__main__", "toast"):        # One for when started with Python, the other for when started with package command...

        import logging
        from baguette.bakery.logger import logger, set_level
        set_level(logging.ERROR)

        import argparse
        from os import environ
        import pathlib
        from typing import Literal, Iterator
        from baguette.bakery.source.colors import Color
        from baguette.croutons.extractor import extract
        from baguette.croutons.metalib.utils import entries
        from baguette.rack import BaguetteRack, TimeoutExit

        parser = argparse.ArgumentParser(
            description = 'Toasts Baguettes, picking up interesting slices as defined by MetaGraphs patterns.',
            add_help = True,
            conflict_handler = 'resolve',
            epilog = """
            Note that the format of input and outputs is quite flexible. Indeed you can :
            give output folders for each output file, which will make all input have their output in these folders
            - give a set of outputs for each input file, as long as they are given in the same place in the parameter sequences
            - do the same with input folders and output folders, as long as they also come in the same order
            - mix these options, again, as long as it has a meaning in the order they come.
            - Note that if a given path does not exists, it is interpreted as a folder, unless the name ends with the appropriate file extension.
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

        inputs : list[pathlib.Path | Literal["-"]] = []
        extracted : list[pathlib.Path | Literal["-"]] = []

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

        parser.add_argument("inputs", type=PathSorter(inputs, "input"), default=None, nargs="*" if ("BAGUETTE_INPUTS" in environ or "BAGUETTE_OUTPUTS" in environ) else "+", help="Baguette folders. These should contain the index file resulting from the baking. Can also be folders baguette folders. Defaults to environment variable 'BAGUETTE_INPUTS' (or 'BAGUETTE_OUTPUTS') if set.")
        parser.add_argument("--extracted", type=PathSorter(extracted, "extracted"), default=None, action="extend", nargs="*", help="the path(s) to the output extracted match files (.pyt). Use '-' to leave it to the automatic destination. Defaults to environment variable 'BAGUETTE_EXTRACTED' or '-' if not set.")
        parser.add_argument("--pool", type=pool_size, default=pool_size("0.5"), help="the size of the process pool to use to bake in parallel.")
        parser.add_argument("--maxtime", type=time, default=time("inf"), help="the maximum amount of time spent baking a single baguette. No maxtime by default.")
        parser.add_argument("-p", "--pattern", type=str, action="extend", choices=["-"] + entries(), nargs="+", help="The metapath names (as in the source.metalib module) to search for. Leave empty or use '-' to search for all defined metagraphs.")
        parser.add_argument("--perf", action="store_true", default=False, help="if this is enabled, a performance report will be printed at the end of the baking process.")
        parser.add_argument("--paint", type=paint_color, nargs="+", default=[], help="If a color is given for painting, the matches found will be painted in the visual.gexf file. Must be a valid color name or RGB values.")
        parser.add_argument("-v", "--verbosity", action="count", default=0, help="increases the verbosity of the output.")

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

        if not inputs:
            try:
                inputs = [pathlib.Path(environ["BAGUETTE_INPUTS"])]
            except KeyError:
                try:
                    inputs = [pathlib.Path(environ["BAGUETTE_OUTPUTS"])]
                except KeyError:
                    raise RuntimeError("Environment variable 'BAGUETTE_INPUTS' not found and there is no input...")
            except:
                parser.error("invalid baguette input path in environment variable : '{}'".format(environ["BAGUETTE_INPUTS"] if "BAGUETTE_INPUTS" in environ else environ["BAGUETTE_OUTPUTS"]))
        if not extracted:
            if "BAGUETTE_EXTRACTED" in environ:
                try:
                    extracted = [pathlib.Path(environ["BAGUETTE_EXTRACTED"])]
                except:
                    parser.error("invalid extraction path in environment variable : '{}'".format(environ["BAGUETTE_EXTRACTED"]))
            else:
                extracted = ["-"]
        
        if not args.pattern:
            args.pattern = entries()
        if "-" in args.pattern and len(args.pattern) > 1:
            parser.error("if '-' is given for pattern, it should be the only.")
        if "-" in args.pattern:
            args.pattern = entries()

        if args.paint:
            if len(args.paint) == 1:
                args.paint *= len(args.pattern)
            if len(args.paint) != len(args.pattern):
                parser.error("expected one color or as many colors as patterns to match.")
        
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


        input_groups : JobQueue = JobQueue()
        extracted_groups : JobQueue = JobQueue()

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
            

        for i in inputs:
            if i == "-":
                parser.error("cannot use automatic destination operator for input baguette folders.")
            if determine_type(i, ".bag") == "folder":
                if i.exists():
                    input_groups.insert_group([p for p in i.iterdir()])
                else:
                    parser.error("input folder does not exist : '{}'".format(i))
            else:
                if i.exists():
                    input_groups.append_to_active_group(i)
                else:
                    parser.error("input baguette folder does not exist : '{}'".format(i))
        input_groups.finalize()
        
        for e in extracted:
            if determine_type(e, ".pyt") == "folder":
                extracted_groups.insert_group(e)
            else:
                if e == "-":
                    raise RuntimeError("How?")
                extracted_groups.append_to_active_group(e)
        extracted_groups.finalize()
        if len(extracted_groups) == 1 and len(input_groups) > 1 and (isinstance(extracted_groups[0], pathlib.Path) or extracted_groups[0] == "-"):
            extracted_groups = JobQueue([extracted_groups[0]] * len(input_groups))

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

        if len(input_groups) != len(extracted_groups):
            parser.error("different number of work groups in inputs/outputs.")
        
        for i, e in zip(input_groups, extracted_groups):
            if not isinstance(i, list):
                raise RuntimeError("How did we get here?")
            n = len(i)
            if isinstance(e, list) and len(e) != n:
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

        for igroup, egroup in zip(input_groups, extracted_groups):

            if igroup == "-":
                parser.error("cannot use automatic destination operator for input files.")
            elif isinstance(igroup, pathlib.Path):      # Folder input
                igroup = list(igroup.iterdir())         # Transform in file inputs
            
            if egroup == "-":                           # Magic destination:
                egroup = [None for _ in igroup]         # To be determined later
            elif isinstance(egroup, pathlib.Path):      # Folder baguette destination
                egroup = [create_name(pathlib.Path(egroup, stripname(r) + ".pyt")) for r in igroup]       # Pre-compute the baguette paths with report names
            
            for i, e in zip(igroup, egroup):
                if not (i / "index.pyt").exists():
                    parser.error("baguette folder does not have the appropriate index file : '{}' not found.".format(i / "index.pyt"))
                if not (i / "index.pyt").is_file():
                    parser.error("baguette folder does not have the appropriate index file : '{}' is not a file.".format(i / "index.pyt"))
                bg = BaguetteRack.import_from(i / "index.pyt")
                bg.extracted = e if e is not None else bg.working_directory / "extracted.pyt"
                bg.pattern_names = args.pattern
                bg.maxtime = args.maxtime
                bg.perf = args.perf
                bg.paint_color = args.paint
                work.append(bg)
        
        
        # Extract now...

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
                br = P.apply(extract, (br, ))
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
                logger.error("Got a '{}' error during the toasting of '{}'.".format(br.exception.exc_type.__name__, br.working_directory.name))
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
                print("{} failed toasts, {} took too long and {} well-toasted.".format(failed, timed_out, success))
            elif failed and success:
                print("{} failed toasts, {} toasted correctly.".format(failed, success))
            elif timed_out and success:
                print("{} baguettes took too long to toast, {} toasted correctly.".format(timed_out, success))
            elif failed and timed_out:
                print("{} toasts are failed and the {} others took too long to toast...".format(failed, timed_out))
            elif failed:
                print("All {} baguettes did not toast correctly...".format(failed))
            elif timed_out:
                print("All {} baguettes took too long to toast...".format(timed_out))
            elif success:
                print("All {} are well-toasted!".format(success))
        except KeyboardInterrupt:
            print("Exiting.")
            




if __name__ == "__main__":
    main()