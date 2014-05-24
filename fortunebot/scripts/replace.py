# -*- coding: utf-8 -*-

import time
import re
import shlex
from fortunebot.utils import UndeadArgumentParser
from argparse import ArgumentError
from collections import deque

class Replace():

    def __init__(self, enableShortcut, maxLength, maxLines):
        self.enableShortcut = enableShortcut
        self.maxLength = maxLength
        self.maxLines = maxLines
        self.cache = {}

    def squeeze(self, num, left, right):
        if num < left: return left
        if num > right: return right
        return num

    def findUnescapedSlash(self, text):
        l = 0
        r = len(text)
        while l < r:
            if text[l] == '\\':
                l += 1
            elif text[l] == '/':
                break
            l += 1
        return l

    def splitByUnescapedSlash(self, text):
        tokens = []
        while 1:
            idx = self.findUnescapedSlash(text)
            if idx == len(text):
                tokens.append(text)
                break
            tokens.append(text[:idx])
            text = text[(idx+1):]
        return tokens

    def getFirstNumber(self, s):
        found = False
        n = 0
        for c in s:
            if c >= "0" and c <= "9":
                found = True
                n = n*10 + int(c)
            elif n != 0:
                break
        if not found:
            return -1
        return n

    def parseArgs(self, text):
        if len(text) < 4:
            return None
        if self.enableShortcut and text[:2] == 's/':
            tokens = self.splitByUnescapedSlash(text)
            if len(tokens) < 3:
                return None
            pattern = tokens[1]
            repl = tokens[2]
            flags = "" if len(tokens) == 3 else tokens[3]
            line = self.getFirstNumber(flags)
            search = "s" in flags
            return [pattern, repl, line, search]
        args = text.split()
        if args[0] == "!replace":
            sargs = shlex.split(" ".join(args[1:])) 
            parser = UndeadArgumentParser(add_help=False)
            parser.add_argument("pattern")
            parser.add_argument("repl")
            parser.add_argument("-l", "--line", type=int, default=-1, dest="line")
            parser.add_argument("-s", "--search", action="store_true", default=False, dest="search")
            pargs = parser.parse_args(sargs)
            return [pargs.pattern, pargs.repl, pargs.line, pargs.search]
        return None
            

    def on_pubmsg(self, nick, channel, text):
        try:
            args = self.parseArgs(text)
        except ArgumentError as e:
            return "Syntax: !replace [-l <line> | -s] <pattern> <repl>"
        if not args:
            if nick not in self.cache:
                self.cache[nick] = deque()
            while len(self.cache[nick]) >= self.maxLines:
                self.cache[nick].pop()
            self.cache[nick].appendleft(text)
            return None
        if nick not in self.cache:
            return None
        pattern = args[0]
        repl = args[1]
        line = self.squeeze(args[2], -1, len(self.cache[nick])-1)
        search = args[3]
        if line == -1:
            if search:
                flag = True
                for message in self.cache[nick]:
                    if re.search(pattern, message):
                        flag = False
                        break
                if flag:
                    return "Unable to find anything that matches pattern!"
            else:
                message = self.cache[nick][0]
        else:
            message = self.cache[nick][line]
        try:
            res = re.sub(pattern, repl, message)
        except re.error as e:
            return "But {0}, that's not valid regex!".format(nick)
        # Limit length to prevent abuse
        if len(res) > self.maxLength:
            res = res[:self.maxLength] + "[...]"
        return "{0} meant: {1}".format(nick, res) 
