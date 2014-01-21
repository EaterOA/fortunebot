#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Very simple bot module based on irclib's testbot

The known commands are:

    !insult
    --  Prints a shakespearean insult

    !w <zip code>
    --  Prints information about the weather at zip code. Zip code defaults
        to 90024 (Los Angeles)

    !fortune [category]
    --  Prints a short fortune, optionally of a specified category

    !8ball
    --  Prints a random magic 8-ball reply

    If you call the bot's nickname, it will respond with a markov-chain-
    generated response

"""

import select
import time
import errno
import irc.bot
from ConfigParser import RawConfigParser
from fortunebot.scripts import *

class FortuneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, confpaths):
        super(FortuneBot, self).__init__([], "", "")
        self.defaultConfig = self._getDefaultConfig()
        self.config = {}
        self.scripts = {}
        self.loadConfig(confpaths)

    def _getDefaultConfig(self):
        scripts = ["enable_weather", "enable_insult", "enable_fortune",
                   "enable_8ball", "enable_markov"]
        defaultConfig = dict.fromkeys(scripts, "yes")
        defaultConfig["weather_key"] = ""
        defaultConfig["markov_data"] = ""
        defaultConfig["markov_listen"] = "yes"
        defaultConfig["fortune_length"] = 100
        defaultConfig["server"] = ""
        defaultConfig["port"] = 6667
        defaultConfig["channel"] = ""
        defaultConfig["nickname"] = "fortunebot"
        defaultConfig["realname"] = "fortunebot"
        defaultConfig["reconnect"] = "yes"
        defaultConfig["reconnect_interval"] = 30
        return defaultConfig

    def loadConfig(self, confpaths):
        # Override default values with anything in config file
        parser = RawConfigParser(self.defaultConfig)
        parser.read(confpaths)
        sections = ["Connect", "Scripts"]
        for s in sections:
            if not parser.has_section(s):
                parser.add_section(s)
        c = self.config
        c["server"] = parser.get("Connect", "server")
        c["port"] = parser.getint("Connect", "port")
        c["channel"] = parser.get("Connect", "channel")
        c["nickname"] = parser.get("Connect", "nickname")
        c["realname"] = parser.get("Connect", "realname")
        c["reconnect"] = parser.getboolean("Connect", "reconnect")
        c["reconnect_interval"] = parser.getint("Connect", "reconnect_interval")
        if c["reconnect_interval"] < 0:
            c["reconnect_interval"] = 0
        c["weather_key"] = parser.get("Scripts", "weather_key")
        c["fortune_length"] = parser.getint("Scripts", "fortune_length")
        c["markov_data"] = parser.get("Scripts", "markov_data")
        c["markov_listen"] = parser.getboolean("Scripts", "markov_listen")
        #Load scripts with config
        self.scripts = {}
        if parser.getboolean("Scripts", "enable_insult"):
            self.scripts["insult"] = insult.Insult()
        if parser.getboolean("Scripts", "enable_weather"):
            self.scripts["weather"] = weather.Weather(c["weather_key"])
        if parser.getboolean("Scripts", "enable_fortune"):
            self.scripts["fortune"] = fortune.Fortune(c["fortune_length"])
        if parser.getboolean("Scripts", "enable_8ball"):
            self.scripts["8ball"] = magic8ball.Magic8Ball()
        if parser.getboolean("Scripts", "enable_markov"):
            self.scripts["markov"] = markov.Markov(c["markov_data"], c["markov_listen"], c["nickname"])

    def start(self):
        if not self.config["server"] or not self.config["channel"]:
            raise IOError("The server and channel must be specified!")
        try:
            self.connect(self.config["server"], self.config["port"], self.config["nickname"], ircname=self.config["realname"])
        except irc.client.ServerConnectionError:
            raise IOError("Unable to connect to server")
        self._process_forever()

    def disconnect(self, msg=""):
        self.config["reconnect"] = False
        self.connection.disconnect(msg)

    def on_disconnect(self, c, e):
        if self.config["reconnect"]:
            self.connection.execute_delayed(self.config["reconnect_interval"], self.connection.reconnect)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.config["channel"])

    def on_privmsg(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        nick = e.source.nick
        channel = e.target
        text = e.arguments[0].encode('utf-8')
        for name, s in self.scripts.iteritems():
            if "on_pubmsg" in dir(s):
                msg = s.on_pubmsg(nick, channel, text)
                if msg:
                    c.privmsg(channel, msg.decode("utf-8"))

    def _process_forever(self, timeout=0.2):
        """
        A hack that duplicates the IRC object's process_forever, in order
        to work around an unhandled InterruptedSystemCall exception on a
        SIGHUP
        https://bitbucket.org/jaraco/irc/issue/36/client-crashes-on-eintr
        """
        while 1:
            self._process_once(timeout)

    def _process_once(self, timeout=0):
        """
        IRC's process_once with the fix for InterruptedSystemCall
        """
        with self.ircobj.mutex:
            sockets = [x.socket for x in self.ircobj.connections if x is not None]
            sockets = [x for x in sockets if x is not None]
            if sockets:
                while 1:
                    try:
                        (i, o, e) = select.select(sockets, [], [], timeout)
                        break
                    except select.error as e:
                        if e[0] != errno.EINTR: raise
                self.ircobj.process_data(i)
            else:
                time.sleep(timeout)
            self.ircobj.process_timeout()
