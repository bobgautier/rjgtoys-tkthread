"""

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
    """This is a subclass of the standard library :class:`queue.Queue`.

    An :class:`~rjgtoys.tkthread.EventQueue` feeds any objects sent to it into a
    handler function that is called from the main Tk event loop.

    **NOTE**:

      The constructor for :class:`EventQueue` must be called from the main Tk thread.

    ``handler``
        A callable that will be called to handle a process.
        It is called as ``handler(event)`` where ``event`` is a value that has previously
        been :meth:`put` to the :class:`EventQueue`.   The ``handler`` is called from the tkinter
        event loop and may interact with tkinter objects, however note that it is
        *not* passed the ``widget`` that was passed to the :class:`EventQueue` constructor.

    ``widget``
        A tkinter widget, or ``None`` to use the default root widget.
        This widget reference is used to create a Tk event handler; it
        doesn't really have to be associated with the events that are
        to be generated or handled.

    ``maxsize``
        The maximum size of the queue.
        If ``maxsize <= 0`` the size is not limited.


    TODO: talk about exceptions from handler, and how to feed events in.

    An :class:`EventQueue` implements the context manager protocol, which means it
    can be used like this::

        with EventQueue(handler=handle_event) as q:
            invoke_process_to_feed_events_to(q)

    The context manager exit operation calls :meth:`drain` on the queue, so all events have
    been processed by the time the ``with`` completes.

    .. automethod:: put
    .. automethod:: put_nowait
    .. automethod:: drain

    """

    def __init__(self, handler, widget=None, maxsize=0):

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
        """Add an event to the queue.

        ``block``
           If ``True`` (the default), then wait if the queue is full,
           otherwise raise :exc:`queue.Full` immediately.

        ``timeout``
           If ``block`` is ``True``, specifies the maximum time to wait,
           in seconds, before raising :exc:``queue.Full`` if the queue
           remains full.   A value of ``None`` means wait indefinitely.
           Ignored if ``block`` is ``False``.
        """

        super().put(event, block=block, timeout=timeout)
        os.write(self._pipe_w, b"x")

    def put_nowait(self, event):
        """Add an event to the queue without waiting.

        Either puts the event, or raises :exc:`queue.Full` immediately.
        """

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
    An :class:`~rjgtoys.tkthread.EventGenerator` is a subclass of :class:`threading.Thread`.

    The constructor creates and optionally starts a thread that fetches values
    from an iterable, and feeds each into a :class:`~rjgtoys.tkthread.EventQueue`
    which in turn will make callbacks to a handler function, to process the
    events in the main Tk thread.

    ``generator``
        An iterable that will provide the events to be processed.

        It will be called from a new thread, and each value that it generates
        will be put into a queue.

    ``queue``
        The queue into which to put the generated events.

        If `None` is passed, a new :class:`~rjgtoys.tkthread.EventQueue` is created,
        using the ``handler``, ``widget`` and ``maxsize`` parameters - see
        :class:`~rjgtoys.tkthread.EventQueue` for descriptions of those.

    ``start``
        A boolean that indicates whether the thread should be started.

        The default is to start the thread immediately.  This saves having
        to write an explicit call to :meth:`start`.

    ``group``
        Should be ``None``.

        This is reserved for a future extension to :class:`threading.Thread`.

    ``name``
        A name for the thread.

        If ``None`` is passed, a name of the form ``EventGenerator-N`` is
        used, where ``N`` is an integer.

    Most of the above parameters will rarely be needed.   The most
    typical pattern is expected to be::

        EventGenerator(
            generator=source_of_events,
            handler=handler_of_events,
            widget=my_toplevel_widget
        )

    This creates a (notionally) unlimited sized :class:`~rjgtoys.tkthread.EventQueue`
    which handles events put into it by calling ``handler_of_events``
    from an event handler associated with ``my_toplevel_widget``.   The events
    are generated by a thread that calls ``source_of_events`` until it is exhausted.

    :class:`~rjgtoys.tkthread.EventGenerator` implements the context manager protocol.
    If used as a context manager, exiting the context implies calling :meth:`drain`
    and so exit is delayed until the generator is exhausted and the queue drained -
    i.e. until all events have been processed.

    .. py:method:: start()

      Starts the event collection thread (a loop that calls the ``generator``
      specified in the constructor).

      This call is unnecessary if ``start=True`` was passed (or defaulted) to
      the constructor.

    .. py:method:: join(timeout=None)

       Waits (for up to ``timeout`` seconds, or indefinitely if ``timeout is None``)
       for completion of the event generator.   Note: does *not* drain the queue.

    .. automethod:: drain

    .. automethod:: run

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
        name = str(name or _newname())
        super().__init__(group=group, name=name, daemon=True)
        self._generator = generator
        self._queue = queue or EventQueue(handler=handler, widget=widget, maxsize=maxsize)
        if start:
            self.start()

    def run(self):
        """Consumes the generator iterable and sends each value to the queue.

        Terminates when and if the generator terminates.

        You might want to override this in a subclass if you want to use generators
        that have unusual ways of signalling (early?) completion.
        """

        for work in self._generator:
            self._queue.put(work)

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tbk):
        self.drain()

    def drain(self, timeout=None):
        """Wait until the generator and queue have been processed.

        Calls ``join(timeout)`` and then calls ``drain`` on the queue (even if the ``join`` timed out).

        """

        self.join(timeout=timeout)
        self._queue.drain()
