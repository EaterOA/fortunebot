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

"""

import irc.bot
from ConfigParser import RawConfigParser
from fortunebot.scripts import *

class FortuneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, confpath):
        super(FortuneBot, self).__init__([], "", "")
        self.defaultConfig = self.__getDefaultConfig()
        self.config = {}
        self.loadConfig(confpath)

    def __getDefaultConfig(self):
        scripts = ["enable_weather", "enable_insult", "enable_fortune", "enable_8ball"]
        defaultConfig = dict.fromkeys(scripts, "true")
        defaultConfig['server'] = ""
        defaultConfig['port'] = 6667
        defaultConfig['channel'] = ""
        defaultConfig['nickname'] = "fortunebot"
        defaultConfig['realname'] = "fortunebot"
        defaultConfig['reconnect_interval'] = 30
        return defaultConfig

    def loadConfig(self, confpaths):
        # Override default values with anything in config file
        parser = RawConfigParser(self.defaultConfig)
        parser.read(confpaths)
        sections = ["Connect", "Scripts"]
        for s in sections:
            if not parser.has_section(s):
                parser.add_section(s)
        self.config['server'] = parser.get('Connect', 'server')
        self.config['port'] = parser.getint('Connect', 'port')
        self.config['channel'] = parser.get('Connect', 'channel')
        self.config['nickname'] = parser.get('Connect', 'nickname')
        self.config['realname'] = parser.get('Connect', 'realname')
        self.config['reconnect_interval'] = parser.getint('Connect', 'reconnect_interval')
        for s in ["enable_weather", "enable_insult",
                  "enable_fortune", "enable_8ball"]:
            self.config[s] = parser.getboolean("Scripts", s)

    def start(self):
        if not self.config['server'] or not self.config['channel']:
            raise IOError("The server and channel must be specified!")
        try:
            self.connect(self.config['server'], self.config['port'], self.config['nickname'], ircname=self.config['realname'])
        except irc.client.ServerConnectionError:
            raise IOError("Unable to connect to server")
        self.ircobj.process_forever()

    def disconnect(self, msg=""):
        self.tryReconnect = False
        self.connection.disconnect(msg)

    def on_disconnect(self, c, e):
        if self.config['reconnect_interval'] > 0:
            self.connection.execute_delayed(self.config['reconnect_interval'], self.connection.reconnect)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.config["channel"])

    def on_privmsg(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        text = e.arguments[0].split()
        if text and text[0][0] == "!":
            self.do_command(e, text[0], text[1:])

    def do_command(self, e, cmd, args):
        nick = e.source.nick
        channel = e.target
        c = self.connection

        if self.config["enable_insult"] and cmd == "!insult":
            msg = insult.getInsult()
            c.privmsg(channel, msg)
        if self.config["enable_weather"] and cmd == "!w":
            zipcode = "90024"
            if args:
                zipcode = args[0]
            msg = weather.getWeather(zipcode)
            c.privmsg(channel, msg)
        if self.config["enable_fortune"] and cmd == "!fortune":
            category = None
            if args:
                category = args[0]
            msg = fortune.getFortune(category)
            c.privmsg(channel, msg)
        if self.config["enable_8ball"] and cmd == "!8ball":
            msg = magic8ball.get8Ball()
            c.privmsg(channel, msg)

