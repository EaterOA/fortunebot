# -*- coding: utf-8 -*-

import urllib
import re

class Insult():

    NAME = "insult"

    def __init__(self):
        pass

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!insult":
            return
        return self.getInsult()

    def getInsult(self): 
        insult = ""
        try:
            page = urllib.urlopen("http://www.pangloss.com/seidel/Shaker/index.html").read()
            match = re.search("^.+?</font>$", page, re.M)
            insult = match.group(0).split('<')[0]
        except IOError:
            insult = "ERROR: Unable to retrieve insult"
        return insult

