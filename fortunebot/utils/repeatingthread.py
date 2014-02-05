"""
A subclass of threading.Thread that provides the simple capability of
repeating the given function

Basically a better version of threading.Timer
"""

import threading

class RepeatingThread(threading.Thread):

    def __init__(self, interval, delay, instances, function, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval
        self.delay = delay
        self.instances = instances if instances else -1
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        if self.delay:
            self.finished.wait(self.delay)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)
            self.instances -= 1
            if self.instances == 0:
                self.finished.set()
            elif self.instances < -1000:
                self.instances = -1
