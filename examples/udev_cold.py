"""
Monitor udev, with tkinter and tkthread.WorkQueue

This one will not spin a CPU, because WorkQueue avoids tight polling.

"""

import os
import time
import tkinter as tk
import queue

import pyudev

from rjgtoys.tkthread import WorkQueue


class UdevTracer:

    def __init__(self, window):

        self.window = window

        self.queue = WorkQueue(window, self.process)

        self.cleanup()

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)

        observer = pyudev.MonitorObserver(monitor, callback=self.notify, name='udev_cold')

        observer.start()

    def notify(self, device):

        msg = "Event: {0}".format(device)
        self.queue.put(msg)

    def cleanup(self):
        self.reset()
        self.window.update()
        self.window.after(5000, self.cleanup)

    def reset(self):
        self.window.delete('1.0','end')
        self.window.insert('1.0','Wait, or kill the window\n')

    def add_message(self, msg):
        self.window.insert('end',msg)
        self.window.insert('end', '\n')

    def process(self, msg):
        """Process a queued message."""

        self.add_message(msg)


def main():

    root = tk.Tk()

    app = tk.Text(root)

    w = UdevTracer(app)

    app.pack()
    app.mainloop()

if __name__ == "__main__":
    main()

