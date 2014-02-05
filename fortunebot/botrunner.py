#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry class into fortunebot. Sets up basic logging, handles file paths,
and daemonizes the program if necessary
"""

import os
import signal
import resource
import logging
logger = logging.getLogger("fortunebot")
from argparse import ArgumentParser
from fortunebot.bot import FortuneBot

class FortunebotRunner():
    def __init__(self, daemonize, pidpath, logpath, confpath):
        self.daemonize = daemonize
        if self.daemonize and not (pidpath and logpath and confpath):
            _printError("pidfile, logfile, and confpath must be specified")
            os._exit(1)
        self.pidpath = os.path.abspath(pidpath)
        self.logpath = os.path.abspath(logpath)
        self.confpath = os.path.abspath(confpath)
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.siginterrupt(signal.SIGHUP, False)
        self.bot = FortuneBot([self.confpath, os.path.abspath("fortunebot.conf"), "/etc/fortunebot.conf"])

    def _setupLogging(self):
        """
        Setup logfile and formatting
        """
        try:
            logger.handlers = []
            hdlr = logging.FileHandler(self.logpath)
            fmtr = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(fmtr)
            logger.addHandler(hdlr)
        except IOError as e:
            logger.error("Unable to set up logging at {0}. {1}".format(self.logpath, e.strerror))
            os._exit(1)
        logger.info("Set up log file")

    def _sendBackground(self):
        """
        Send to background with double-fork
        """
        try:
            pid = os.fork()
            if pid:
                os._exit(0)
            os.setsid()
            pid = os.fork()
            if pid:
                os._exit(0)
            os.chdir("/")
            os.umask(0)
        except OSError as e:
            logger.error("Unable to fork into background. {0}".format(e.strerror))
            os._exit(1)
        logger.info("Forked into background")
        
    def _redirectIO(self):
        """
        Redirect IO to /dev/null
        """
        try:
            """
            Close all open file descriptors, including standard IO
            See code.activestate.com/recipes/278731/
            """
            maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
            if (maxfd == resource.RLIM_INFINITY):
                maxfd = 1024
            for fd in reversed(range(maxfd)):
                try:
                    os.close(fd)
                except OSError:
                    pass
            """
            Open /dev/null as fd 0, 1, and 2
            """
            open(os.devnull, "r")
            open(os.devnull, "w")
            open(os.devnull, "w")
        except IOError as e:
            logger.error("Unable to redirect IO. {0}".format(e.strerror))
            os._exit(1)
        logger.info("Redirected IO to /dev/null")

    def _writepid(self):        
        """
        Writing pidfile
        """
        try:
            pidfile = open(self.pidpath, "w")
            pidfile.write(str(os.getpid()))
            pidfile.close()
        except IOError as e:
            logger.error("Unable to write pidfile at {0}: {1}".format(self.pidpath, e.strerror))
            os._exit(1)
        logger.info("Wrote pidfile")

    def start(self):
        if self.status():
            logger.error("Bot already running!")
            os._exit(1)

        if self.daemonize:
            self._sendBackground()
            self._redirectIO()
            self._setupLogging()
            self._writepid()

        logger.info("Starting bot")
        try:
            self.bot.start()
        finally:
            self._clean()
            os._exit(1)

    def getpid(self):
        try:
            pidfile = open(self.pidpath, "r")
            pid = int(pidfile.read())
            pidfile.close()
            return pid
        except IOError:
            return None

    def status(self):
        pid = self.getpid()
        if not pid:
            return False
        return os.path.exists("/proc/{0}".format(pid))


    def stop(self):
        logger.info("Disconnecting bot")
        self.bot.disconnect("Farewell comrades!")
        self._clean()

    def _clean(self):
        if self.daemonize:
            logger.info("Removing pid file")
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                logger.warning("Problem encountered deleting pidfile: {0}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        self.stop()
        os._exit(0)

    def sighup_handler(self, signum, frame):
        self.bot.loadConfig([self.confpath, "fortunebot.conf"])
        
def main():

    # Set up basic stream logging
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    streamHandler.setFormatter(formatter) 
    logger.addHandler(streamHandler)

    # Parse input
    parser = ArgumentParser()
    parser.add_argument("--daemonize", action="store_true", default=False, help="run fortunebot as a daemon")
    parser.add_argument("--pidpath", default="/var/run/fortunebot/fortunebot.pid", help="specify path for pid file, if daemonize")
    parser.add_argument("--logpath", default="/var/log/fortunebot/fortunebot.log", help="specify path for log file, if daemonize")
    parser.add_argument("--confpath", default="/opt/fortunebot/config/fortunebot.conf", help="specify path for config file")
    args = parser.parse_args()

    # Start the bot!
    runner = FortunebotRunner(args.daemonize, args.pidpath,
                              args.logpath, args.confpath)
    runner.start()

if __name__ == "__main__":
    main()
