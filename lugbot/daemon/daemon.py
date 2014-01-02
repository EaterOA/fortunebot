#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
"""


from optparse import OptionParser
from lugbot.bot.bot import LugBot
import os, sys, signal, logging


class Daemon():
    def __init__(self, server, port, channel, nickname, isDaemon=False, piddir="/tmp/", logdir="/tmp/"):
        self.isDaemon = isDaemon
        self.pidpath = "%s/%s" % (piddir, "lugbot.pid")
        self.logpath = "%s/%s" % (logdir, "lugbot.log")
        self.logger = None
        self.isLogging = False
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        self.bot = LugBot(server, port, channel, nickname)

    def __printError(self, msg):
        if self.isLogging:
            self.logger.error(msg)
        else:
            sys.stderr.write("{0}\n".format(msg))
    
    def __printInfo(self, msg):
        if self.isLogging:
            self.logger.info(msg)
        else:
            sys.stdout.write("{0}\n".format(msg))

    def __printWarning(self, msg):
        if self.isLogging:
            self.logger.warning(msg)
        else:
            sys.stderr.write("{0}\n".format(msg))

    def __printDebug(self, msg):
        if self.isLogging:
            self.logger.debug(msg)
        else:
            sys.stdout.write("{0}\n".format(msg))

    def __setupDaemon(self):
        """
        Set up logging first
        """
        try:
            self.logger = logging.getLogger("lugbot")
            hdlr = logging.FileHandler(self.logpath)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.DEBUG)
            self.isLogging = True
        except IOError as e:
            self.__printError("Unable to set up logging. {0}".format(e.strerror))
            sys.exit(1)
        self.__printDebug("Set up logging")

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
        except OSError:
            self.__printError("Unable to fork into background")
            sys.exit(1)
        self.__printDebug("Forked into background")

        """
        Redirect stdin, stdout, and stderr to /dev/null
        """
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            devnull = open(os.devnull, 'rw')
            sys.stdin = devnull
            sys.stdout = devnull
            sys.stderr = devnull
        except IOError as e:
            self.__printError("Unable to redirect standard channels. {0}".format(e.strerror))
            sys.exit(1)
        self.__printDebug("Redirected stdin, stdout, and stderr")

        """
        Writing pidfile
        """
        try:
            pidfile = open(self.pidpath, "w")
            pidfile.write(str(os.getpid()))
            pidfile.close()
        except IOError as e:
            self.__printError("Unable to write pidfile. {0}".format(e.strerror))
            sys.exit(1)
        self.__printDebug("Wrote pidfile")

    def start(self):
        if self.status():
            self.__printError("Bot already running!")
            sys.exit(1)

        if self.isDaemon:
            self.__setupDaemon()
        self.__printDebug("Done daemonizing")
        self.__printInfo("Starting bot...")
        
        self.bot.start()
        self.__printWarning("Bot has exited on its own")
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

    def __clean(self):
        if self.isDaemon:
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                self.__printWarning("Problem encountered deleting pidfile. {0}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        self.__printInfo("Stopping daemon...")
        self.bot.disconnect("Farewell comrades!")
        self.__printDebug("Disconnected bot")
        self.__clean()
        sys.exit(0)

    def sighup_handler(self, signum, frame):
        pass
        
def main():
    usage = "Usage: %prog [options] <server> <channel> <nickname>"
    parser = OptionParser(usage)
    parser.add_option("-p", action="store", type="int", dest="port", default=6667, help="specify port, default 6667")
    parser.add_option("--daemon", action="store_true", dest="daemon", default=False, help="run lugbot as a daemon")
    parser.add_option("--pid-file", action="store", type="string", dest="piddir", default="/var/run/lugbot/", help="specify directory for pid file")
    parser.add_option("--log-file", action="store", type="string", dest="logdir", default="/var/log/lugbot/", help="specify directory for log file")
    options, args = parser.parse_args()
    if len(args) < 3:
        parser.error("You must specify server, channel, and nickname")
    daemon = Daemon(args[0], options.port, args[1], args[2], options.daemon, options.piddir, options.logdir)
    daemon.start()

if __name__ == "__main__":
    main()
