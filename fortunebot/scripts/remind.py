# -*- coding: utf-8 -*-

import shlex
import time
from collections import defaultdict, deque
from fortunebot.utils import UndeadArgumentParser
import argparse

class Remind():

    def __init__(self, tasklimit, durlimit):
        self.durlimit = durlimit
        self.tasklimit = tasklimit
        self.tasklist = defaultdict(deque)

    def on_poll(self, channel):
        curTime = int(time.time())
        toggleList = []
        for i, t in enumerate(self.tasklist[channel]):
            if curTime >= t[0]:
                toggleList.append((i, t))
        if not toggleList:
            return None
        msgList = []
        for i, t in reversed(toggleList):
            del self.tasklist[channel][i]
            msgList.append(t[1])
        return msgList

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!remind":
            return
        sargs = shlex.split(" ".join(args[1:]))
        parser = UndeadArgumentParser(add_help=False)
        parser.add_argument("time", type=int)
        parser.add_argument("msg", nargs=argparse.REMAINDER)
        tformat = parser.add_mutually_exclusive_group()
        tformat.add_argument("-s", dest="tmult", action="store_const", const=1)
        tformat.add_argument("-h", dest="tmult", action="store_const", const=60*60)
        tformat.add_argument("-d", dest="tmult", action="store_const", const=60*60*24)
        tformat.add_argument("-m", dest="tmult", action="store_const", const=60)
        try:
            pargs = parser.parse_args(sargs)
        except Exception:
            return "Syntax: !remind [-s|-m|-h|-d] <time> <message>"
        if not pargs.tmult:
            pargs.tmult = 1
        message = " ".join(pargs.msg)
        return self.setReminder(channel, pargs.time * pargs.tmult, message)

    def setReminder(self, channel, dur, message):
        if dur < 0:
            dur = 0
        if dur > self.durlimit:
            return "NOPE. I can only remember things for {0} seconds".format(self.durlimit)
        if len(self.tasklist[channel]) == self.tasklimit:
            return "NOPE. I have too many other things to remember."
        task = (int(time.time()) + dur, message)
        self.tasklist[channel].append(task)
        return "Task registered"
