"""
tkthread - a bridge between threads and tkinter

"""

import os
import queue
import threading

import tkinter as tk


class WorkQueue(queue.Queue):

    def __init__(self, window, worker, maxsize=0):

        super().__init__(maxsize)
        self._pipe_r, self._pipe_w = os.pipe()
        self._worker = worker

        window.tk.createfilehandler(self._pipe_r, tk.READABLE, self._readable)

    def _readable(self, what, how):

        _ = os.read(self._pipe_r, 1)

        try:
            work = self.get(block=False)
        except queue.Empty:
            return

        try:
            self._worker(work)
        except Exception as e:
            # What to do?
            pass

    def put(self, work, block=True, timeout=None):
        super().put(work, block=block, timeout=timeout)
        os.write(self._pipe_w, b"x")


class WorkGenerator(threading.Thread):

    def __init__(self, *, group=None, source=None, worker=None, window=None, name=None, queue=None, maxsize=0, start=True):
        super().__init__(group=group, name=name, daemon=True)
        self._source = source
        self._queue = queue or WorkQueue(window=window, worker=worker, maxsize=maxsize)
        if start:
            self.start()

    def run(self):
        for work in self._source:
            self._queue.put(work)
