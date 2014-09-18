# -*- coding: utf-8 -*-

"""
fortune.py

A script that tells fortune messages, using the system's fortune command.
"""

from threading import Timer
from subprocess import Popen, PIPE, STDOUT
import re

class Fortune():

    NAME = "fortune"
    PARAMS = [('int', "length")]

    def __init__(self, length):
        if length < 0:
            length = 0
        self.length = length

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!fortune":
            return
        category = args[1] if len(args) > 1 else None
        return self.getFortune(category)

    def _pkill(self, p):
        if p.poll() == None:
            try:
                p.kill()
            except:
                pass

    def getFortune(self, category): 
        cmd = ["fortune", "-sn", str(self.length)]
        if category:
            #Sanitize
            category = category.split()[0]
            category = "".join([c for c in category if c.isalnum()])
            cmd.append(category)
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
        timeout = Timer(0.5, self._pkill, [proc])
        timeout.start()
        res, err = proc.communicate()
        timeout.cancel()
        if not res:
            res = "ERROR: Fortune not found" 
        else:
            res = res.strip()
            res = re.sub(r"[ \t\r\n]+", " ", res)
        return res.decode("latin-1").encode("utf-8")

