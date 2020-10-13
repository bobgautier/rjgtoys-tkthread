"""
Monitor udev, without tkinter

This is a basic example of the logic.
"""

import time

import pyudev

class UdevTracer:

    def __init__(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)

        observer = pyudev.MonitorObserver(monitor, callback=self.notify, name='udev_notk')

        observer.start()

    def notify(self, device):

        print("Event: {0}".format(device))

def main():
    trace = UdevTracer()
    while True:
        print("Wait, or hit CTRL/C")
        time.sleep(5)
        # Or hit CTRL/C

if __name__ == "__main__":
    main()

