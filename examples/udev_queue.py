"""
Monitor udev, with tkinter and tkthread.EventQueue

This one will not spin a CPU, because EventQueue avoids tight polling.

"""

import os
import time
import tkinter as tk
import queue

import pyudev

from rjgtoys.tkthread import EventQueue


class UdevTracer:

    def __init__(self, widget):

        self.widget = widget

        self.queue = EventQueue(handler=self.add_message, widget=widget)

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
        self.widget.update()
        self.widget.after(5000, self.cleanup)

    def reset(self):
        self.widget.delete('1.0','end')
        self.widget.insert('1.0','Wait, or kill the window\n')

    def add_message(self, msg):
        self.widget.insert('end',msg)
        self.widget.insert('end', '\n')


def main():

    root = tk.Tk()

    w = tk.Text(root)

    tracer = UdevTracer(w)

    w.pack()
    w.mainloop()

if __name__ == "__main__":
    main()

