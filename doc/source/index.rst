rjgtoys.tkthread: Simplify using threads with tkinter
=====================================================

Like most GUI frameworks, Tk (in Python, tkinter) is event-driven, and not
thread-safe.   It's not possible to interact with a tkinter UI from a thread
other than the one in which its event loop is running.

Workarounds for this problem generally boil down to doing
some sort of polling, which either introduces delays, or is wasteful of
CPU resource.

This package provides a 'bridge' between threads and tkinter that does
not suffer from either of these problems; threads can run freely, and can
schedule operations to be performed on a tkinter UI.   Those operations
will be picked up with minimal delay and executed asynchronously with
the threads, but without incurring any polling cost.

The examples provided demonstrate the difference in CPU cost between a
'polling' solution and the one provided by this package.

.. toctree::
   :maxdepth: 2

   tutorial
   reference
   getting
   todo




