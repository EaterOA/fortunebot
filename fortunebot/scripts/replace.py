# -*- coding: utf-8 -*-

import time
import re
import shlex
from fortunebot.utils import UndeadArgumentParser
from argparse import ArgumentError

class Replace():

    def __init__(self, enableShortcut, maxLength, cacheDur):
        self.enableShortcut = enableShortcut
        self.maxLength = maxLength
        self.cacheDur = cacheDur
        if self.cacheDur < 0:
            self.cacheDur = 0
        self.cache = {}

    def on_poll(self):
        if not self.cacheDur:
            return None
        curTime = int(time.time())
        expiredList = []
        for k, v in self.cache.iteritems():
            if curTime >= v.end:
                expiredList.append(k)
        for k in expiredList:
            del self.cache[k]
        return None

    def findUnescapedSlash(self, text):
        l = 0
        r = len(text)
        while l < r:
            if text[l] == '\\':
                l += 1
            elif text[l] == '/':
                return l
            l += 1
        return -1

    def parseArgs(self, text):
        if len(text) < 4:
            return None
        if self.enableShortcut and text[:2] == 's/':
            text = text[2:]
            idx = self.findUnescapedSlash(text)
            if idx == -1:
                return None
            pattern = text[:idx]
            repl = text[(idx+1):]
            if not pattern:
                return None
            return [pattern, repl]
        args = text.split()
        if args[0] == "!replace":
            sargs = shlex.split(" ".join(args[1:])) 
            parser = UndeadArgumentParser(add_help=False)
            parser.add_argument("pattern")
            parser.add_argument("repl")
            pargs = parser.parse_args(sargs)
            return [pargs.pattern, pargs.repl]
        return None
            

    def on_pubmsg(self, nick, channel, text):
        try:
            args = self.parseArgs(text)
        except ArgumentError as e:
            return "Syntax: !replace <pattern> <repl>"
        if not args:
            c = ReplaceCache(int(time.time()) + self.cacheDur, text)
            self.cache[nick] = c
            return None
        if nick not in self.cache:
            return None
        pattern = args[0]
        repl = args[1]
        try:
            res = re.sub(pattern, repl, self.cache[nick].message)
        except re.error as e:
            return "But {0}, that's not valid regex!".format(nick)
        # Limit length to prevent abuse
        if len(res) > self.maxLength:
            res = res[:self.maxLength] + "[...]"
        return "{0} meant: {1}".format(nick, res) 

class ReplaceCache():
    
    def __init__(self, end, message):
        self.end = end
        self.message = message

