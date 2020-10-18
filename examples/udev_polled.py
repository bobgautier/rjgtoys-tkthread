"""
Monitor udev, with tkinter but without tkthread

This one will spin a CPU, because it is polling a queue, in an idle handler.

"""

import time
import tkinter as tk
import queue

import pyudev


class UdevTracer:

    def __init__(self, widget):

        self.widget = widget

        self.queue = queue.Queue()

        self.cleanup()

        self.process()

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)

        observer = pyudev.MonitorObserver(monitor, callback=self.notify, name='udev_hot')

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

    def process(self):
        """Process queued messages."""

        # This is the expensive bit; we can't afford to wait, here,
        # because we'll make the rest of the UI unresponsive if we do.

        while True:
            try:
                msg = self.queue.get(block=False)
            except queue.Empty:
                break
            self.add_message(msg)
            self.queue.task_done()
        self.widget.update()
        self.widget.after_idle(self.process)


def main():

    root = tk.Tk()

    app = tk.Text(root)

    w = UdevTracer(app)

    app.pack()
    app.mainloop()

if __name__ == "__main__":
    main()

