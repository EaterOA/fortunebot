#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry class into fortunebot. Sets up basic logging, handles file paths,
and daemonizes the process if necessary.

Hooked by setuptools into `fortunebot`
"""

import six
import sys
import os
import signal
import resource
import logging
import appdirs
from argparse import ArgumentParser
from fortunebot.bot import Fortunebot
logger = logging.getLogger("fortunebot")

class FortunebotRunner(object):

    def __init__(self, daemonize, pidpath, logpath, confpath, workpath):
        self.daemonize = daemonize
        self.workpath = os.path.abspath(workpath)
        self.pidpath = self.resolved(pidpath)
        self.logpath = self.resolved(logpath)
        self.confpaths = [
            os.path.join(
                appdirs.user_config_dir("fortunebot"), "fortunebot.conf"),
            self.resolved("fortunebot.conf"),
            self.resolved(confpath),
        ]
        try:
            self.bot = Fortunebot()
        except Exception as ex:
            die("Died when constructing bot: {}".format(ex))

    def resolved(self, path):
        return os.path.abspath(os.path.join(self.workpath, path))

    def start(self):
        if self.status():
            die("Bot already running!")

        self.setup_signals()

        if self.daemonize:
            self.send_background()
            self.redirect_IO()
            self.setup_logging()
            self.writepid()

        try:
            os.chdir(self.workpath)
        except Exception as ex:
            die("Died while changing to workpath: {}".format(ex))

        logger.info("Starting bot")
        try:
            self.bot.load_config(self.confpaths)
            self.bot.start()
        except Exception:
            logger.exception("Bot died:")
        finally:
            self.clean()
            os._exit(1)

    def setup_signals(self):
        """
        Register signal handlers
        """
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.siginterrupt(signal.SIGHUP, False)
        logger.info("Set up signal handlers")

    def setup_logging(self):
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
            die("Unable to set up logging at {}. {}".format(self.logpath, e.strerror))
        logger.info("Set up log file")

    def send_background(self):
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
            die("Unable to fork into background. {}".format(e.strerror))
        logger.info("Forked into background")

    def redirect_IO(self):
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
            for fd in reversed(six.moves.xrange(maxfd)):
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
            die("Unable to redirect IO. {}".format(e.strerror))
        logger.info("Redirected IO to /dev/null")

    def writepid(self):
        """
        Writing pidfile
        """
        try:
            pidfile = open(self.pidpath, "w")
            pidfile.write(str(os.getpid()))
            pidfile.close()
        except IOError as e:
            die("Unable to write pidfile at {}: {}".format(self.pidpath, e.strerror))
        logger.info("Wrote pidfile")

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
        return os.path.exists("/proc/{}".format(pid))

    def clean(self):
        if self.daemonize:
            logger.info("Removing pid file")
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                logger.warning("Problem encountered deleting pidfile: {}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        logger.info("Disconnecting bot...")
        self.bot.disconnect("Farewell comrades!")
        self.bot.clean()
        self.clean()
        os._exit(0)

    def sighup_handler(self, signum, frame):
        logger.info("Reloading bot configs")
        self.bot.load_config(self.confpaths)

def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument(
        "--daemonize", action="store_true", default=False,
        help="run fortunebot as a daemon")
    parser.add_argument(
        "--confpath", default="fortunebot.conf",
        help="Specify path for config file. Default fortunebot.conf")
    parser.add_argument(
        "--pidpath", default="fortunebot.pid",
        help="Specify path for pid file, if daemonize. Default fortunebot.pid")
    parser.add_argument(
        "--logpath", default="fortunebot.log",
        help="Specify path for log file, if daemonize. Default fortunebot.log")
    parser.add_argument(
        "--workpath", default=".",
        help="Specify the working directory of the process, which affects "
            "all relative paths on command line and config file. Default "
            "current directory")
    return parser.parse_args(args)

def die(msg, code=1):
    logger.error(msg)
    os._exit(1)

def main():

    # Set up basic stream logging
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Parse command line arguments
    args = parse_args(sys.argv[1:])

    # Start the bot!
    runner = FortunebotRunner(args.daemonize, args.pidpath,
                              args.logpath, args.confpath,
                              args.workpath)
    runner.start()
