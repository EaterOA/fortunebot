# -*- coding: utf-8 -*-

"""
magic8ball.py

A script that produces random magic 8 ball responses.
"""

import random

class Magic8Ball(object):

    NAME = "8ball"
    HELP = "!8ball [question] - Seek answer from the magic 8-ball"

    def __init__(self):
        self.messages = ["It is certain", "It is decidedly so",
                         "Without a doubt", "Yes definitely",
                         "You may rely on it", "As I see it, yes",
                         "Most likely", "Outlook good",
                         "Yes", "Signs point to yes",
                         "Reply hazy try again", "Ask again later",
                         "Better not tell you now", "Cannot predict now",
                         "Concentrate and ask again", "Don't count on it",
                         "My reply is no", "My sources say no",
                         "Outlook not so good", "Very doubtful"]

    def on_pubmsg(self, source, channel, text):
        args = text.split()
        if not args or args[0] != "!8ball":
            return
        return random.choice(self.messages)

