# -*- coding: utf-8 -*-

"""
remind.py

A script that stores messages on behalf of users and plays them back after a
specified duration.
"""

import shlex
import time
from collections import defaultdict, deque
from fortunebot.utils import UndeadArgumentParser
import argparse

class Remind(object):

    NAME = "remind"
    PARAMS = [("int", "tasklimit"),
              ("int", "durlimit")]
    HELP = "!remind [-s|-m|-h|-d] <time> <message> - Schedule a message to be "\
           "announced after a certain time. -s, -m, -h, or -d specifies the "  \
           "time to be in seconds, minutes, hours, or days (if no option, "    \
           "defaults to days)"

    def __init__(self, tasklimit, durlimit):
        self.durlimit = durlimit
        self.tasklimit = tasklimit
        self.tasklist = defaultdict(deque)

    def on_poll(self, channel):
        now = int(time.time())
        toggle_list = []
        for i, t in enumerate(self.tasklist[channel]):
            if now >= t[0]:
                toggle_list.append((i, t))
        if not toggle_list:
            return None
        msg_list = []
        for i, t in reversed(toggle_list):
            del self.tasklist[channel][i]
            msg_list.append(t[1])
        return msg_list

    def on_pubmsg(self, source, channel, text):
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
        return self.set_reminder(channel, pargs.time * pargs.tmult, message)

    def set_reminder(self, channel, dur, message):
        if dur < 0:
            dur = 0
        if dur > self.durlimit:
            return "NOPE. I can only remember things for {0} seconds".format(self.durlimit)
        if len(self.tasklist[channel]) == self.tasklimit:
            return "NOPE. I have too many other things to remember."
        task = (int(time.time()) + dur, message)
        self.tasklist[channel].append(task)
        return "Task registered"
