# -*- coding: utf-8 -*-

"""
insult.py

A script that produces Shakespearean insults. It pulls insults via HTTP from
Chris Seidel's Shakespearean Insulter website.
"""

import requests
import re

class Insult(object):

    NAME = "insult"
    HELP = "!insult - Insults you elegantly"

    def on_pubmsg(self, source, channel, text):
        args = text.split()
        if not args or args[0] != "!insult":
            return
        return self.get_insult()

    def get_insult(self):
        insult = ""
        try:
            r = requests.get("http://www.pangloss.com/seidel/Shaker/index.html")
            match = re.search("^.+?</font>$", r.text, re.M)
            insult = match.group(0).split('<')[0]
        except:
            insult = "ERROR: Unable to retrieve insult"
        return insult

