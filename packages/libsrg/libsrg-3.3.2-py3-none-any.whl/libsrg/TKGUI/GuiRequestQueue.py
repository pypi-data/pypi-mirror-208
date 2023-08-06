import logging
import queue
import random
import tkinter as tk
from tkinter import ttk

from libsrg.TKGUI.GuiRequest import GuiRequest


class GuiRequestQueue:
    _instance: "GuiRequestQueue" = None
    _key = random.randrange(0, 100000)
    logger = logging.getLogger("GuiRequestQueue")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = GuiRequestQueue(cls._key)
        return cls._instance

    def __init__(self, key):
        if key != self._key:
            raise Exception("Use get_instance, do not call constructor directly")
        self._instance = self

        self._queue = queue.Queue()
        self._callbacks = {}
        self._period = 100
        self._root = None

        self.register_callback(GuiRequest.EXIT, self.handle_exit_request)
        self.register_callback(GuiRequest.GET_NEW_LABEL, self.server_new_label)

    def register_callback(self, name, func):
        self._callbacks[name] = func

    def ask_gui_new_label(self, msg: str) -> ttk.Label:
        self.logger.info(f"msg={msg}")
        qreq = GuiRequest(GuiRequest.GET_NEW_LABEL, txt=msg)
        res = self.client_one_request(qreq)
        if res:
            return qreq.kwargs['label']
        else:
            return None

    def tell_gui_exit(self):
        self.logger.info("request")
        qreq = GuiRequest(GuiRequest.EXIT)
        self._queue.put(qreq)
        # does not wait

    def server_new_label(self, req: GuiRequest):
        lab = ttk.Label(self._root, text=req.kwargs['txt'],anchor='w',relief=tk.RAISED,justify=tk.LEFT)
        lab.pack(fill=tk.X)
        lab.configure(justify=tk.LEFT, anchor='w')
        req.kwargs['label'] = lab

    def handle_exit_request(self, _: GuiRequest):
        self.logger.info("Exiting")
        exit()

    def server_one_request(self, qreq: GuiRequest):
        qreq.success = False
        self.logger.info(qreq)
        try:
            action = qreq.action
            if action in self._callbacks:
                fun = self._callbacks[action]
                self.logger.info(qreq)
                fun(qreq)
                qreq.success = True
            else:
                self.logger.error(f"no callback registered for {qreq}")
        except Exception as ex:
            self.logger.critical(ex, exc_info=True)
        finally:
            qreq.sem.release()

    def client_one_request(self, qreq: GuiRequest) -> bool:
        self.logger.info(qreq)
        self._queue.put(qreq)
        self.logger.info(f"acquiring sem {qreq}")
        qreq.sem.acquire()
        self.logger.info(f"acquired sem {qreq}")
        return qreq.success

    def service_queue(self):
        try:
            while not (self._queue.empty()):
                qreq: GuiRequest = self._queue.get_nowait()
                self.server_one_request(qreq)
        except queue.Empty as ex:
            self.logger.critical(ex, exc_info=True)
        except Exception as ex:
            self.logger.critical(ex, exc_info=True)
        finally:
            self._root.after(self._period, self.service_queue)

    # Call once from gui thread
    def server_start_periodic(self, root, period=100):
        self._period = period
        self._root = root
        self._root.after(self._period, self.service_queue)
        self.logger.info("Started periodic calls to service_queue")

    def get_root(self):
        return self._root
