# -*- coding: utf-8 -*-

"""
choose.py
"""

import random

class Choose(object):

    NAME = "choose"
    HELP = "!choose [choices...] - Helps you make a decision (DISCLAIMER: Not "\
           "liable for any damage or consequence that result from said decision"

    def on_pubmsg(self, source, channel, text):
        text = text.lower()
        args = text.split()
        if not args or args[0] != "!choose":
            return
        if len(args) == 1:
            return "NO, YOU"
        return "I choose: {0}".format(random.choice(args[1:]))
