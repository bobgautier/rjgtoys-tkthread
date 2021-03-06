Tutorial
========

This tutorial involves taking a simple application and
making it work with Tk, first without :mod:`rjgtoys.tkthread` and
then introducing two different ways of using the :mod:`rjgtoys.tkthread`
components.

As far as I'm aware it will only run on Linux.

The examples show the full code for the four versions of the script, and
therefore are a little lengthy, but I felt it was better to show all the code
in context than to try to show fragments that might have been unclear.

Step 1: A simple :mod:`pyudev` application
------------------------------------------

The starting point is a simple command-line
application that listens for udev events,
such as plugging in, or unplugging, a USB stick.

The :mod:`pyudev` package offers a :class:`pyudev.MonitorObserver` class that
will make callbacks when an event is detected.   This script uses that to
print some details of each event.

.. literalinclude:: ../../examples/udev_notk.py

Step 2: A simple application using Tk
-------------------------------------

The next version introduces Tk. Instead of printing events, it adds them
to a :class:`tkinter.Text` widget.   In order to do that safely, because
the callbacks from the :class:`pyudev.MonitorObserver` are executed in
a thread that is not main thread running the Tk main loop, the events
generated by udev are sent into a :class:`queue.Queue` and pulled from
there by a Tk timer event handler.

The timer handler runs every five seconds.   As a result there can be a delay
of up to five seconds between
an event being detected, and it being reported.   The delay can be reduced by
decreasing the interval between timer events, or it can be eliminated altogether
by replacing the timer event handler with an ``after_idle`` handler, but as the
delay reduces, the CPU utilisation increases, and using an ``after_idle`` handler
will leave one CPU of your machine permanently busy, which is wasteful.

.. literalinclude:: ../../examples/udev_polled.py

Step 3: Efficient event handling with a :class:`rjgtoys.tkthread.EventQueue`
----------------------------------------------------------------------------

One way to avoid the delay or polling overhead of the previous example is to
use an :class:`rjgtoys.tkthread.EventQueue`.

This encapsulates the queueing that is needed to help pass events from the
source thread to the main loop thread, and the creation of a Tk event handler
that executes in the same thread as the Tk main event loop and consumes the
queued events.

.. literalinclude:: ../../examples/udev_queue.py

Step 4: Generic event collection with :class:`rjgtoys.tkthread.EventGenerator`
------------------------------------------------------------------------------

The callback interface provided by :class:`pyudev.MonitorObserver` is very
nice to use, but it's a bit unusual; in many cases the source of events will be
a function that will deliver the next event, when it arrives - and will block
until then.   That's a simple way to do file or network I/O, for example.

When the source of events can be framed as a generator, you can use
:class:`rjgtoys.tkthread.EventGenerator`
to do the job of consuming events from the generator and delivering them into
an :class:`~rjgtoys.tkthread.EventQueue`.

As a result, you no longer have to write a separate thread to do the event
collection.

.. literalinclude:: ../../examples/udev_generator.py


