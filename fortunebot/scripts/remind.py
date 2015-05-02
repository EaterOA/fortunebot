# -*- coding: utf-8 -*-

"""
remind.py

A script that stores messages on behalf of users and plays them back after a
specified duration.
"""

from collections import defaultdict
from fortunebot.utils import UndeadArgumentParser, CacheDict
import random
import argparse
import shlex

class Remind(object):

    NAME = "remind"
    PARAMS = [("int", "tasklimit")]
    HELP = "!remind [-s|-m|-h|-d] <time> <message> - Schedule a message to be "\
           "announced after a certain time. -s, -m, -h, or -d specifies the "  \
           "time to be in seconds, minutes, hours, or days (if no option, "    \
           "defaults to days)"

    def __init__(self, tasklimit):
        self.tasklimit = tasklimit
        self.tasks = defaultdict(lambda: CacheDict(limit=tasklimit))

    def on_poll(self, channel):
        toggled = self.tasks[channel].prune()
        if not toggled:
            return
        return list(toggled.values())

    def on_pubmsg(self, source, channel, text):
        try:
            args = self.parse_args(text)
            if not args:
                return
        except Exception:
            return "Syntax: !remind [-s|-m|-h|-d] <time> <message>"
        if not args.tmult:
            args.tmult = 1
        message = " ".join(args.msg)
        return self.set_reminder(channel, args.time * args.tmult, message)

    def parse_args(self, text):
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
        return parser.parse_args(sargs)

    def set_reminder(self, channel, dur, message):
        if len(self.tasks[channel]) == self.tasklimit:
            return "NOPE. I have too many other things to remember."
        # A bit of a hack to find unique keys used to insert messages into
        # CacheDict
        rkey = random.randint(0, 1<<30)
        while rkey in self.tasks[channel]:
            rkey = random.randint(0, 1<<30)
        self.tasks[channel].insert(rkey, message, dur)
        return "Task registered"
