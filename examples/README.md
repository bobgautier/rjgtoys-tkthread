# Example code for `rjgtoys-tkthread`

These examples all use [pyudev](https://pyudev.readthedocs.io/en/latest/), a
Python binding to libudev.

They demonstrate four stages in the 'evolution' of a little application
that monitors for udev events (such as plugging in, or unplugging, a USB stick).

`udev_notk.py` is the baseline; the bare logic, with no Tk involvement at all.
It creates a thread that listens for udev events and prints them.

`udev_polled.py` is the next step; it uses Tk, but without the help of
this package.   Events are sent into a queue, and a Tk `after` handler
takes events from a queue and updates a widget.

`udev_queue.py` uses an `rjgtoys.tkthread.EventQueue` to avoid the polling.
This looks a little like the previous example, but there is no longer
an `after` handler, and all the Tk event loop interaction is hidden.

`udev_generator.py` uses `rjgtoys.tkthread.EventGenerator` instead, which saves
a few lines of code.


