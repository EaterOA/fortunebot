# -*- coding: utf-8 -*-

import time
import re

class Replace():

    def __init__(self, cachedur):
        self.cachedur = cachedur
        if self.cachedur < 0:
            self.cachedur = 0
        self.cache = {}

    def on_poll(self):
        if not self.cachedur:
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
        if len(text) < 4 or text[:2] != 's/':
            return None
        text = text[2:]
        idx = self.findUnescapedSlash(text)
        if idx == -1:
            return None
        pattern = text[:idx]
        repl = text[(idx+1):]
        if self.findUnescapedSlash(repl) != -1:
            return None
        return [pattern, repl]

    def on_pubmsg(self, nick, channel, text):
        args = self.parseArgs(text)
        if not args:
            c = ReplaceCache(int(time.time()) + self.cachedur, text)
            self.cache[nick] = c
            return None
        pattern = args[0]
        repl = args[1]
        try:
            regobj = re.compile(pattern)
        except re.error as e:
            return "But {0}, that's not valid regex!".format(nick)
        if nick not in self.cache:
            return None
        res = regobj.sub(repl, self.cache[nick].message)
        return "{0} meant \"{1}\"".format(nick, res) 

class ReplaceCache():
    
    def __init__(self, end, message):
        self.end = end
        self.message = message

