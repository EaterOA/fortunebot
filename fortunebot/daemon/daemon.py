#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from argparse import ArgumentParser
from fortunebot.bot.bot import FortuneBot
import os, sys, signal, logging


class Daemon():
    def __init__(self, server, port, channel, nickname, isDaemon=False, pidpath="/tmp/fortunebot.pid", logpath="/tmp/fortunebot.log"):
        self.isDaemon = isDaemon
        if self.isDaemon and (not pidpath or not logpath):
            _printError("pidfile and logfile must be specified")
            sys.exit(1)
        self.pidpath = pidpath 
        self.logpath = logpath 
        self.logger = None
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        self.bot = FortuneBot(server, port, channel, nickname)

    def __printError(self, msg):
        if self.logger is not None:
            self.logger.error(msg)
        sys.stderr.write("{0}\n".format(msg))
    
    def __printInfo(self, msg):
        if self.logger is not None:
            self.logger.info(msg)
        sys.stdout.write("{0}\n".format(msg))

    def __printWarning(self, msg):
        if self.logger is not None:
            self.logger.warning(msg)
        sys.stderr.write("{0}\n".format(msg))

    def __printDebug(self, msg):
        if self.logger is not None:
            self.logger.debug(msg)
        sys.stdout.write("{0}\n".format(msg))

    def __setupLogging(self):
        """
        Setup logfile and formatting
        """
        try:
            hdlr = logging.FileHandler(self.logpath)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            self.logger = logging.getLogger("fortunebot")
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.DEBUG)
        except IOError as e:
            self.__printError("Unable to set up logging at {0}. {1}".format(self.logpath, e.strerror))
            sys.exit(1)
        self.__printDebug("Set up logging")

    def __sendBackground(self):
        """
        Send to background with double-fork
        """
        try:
            pid = os.fork()
            if pid:
                sys.exit(0)
            os.chdir("/")
            os.setsid()
            os.umask(2)
            pid = os.fork()
            if pid:
                sys.exit(0)
        except OSError as e:
            self.__printError("Unable to fork into background. {0}".format(e.strerror))
            sys.exit(1)
        self.__printDebug("Forked into background")
        
    def __redirectIO(self):
        """
        Redirect IO to /dev/null
        """
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            devnullw = open(os.devnull, 'w')
            devnullr = open(os.devnull, 'r')
            sys.stdin = devnullr
            sys.stdout = devnullw
            sys.stderr = devnullw
        except IOError as e:
            self.__printError("Unable to redirect IO. {0}".format(e.strerror))
            sys.exit(1)
        self.__printDebug("Redirected IO to /dev/null")

    def __writepid(self):        
        """
        Writing pidfile
        """
        try:
            pidfile = open(self.pidpath, "w")
            pidfile.write(str(os.getpid()))
            pidfile.close()
        except IOError as e:
            self.__printError("Unable to write pidfile at {0}. {1}".format(self.pidpath, e.strerror))
            sys.exit(1)
        self.__printDebug("Wrote pidfile")

    def start(self):
        if self.status():
            self.__printError("Bot already running!")
            sys.exit(1)

        if self.isDaemon:
            self.__setupLogging()
            self.__sendBackground()
            self.__redirectIO()
            self.__writepid()

        self.__printInfo("Starting bot...")
        try:
            self.bot.start()
            self.__printWarning("Bot has exited on its own")
        except IOError:
            self.__printError("Unable to connect to server")
        self.__clean()

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
        self.__printInfo("Stopping daemon...")
        self.bot.disconnect("Farewell comrades!")
        self.__printDebug("Disconnected bot");
        self.__clean()

    def __clean(self):
        if self.isDaemon:
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                self.__printWarning("Problem encountered deleting pidfile. {0}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        self.stop()
        sys.exit(0)

    def sighup_handler(self, signum, frame):
        self.stop()
        self.start()
        
from fortunebot.scripts import fortune

def main():
    parser = ArgumentParser()
    parser.add_argument("server")
    parser.add_argument("channel")
    parser.add_argument("nickname")
    parser.add_argument("-p", "--port", type=int, dest="port", default=6667, help="specify port, default 6667")
    parser.add_argument("--daemon", dest="daemon", action="store_true", default=False, help="run fortunebot as a daemon")
    parser.add_argument("--pid-file", dest="pidpath", default="/var/run/fortunebot/fortunebot.pid", help="specify path for pid file")
    parser.add_argument("--log-file", dest="logpath", default="/var/log/fortunebot/fortunebot.log", help="specify path for log file")
    args = parser.parse_args()
    daemon = Daemon(args.server, args.port, args.channel, args.nickname, args.daemon, args.pidpath, args.logpath)
    daemon.start()

if __name__ == "__main__":
    main()