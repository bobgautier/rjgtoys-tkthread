"""
tkthread - a bridge between threads and tkinter

.. autoclass:: EventQueue

.. autoclass:: EventGenerator

"""

import os
import queue
import threading

import tkinter as tk

import logging

log = logging.getLogger(__name__)


class EventQueue(queue.Queue):
    """This is a variation on the standard library :class:`queue.Queue` that
    feeds any objects sent to it into a tkinter callback.
    """

    def __init__(self, widget, handler, maxsize=0):
        """
        widget: A tkinter widget, None` to use the default root widget

            This widget doesn't really have to be associated with the events that are
            to be generated, it is simply needed in order to allow creation of an event handler.

        handler: A callable that will be called to handle a process.

            It is called as `handler(event)` where `event` is a value that has previously
            been `put` to the `EventQueue`.   The `handler` is called from the tkinter
            event loop and may interact with tkinter objects, however note that it is
            *not* passed the `widget` that was passed to the `EventQueue` constructor.

        maxsize (int): The maximum size of the queue.

            If maxsize <= 0 the size is not limited.


        TODO: talk about exceptions from handler, and how to feed events in.

        Must be called from the main Tk thread.

        """

        super().__init__(maxsize)
        self._pipe_r, self._pipe_w = os.pipe()
        self._handler = handler

        widget = widget or tk._default_root
        widget.tk.createfilehandler(self._pipe_r, tk.READABLE, self._readable)

    def drain(self):
        """Close the queue for further events, and process any that are waiting."""

        # Close the pipe

        for p in (self._pipe_r, self._pipe_w):
            try:
                os.close(p)
            except OSError:
                pass

        # Process all pending events

        while True:
            try:
                event = self.get(block=False)
            except queue.Empty:
                break

            try:
                self._handler(event)
            except Exception as e:
                log.exception("Exception raised by event handler")

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tbk):
        self.drain()

    def _readable(self, what, how):

        _ = os.read(self._pipe_r, 1)

        try:
            event = self.get(block=False)
        except queue.Empty:
            return

        try:
            self._handler(event)
        except Exception as e:
            log.exception("Exception raised by event handler")

    def put(self, event, block=True, timeout=None):
        """Add an event to the queue."""

        super().put(event, block=block, timeout=timeout)
        os.write(self._pipe_w, b"x")

    def put_nowait(self, event):
        """Add an event to the queue without waiting."""

        return self.put(event, block=False)

"""


target is the callable object to be invoked by the run() method. Defaults to None, meaning nothing is called.

name is the thread name. By default, a unique name is constructed of the form “Thread-N” where N is a small decimal number.

args is the argument tuple for the target invocation. Defaults to ().

kwargs is a dictionary of keyword arguments for the target invocation. Defaults to {}.

If a subclass overrides the constructor, it must make sure to invoke the base class constructor (Thread.__init__()) before doing anything else to the thread.
"""

# Name construction stuff copied from threading.py

from itertools import count as _count

# Helper to generate new EventGenerator names
_counter = _count().__next__
_counter() # Consume 0 so first non-main thread has id 1.
def _newname(template="EventGenerator-%d"):
    return template % _counter()


class EventGenerator(threading.Thread):
    """
    An :class:`EventGenerator` is a thread that fetches values from an iterable, and
    feeds each into a :class:`WorkQueue` and therefore, turns them into events
    that tkinter can process.

    """

    def __init__(
        self, *,
        generator=None,
        handler=None,
        start=True,
        queue=None,
        widget=None,
        group=None,
        name=None,
        maxsize=0,
        ):
        """
        Creates and optionally starts a thread that will generate events to
        be processed by tkinter.

        generator: An iterable that will provide the events to be processed.

            It will be called from a new thread, and each value that it generates
            will be put into a queue.

        queue: The queue into which to put the generated events.

            If `None` is passed, a new :class:`EventQueue` is created, using
            the `handler`, `widget` and `maxsize` parameters - see documentation
            for :class:`EventQueue` for descriptions of those.

        start: A boolean that indicates whether the thread should be started.

            The default is to start the thread immediately.  This saves having
            to write an explicit `start()` call.

        group: Should be `None`

            This is reserved for a future extension to :class:`threading.Thread`.

        name: A name for the thread.

            If `None` is passed, a name of the form `EventGenerator-N` is
            used, where `N` is an integer.

        Most of the above parameters will rarely be needed.   The most
        typical pattern is expected to be::

            EventGenerator(
                generator=source_of_events,
                handler=handler_of_events,
                widget=my_toplevel_widget
            )

        This creates a (notionally) unlimited sized queue and feeds events into
        it from `source_of_events`, handling them by calling `handler_of_events`
        from an event handler associated with `my_toplevel_widget`.

        """
        name = str(name or _newname())
        super().__init__(group=group, name=name, daemon=True)
        self._generator = generator
        self._queue = queue or EventQueue(widget=widget, handler=handler, maxsize=maxsize)
        if start:
            self.start()

    def run(self):
        for work in self._generator:
            self._queue.put(work)

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tbk):
        self.join()
        self._queue.drain()
