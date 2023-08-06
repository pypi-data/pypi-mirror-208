"""
This module contains the compile function which is used to bake baguettes.
"""

from ..rack import BaguetteRack

__all__ = ["compile"]





def compile(rack : BaguetteRack) -> BaguetteRack:

    """
    Compiles a baguette using the data written in the given BaguetteRack object.
    Returns a BaguetteRack (the same) containing the results (and exceptions on failure).
    """

    from ..rack import BaguetteRack, TimeoutExit

    try:

        if rack.baked:
            return rack
        
        import logging
        levels = {
            0 : logging.ERROR,
            1 : logging.WARNING,
            2 : logging.INFO,
            3 : logging.DEBUG
        }
        
        from .logger import set_level, logger
        set_level(levels[rack.verbosity])

        logger.debug("Just change worker's verbosity level.")

        import os
        from pickle import dump
        from .source.build import Builder
        from .source.config import CompilationParameters, ajust_for_background_color
        from .source import types
        from Viper.better_threading import Future, DaemonThread

        if rack.perf:
            from .source.utils import chrono
            chrono.enabled = True
            chrono.auto_report = True

        if not os.path.exists(rack.report):
            rack.suppressed = True
            raise FileNotFoundError("Could not find report file: {}".format(rack.report))
        if not os.path.isfile(rack.report):
            rack.suppressed = True
            raise FileExistsError("Given path to report file is not a file.")
        if os.path.exists(rack.baguette) and not os.path.isfile(rack.baguette):
            rack.suppressed = True
            raise FileExistsError("Given baguette output file exists and is not a file.")
        if os.path.exists(rack.visual) and not os.path.isfile(rack.visual):
            rack.suppressed = True
            raise FileExistsError("Given visual output file exists and is not a file.")

        if rack.skip_data_comparison:
            CompilationParameters.SkipLevenshteinForDataNodes = True
        if rack.skip_diff_comparison:
            CompilationParameters.SkipLevenshteinForDiffNodes = True

        result : Future[bool] = Future()

        def compile_main():
            
            try:
                logger.info("Loading file...")
                from json import JSONDecodeError
                try:
                    with rack.report.open("r") as file:
                        b = Builder(file)
                except JSONDecodeError:
                    rack.suppressed = True
                    raise
                logger.info("Checking color settings...")
                ajust_for_background_color(rack.background_color)
                logger.info("Building graph...")
                b.build()
                G = b.graph
                logger.info("Analyzing graph...")
                logger.info("Got {} vertices and {} edges.".format(G.n, G.m))
                logger.info("Saving with pickle")
                rack.baguette.parent.mkdir(parents = True, exist_ok = True)
                with rack.baguette.open("wb") as file:
                    dump(G, file)
                filters = rack.filters
                if filters:
                    for i, (f, name) in enumerate(zip(filters, rack.filter_names)):
                        logger.info("Applying filters {}/{} : {}".format(i + 1, len(filters), name))
                        f.apply(G)
                logger.info("Exporting to .gexf")
                rack.visual.parent.mkdir(parents = True, exist_ok = True)
                G.export(str(rack.visual))
                result.set(True)
                logger.info("Done !")
            except BaseException as e:
                result.set_exception(e)

        def death_timer():
            from time import sleep
            from Viper.format import duration
            if rack.maxtime < float("inf"):
                logger.info("Death timer thread started. {} remaining.".format(duration(rack.maxtime)))
                sleep(rack.maxtime)
                logger.error("Death timer reached, about to exit.")
                result.set_exception(TimeoutExit("Baking maxtime reached"))
            else:
                while True:
                    sleep(600)
        
        t1 = DaemonThread(target = compile_main)
        t2 = DaemonThread(target = death_timer)
        t1.start()
        t2.start()
        
        while not result.wait(0.1):
            pass
        result.result()
    
    except BaseException as e:
        from traceback import print_exc, TracebackException
        rack.exception = TracebackException.from_exception(e)
        if not isinstance(e, (KeyboardInterrupt, TimeoutExit)):
            print_exc()
    finally:
        if rack.exception is None or not issubclass(rack.exception.exc_type, (KeyboardInterrupt, TimeoutExit)):
            rack.baked = True
        return rack





del BaguetteRack