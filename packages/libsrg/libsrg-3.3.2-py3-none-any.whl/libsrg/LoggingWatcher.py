#!/usr/bin/env  python3

import logging
from queue import Queue

log = logging.getLogger("libsrg.LoggingWatcher")


class LoggingWatcher(logging.Handler):
    """LoggingWatcher is a subclass of logging.Handler that counts the number of logs performed at each logging.Level
    self.count_at_level_name is a dictionary indexed by logging.Level, in which counts are maintained.
    self.frozen is a flag which freezes counts while logging counts

    This is a singleton and the constructor should not be explicitly called from outside the class methods.

    """

    __instance: "LoggingWatcher" = None

    def __init__(self, *args, **kwargs):
        super(LoggingWatcher, self).__init__(*args, **kwargs)
        self.kwargs = kwargs
        self.seen = {}
        self.queue = Queue()
        self.do_print = self.kwargs.get("do_print", False)
        self.do_queue = self.kwargs.get("do_queue", True)

    def get_queue(self) -> Queue:
        return self.queue

    def emit(self, record: logging.LogRecord) -> None:
        self.queue.put(record)

    @classmethod
    def attach(cls) -> "LoggingWatcher":
        handler = cls.get_instance()
        logging.getLogger().addHandler(handler)
        return handler

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = LoggingWatcher()
        return cls.__instance
