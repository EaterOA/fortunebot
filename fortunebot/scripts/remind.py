# -*- coding: utf-8 -*-

import shlex
import time
from collections import deque
from fortunebot.utils import UndeadArgumentParser

class Remind():

    def __init__(self, tasklimit, durlimit):
        self.durlimit = durlimit
        self.tasklimit = tasklimit
        self.tasklist = deque()

    def on_poll(self):
        curTime = int(time.time())
        toggleList = []
        for i, t in enumerate(self.tasklist):
            if curTime >= t.end:
                toggleList.append((i, t))
        if not toggleList:
            return None
        msgList = []
        for i, t in reversed(toggleList):
            del self.tasklist[i]
            msgList.append("{0}: {1}".format(t.target, t.message))
        return msgList

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!remind":
            return
        sargs = shlex.split(" ".join(args[1:]))
        parser = UndeadArgumentParser(add_help=False)
        parser.add_argument("time", type=int)
        parser.add_argument("target")
        parser.add_argument("message")
        tformat = parser.add_mutually_exclusive_group()
        tformat.add_argument("-h", dest="tmult", action="store_const", const=60*60)
        tformat.add_argument("-d", dest="tmult", action="store_const", const=60*60*24)
        tformat.add_argument("-m", dest="tmult", action="store_const", const=60)
        try:
            pargs = parser.parse_args(sargs)
        except Exception as e:
            return "Syntax: !remind [-d | -h | -m] <time> <target> <message>"

        if not pargs.tmult:
            pargs.tmult = 1
        return self.setReminder(pargs.time*pargs.tmult, pargs.target, pargs.message)

    def setReminder(self, dur, target, message): 
        if dur < 0:
            dur = 0
        if dur > self.durlimit:
            return "NOPE. I can only remember things for {0} seconds".format(self.durlimit)
        if len(self.tasklist) == self.tasklimit:
            return "NOPE. I have too many other things to remember."
        task = ReminderTask(int(time.time()) + dur, target, message)
        self.tasklist.append(task)
        return "Task registered"

class ReminderTask():
    
    def __init__(self, end, target, message):
        self.end = end
        self.target = target
        self.message = message

