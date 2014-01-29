#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Very simple bot module based on irclib's testbot

The known commands are:

    !help [command]
    -- Prints out help messages to the channel

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

import select, time, errno
import irc.bot
from fortunebot.EasyConfigParser import EasyConfigParser
from fortunebot.scripts import *

class FortuneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, confpaths):
        super(FortuneBot, self).__init__([], "", "")
        self._getDefaults()
        self.loadConfig(confpaths)

    def _getDefaults(self):
        self.config = {}
        self.scripts = {}
        self.defaultConfig = {
            "enable_weather": "yes",
            "enable_insult": "yes",
            "enable_fortune": "yes",
            "enable_8ball": "yes",
            "enable_markov": "yes",
            "enable_help": "yes",
            "weather_key": "",
            "markov_data": "",
            "markov_listen": "yes",
            "markov_respond": "fortunebot",
            "fortune_length": 100,
            "server": "",
            "port": 6667,
            "channel": "",
            "nickname": "fortunebot",
            "realname": "fortunebot",
            "reconnect": "yes",
            "reconnect_interval": 30
        }

    def loadConfig(self, confpaths):
        # Override default values with anything in config file
        sections = ["Connect", "Scripts"]
        parser = EasyConfigParser(self.defaultConfig, sections)
        parser.read(confpaths)
        pdict = {
            "server": parser.get("Connect", "server"),
            "port": parser.getint("Connect", "port"),
            "channel": parser.get("Connect", "channel"),
            "nickname": parser.get("Connect", "nickname"),
            "realname": parser.get("Connect", "realname"),
            "reconnect": parser.getboolean("Connect", "reconnect"),
            "reconnect_interval": parser.getint("Connect", "reconnect_interval"),
            "weather_key": parser.get("Scripts", "weather_key"),
            "fortune_length": parser.getint("Scripts", "fortune_length"),
            "markov_data": parser.get("Scripts", "markov_data"),
            "markov_listen": parser.getboolean("Scripts", "markov_listen"),
            "markov_respond": parser.get("Scripts", "markov_respond")
        }
        c = self.config
        c.update(pdict)
        if c["reconnect_interval"] < 0:
            c["reconnect_interval"] = 0
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
            self.scripts["markov"] = markov.Markov(c["markov_data"], c["markov_listen"], c["markov_respond"])
        if parser.getboolean("Scripts", "enable_help"):
            self.scripts["help"] = bothelp.BotHelp()

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
