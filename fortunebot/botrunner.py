#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry class into fortunebot. Sets up basic logging, handles file paths,
and daemonizes the process if necessary.
"""

import os
import signal
import resource
import logging
from argparse import ArgumentParser
from fortunebot.bot import FortuneBot
logger = logging.getLogger("fortunebot")

class FortunebotRunner(object):

    def __init__(self, daemonize, pidpath, logpath, confpath, workpath):
        self.workpath = os.path.abspath(workpath)
        try:
            os.chdir(self.workpath)
        except Exception as ex:
            logger.error("{0}".format(ex))
            os._exit(1)
        self.daemonize = daemonize
        self.pidpath = os.path.abspath(pidpath)
        self.logpath = os.path.abspath(logpath)
        self.confpaths = ["/etc/fortunebot/fortunebot.conf",
                          os.path.abspath("fortunebot.conf")]
        if os.path.abspath(confpath) not in self.confpaths:
            self.confpaths.append(os.path.abspath(confpath))
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.siginterrupt(signal.SIGHUP, False)
        try:
            self.bot = FortuneBot()
        except Exception as ex:
            logger.error("{0}".format(ex))
            os._exit(1)

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
            if maxfd == resource.RLIM_INFINITY:
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
            os.chdir(self.workpath)

        logger.info("Starting bot")
        try:
            self.bot.load_config(self.confpaths)
            self.bot.start()
        except Exception as ex:
            logger.error("Bot died: {0}".format(ex))
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

    def _clean(self):
        if self.daemonize:
            logger.info("Removing pid file")
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                logger.warning("Problem encountered deleting pidfile: {0}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        logger.info("Disconnecting bot...")
        self.bot.disconnect("Farewell comrades!")
        self.bot.clean()
        self._clean()
        os._exit(0)

    def sighup_handler(self, signum, frame):
        logger.info("Reloading bot configs")
        self.bot.load_config(self.confpaths)

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
    parser.add_argument("--confpath", default="fortunebot.conf", help="Specify path for config file. Default fortunebot.conf")
    parser.add_argument("--pidpath", default="fortunebot.pid", help="Specify path for pid file, if daemonize. Default fortunebot.pid")
    parser.add_argument("--logpath", default="fortunebot.log", help="Specify path for log file, if daemonize. Default fortunebot.log")
    parser.add_argument("--workpath", default=".", help="Specify the working directory of the process, which affects all relative paths on command line and config file. Default current directory")
    args = parser.parse_args()

    # Start the bot!
    runner = FortunebotRunner(args.daemonize, args.pidpath,
                              args.logpath, args.confpath,
                              args.workpath)
    runner.start()

if __name__ == "__main__":
    main()
