# -*- coding: utf-8 -*-

import random

class Magic8Ball():

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

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!8ball":
            return
        return random.choice(self.messages)

