#!/usr/bin/env  python3

import atexit
import logging
import sys
import time
from collections import Counter
from importlib.metadata import version
from typing import List

from libsrg.LevelBanner import LevelBanner
from libsrg.LoggingUtils import level2str, libsrg_version

log = logging.getLogger("libsrg.LoggingCounter")


class LoggingCounter(logging.Handler):
    """LoggingCounter is a subclass of logging.Handler that counts the number of logs performed at each logging.Level
    self.count_at_level_name is a dictionary indexed by logging.Level, in which counts are maintained
    self.frozen is a flag which freezes counts while logging counts

    This is a singleton and the constructor should not be explicitly called from outside of the class methods.

    """

    __instance: "LoggingCounter" = None

    def __init__(self, *args, **kwargs):
        super(LoggingCounter, self).__init__(*args, **kwargs)
        if self.__instance is not None:
            log.critical("Constructor called on existing singleton")
            raise Exception("LoggingCounter is designed as a singleton")

        # index is name of level, not numeric value
        self.count_at_level_name = Counter()
        self.frozen = False
        self.start_time = time.time()
        self.stop_time = None
        self.elapsed_time = None

    def emit(self, record):
        if not self.frozen:
            lev = record.levelname
            # if lev not in self.count_at_level_name:
            #     self.count_at_level_name[lev] = 0
            self.count_at_level_name[lev] += 1

    def count_for_level(self, lev) -> int:
        """lev can be passed as string or numeric level, but index is based on string """
        lev_str: str = level2str(lev)
        return self.count_at_level_name[lev_str]

    def __log_atexit(self, logger: logging.Logger = None, log_level=logging.INFO):
        if logger is None:
            logger = log
        self.frozen = True
        self.stop_time = time.time()
        self.elapsed_time = self.stop_time - self.start_time
        ver = version('libsrg')
        olist: List[str] = [f"\n\n{sys.argv[0]} Using libsrg {ver} from {libsrg_version()}", "Logging Summary:"]
        lasttag = None
        for tag in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            if tag in self.count_at_level_name:
                count = self.count_at_level_name[tag]
                olist.append(f"Logging at Level {tag:10s} occurred {count:10d} times")
                if count:
                    lasttag = tag
        if lasttag:
            banner = LevelBanner.find(lasttag, logging.WARNING)
            olist.append(banner)
        olist.append(f"Elapsed time was {self.elapsed_time:.3f} seconds")
        logger.log(log_level, "\n".join(olist))
        self.frozen = False

    @classmethod
    def config_and_attach(cls, stream_also=True, **kwargs) -> "LoggingCounter":
        """Performs logging.basicConfig and attaches counter
        see https://docs.python.org/3/library/logging.html#logging.basicConfig
        """
        already_exists = cls.__instance is not None
        # format0 = '%(asctime)s %(levelname)s %(message)s'
        if 'format' not in kwargs:
            # see https://docs.python.org/3/library/logging.html#logging.LogRecord
            kwargs['format'] = "%(asctime)s %(levelname)-8s %(lineno)4d %(name) 20s.%(funcName)-22s -- %(message)s"
        if 'level' not in kwargs:
            kwargs['level'] = logging.DEBUG
        # logging.basicConfig(filename=filename, format=fmt, level=level)
        logging.basicConfig(**kwargs)
        if 'filename' in kwargs and stream_also:
            # if logging to file, also log to console
            logging.getLogger().addHandler(logging.StreamHandler())
        handler = cls.get_instance()
        logging.getLogger().addHandler(handler)
        if already_exists:
            log.critical("Looks like a LoggingCounter was already created? Good luck with that...")
        else:
            # log.info("Logging system configured")
            atexit.register(cls.log_counters)
        return handler

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = LoggingCounter()
        return cls.__instance

    @classmethod
    def log_counters(cls, logger: logging.Logger = None, log_level=logging.INFO):
        cls.get_instance().__log_atexit(logger, log_level)
        # atexit.unregister(cls.log_counters)

    @classmethod
    def add_logfile(cls, filename, tgt_logger=None, **kwargs):
        if tgt_logger is None:
            tgt_logger = logging.getLogger()
        h = logging.FileHandler(filename, **kwargs)
        fmt = logging.getLogger().handlers[0].formatter
        h.setFormatter(fmt)
        tgt_logger.addHandler(h)

    @classmethod
    def get_elapsed_time(cls):
        stop_time = time.time()
        elapsed_time = stop_time - cls.get_instance().start_time
        return elapsed_time


# pytest appears to initialize logging before running the user supplied tests
# the code below does not work as intended when converted to a pytest script

# simple demo code
if __name__ == '__main__':
    ctr = LoggingCounter.config_and_attach(level=logging.INFO)

    assert ctr.count_for_level('INFO') == 0

    log.info("Info 1")
    log.info("Info 2")
    log.info("Info 3")
    assert ctr.count_for_level('INFO') == 3
    assert ctr.count_for_level(logging.INFO) == 3
    time.sleep(2)
    log.warning("Warn 1")
    assert ctr.count_for_level('WARNING') == 1

    time.sleep(2)

    et = ctr.get_elapsed_time()
    assert et > 3.95
    assert et < 4.05

    log.info(ctr.__class__.__qualname__)
    # now atexit
    # LoggingCounter.log_counters(log)
