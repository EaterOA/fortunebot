#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
bot.py

The main bot engine, a subclass of irclib's SingleServerIRCBot. It's fitted
with a configuration system, dynamic script plug-in system, and slightly
enhanced basic IRC event handling (reconnects, etc).
"""

import select
import time
import errno
import logging
import importlib
import inspect
import irc.bot
from fortunebot.utils import EasyConfigParser, RepeatingThread
import fortunebot.scripts
logger = logging.getLogger("fortunebot")
"""
irclog = logging.getLogger("irc.client")
irclog.addHandler(logging.StreamHandler())
irclog.setLevel("DEBUG")
"""

class FortuneBot(irc.bot.SingleServerIRCBot):

    def __init__(self, confpaths):
        super(FortuneBot, self).__init__([], "", "")
        self.config = {}
        self.scripts = {}
        self.help_msg = {}
        self.ping_thread = None
        self.loadConfig(confpaths)
        self.poll_thread = RepeatingThread(1.0, 0.0, 0, self.on_poll)
        self.ping_thread = RepeatingThread(self.config["ping_interval"], 0.0, 0, self.probe_connection)
        self.ping_ignored = 0
        self.exit = False

    def clean(self):
        for name in self.scripts.keys():
            del self.scripts[name]

    def loadConfig(self, confpaths):
        logger.info("Loading config from {0}".format(", ".join(confpaths)))

        # Reset configurations
        self.config = {}
        self.scripts = {}
        self.help_msg = {}

        # Read core settings from config file
        sections = ["Connect", "Scripts"]
        parser = EasyConfigParser(sections=sections)
        if not parser.read(confpaths):
            raise Exception("No config files were found or successfully read")
        self.config = {
            "server": parser.get("Connect", "server"),
            "port": parser.getint("Connect", "port"),
            "channels": parser.get("Connect", "channels").split(" "),
            "nickname": parser.get("Connect", "nickname"),
            "realname": parser.get("Connect", "realname"),
            "reconnect_tries": parser.getint("Connect", "reconnect_tries"),
            "reconnect_interval": parser.getint("Connect", "reconnect_interval"),
            "ping_tries": parser.getint("Connect", "ping_tries"),
            "ping_interval": parser.getint("Connect", "ping_interval"),
        }
        self.config["reconnect_tries"] = max(0, self.config["reconnect_tries"])
        self.config["reconnect_interval"] = max(0, self.config["reconnect_interval"])
        self.config["ping_tries"] = max(0, self.config["ping_tries"])
        self.config["ping_interval"] = max(0, self.config["ping_interval"])
        if self.ping_thread:
            self.ping_thread.change_interval(self.config["ping_interval"])

        # Dynamically load scripts
        module_names = fortunebot.scripts.__all__
        ### Get modules in scripts subpackage
        modules = [importlib.import_module("fortunebot.scripts.{0}".format(m))
                   for m in module_names]
        ### Get a valid (NAME'd) class from each module
        classes = []
        seen = set()
        for m in modules:
            for _, obj in inspect.getmembers(m):
                if (inspect.isclass(obj) and
                        "NAME" in dir(obj) and
                        obj.NAME not in seen):
                    classes.append(obj)
                    seen.add(obj.NAME)
                    break
        ### Retrieve configurations and instantiate script objects
        pfuncs = {'str': parser.get,
                  'int': parser.getint,
                  'float': parser.getfloat,
                  'bool': parser.getboolean}
        for c in classes:
            try :
                if parser.getboolean("Scripts", "enable_{0}".format(c.NAME)):
                    params = {}
                    if "PARAMS" in dir(c):
                        for t, p in c.PARAMS:
                            params[p] = pfuncs[t]("Scripts", "{0}_{1}"
                                                  .format(c.NAME, p))
                    if "HELP" in dir(c):
                        self.help_msg[c.NAME] = c.HELP
                    self.scripts[c.NAME] = c(**params)
            except Exception as e:
                logger.warning("Script {0} initialization error: {1}".format(c.NAME, e))

    def start(self):
        if not self.config["server"] or not self.config["channels"]:
            logger.error("No configurations for server and channels found!")
            return
        try:
            self.connect(self.config["server"], self.config["port"], self.config["nickname"], ircname=self.config["realname"])
        except irc.client.ServerConnectionError:
            logger.error("Unable to connect to server")
            return
        self._process_forever()

    def disconnect(self, msg=""):
        self.config["reconnect"] = False
        self.connection.disconnect(msg)

    def send_msg(self, channel, msg):
        if not msg:
            return
        c = self.connection
        illegal = ""
        for ch in range(32):
            illegal += chr(ch)
        if type(msg) is str:
            msg = [msg]
        for m in msg:
            if type(m) is str:
                m = m.translate(None, illegal)
                c.privmsg(channel, m.decode("utf-8"))

    def reconnect(self):
        for count in xrange(self.config["reconnect_tries"]):
            logger.info("Reconnecting to server (try #{0})...".format(count+1))
            self.connection.reconnect()
            time.sleep(self.config["reconnect_interval"])
            if self.connection.is_connected():
                return
        logger.warning("Shutting down due to maximum reconnect limit")
        self.exit = True

    def on_disconnect(self, c, e):
        logger.info("Disconnected from server")
        self.poll_thread.cancel()
        self.ping_thread.cancel()
        self.ping_ignored = 0
        if self.config["reconnect_tries"]:
            self.connection.execute_delayed(self.config["reconnect_interval"], self.reconnect)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        logger.info("Connected to server")
        self.poll_thread.start()
        self.ping_thread.start()
        for ch in self.config["channels"]:
            c.join(ch)

    def probe_connection(self):
        self.ping_ignored += 1
        if self.ping_ignored == self.config["ping_tries"]:
            logger.warning("Ping try limit reached without response, disconnecting...")
            self.connection.disconnect()
        else:
            self.connection.ping(self.config["server"])

    def on_pong(self, c, e):
        self.ping_ignored = 0

    def on_poll(self):
        for name, s in self.scripts.items():
            if "on_poll" in dir(s):
                for ch in self.config["channels"]:
                    try:
                        msg = s.on_poll(ch)
                    except Exception as e:
                        logger.warning("{0} script error during on_poll for {1}: {2}".format(name, ch, e))
                        msg = None
                    self.send_msg(ch, msg)

    def parse_help(self, text):
        msg = None
        if text.startswith("!help"):
            args = text.split(None, 1)
            script = args[1] if len(args) > 1 else None
            if script:
                if script not in self.scripts:
                    msg = "\"{0}\" unknown or inactive".format(script)
                elif script not in self.help_msg:
                    msg = "No help messages defined for {0}!".format(script)
                else:
                    msg = self.help_msg[script]
            else:
                msg = "!help [script] - Active scripts: "
                msg += ", ".join(self.scripts.keys())
        return msg

    def on_privmsg(self, c, e):

        # Extract info
        nick = e.source.nick
        text = e.arguments[0].encode('utf-8')

        # Handle help
        help_msg = self.parse_help(text)
        if help_msg:
            self.send_msg(nick, help_msg)

    def on_pubmsg(self, c, e):

        # Extract info
        nick = e.source.nick
        channel = e.target
        text = e.arguments[0].encode('utf-8')

        # Handle help
        help_msg = self.parse_help(text)
        if help_msg:
            self.send_msg(channel, help_msg)

        # Invoke scripts
        for name, s in self.scripts.items():
            if "on_pubmsg" in dir(s):
                try:
                    msg = s.on_pubmsg(nick, channel, text)
                except Exception as ex:
                    logger.warning("{0} script error during on_pubmsg: {1}".format(name, ex))
                    msg = None
                self.send_msg(channel, msg)

    def _process_forever(self, timeout=0.2):
        """
        A hack that duplicates the IRC object's process_forever, in order
        to work around an unhandled InterruptedSystemCall exception on a
        SIGHUP
        https://bitbucket.org/jaraco/irc/issue/36/client-crashes-on-eintr
        Also added a way to end the loop
        """
        while not self.exit:
            try:
                self.reactor.process_once(timeout)
            except select.error as err:
                if err[0] != errno.EINTR:
                    raise
