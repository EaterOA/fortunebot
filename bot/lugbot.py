#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Very simple skeleton lugbot based off of irclib's testbot

Run using:
python lugbot.py <server[:port]> <channel> <nickname>

The known commands are:

    !die
    --  Commit roboticide

    !insult
    --  Prints a shakespearean insult

    !w <zip code>
    --  Prints information about the weather at zip code. Zip code defaults
        to 90024 (Los Angeles)

    !fortune [category]
    --  Prints a short fortune, optionally of a specified category

    !8ball
    --  Prints a random magic 8-ball reply

"""


from optparse import OptionParser
import irc.bot
import os, sys, inspect

botPath = os.path.realpath(inspect.getfile(inspect.currentframe()))
botDir = os.path.split(botPath)[0]
rootDir = os.path.dirname(botDir)
scriptDir = os.path.join(rootDir, "scripts")
if scriptDir not in sys.path:
    sys.path.insert(0, scriptDir)

import insult
import weather
import fortune
import magic8ball

class LugBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        text = e.arguments[0].split()
        if text and text[0][0] == "!":
            self.do_command(e, text[0], text[1:])

    def do_command(self, e, cmd, args):
        nick = e.source.nick
        c = self.connection

        if cmd == "!die":
            self.die()
        elif cmd == "!insult":
            msg = insult.getInsult()
            c.privmsg(self.channel, msg)
        elif cmd == "!w":
            zipcode = "90024"
            if args:
                zipcode = args[0]
            msg = weather.getWeather(zipcode)
            c.privmsg(self.channel, msg)
        elif cmd == "!fortune":
            category = None
            if args:
                category = args[0]
            msg = fortune.getFortune(category)
            c.privmsg(self.channel, msg)
        elif cmd == "!8ball":
            msg = magic8ball.get8Ball()
            c.privmsg(self.channel, msg)
                 

def main(server, port, channel, nickname):
    bot = LugBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    usage = "Usage: %prog [options] <server> <channel> <nickname>"
    parser = OptionParser(usage)
    parser.add_option("-p", action="store", type="int", dest="port", default=6667, help="specify port, default 6667")
    options, args = parser.parse_args()
    if len(args) < 3:
        parser.error("You must specify a server, channel, and nickname")
    main(args[0], options.port, args[1], args[2])
