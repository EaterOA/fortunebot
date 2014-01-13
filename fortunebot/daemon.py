#! /usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from fortunebot.bot import FortuneBot
import os, sys, signal, logging, resource

class Daemon():
    def __init__(self, isDaemon, pidpath, logpath, confpath):
        self.isDaemon = isDaemon
        if self.isDaemon and not (pidpath and logpath and confpath):
            _printError("pidfile, logfile, and confpath must be specified")
            os._exit(1)
        self.pidpath = pidpath
        self.logpath = logpath
        self.confpath = confpath
        self.logger = None
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        signal.signal(signal.SIGHUP, self.sighup_handler)
        signal.siginterrupt(signal.SIGHUP, False)
        self.bot = FortuneBot([confpath, "fortunebot.conf"])

    def _printError(self, msg):
        if self.logger is not None:
            self.logger.error(msg)
        sys.stderr.write("{0}\n".format(msg))
    
    def _printInfo(self, msg):
        if self.logger is not None:
            self.logger.info(msg)
        sys.stdout.write("{0}\n".format(msg))

    def _printWarning(self, msg):
        if self.logger is not None:
            self.logger.warning(msg)
        sys.stderr.write("{0}\n".format(msg))

    def _printDebug(self, msg):
        if self.logger is not None:
            self.logger.debug(msg)
        sys.stdout.write("{0}\n".format(msg))

    def _setupLogging(self):
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
            self._printError("Unable to set up logging at {0}. {1}".format(self.logpath, e.strerror))
            os._exit(1)
        self._printDebug("Set up logging")

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
            self._printError("Unable to fork into background. {0}".format(e.strerror))
            os._exit(1)
        self._printDebug("Forked into background")
        
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
            self._printError("Unable to redirect IO. {0}".format(e.strerror))
            os._exit(1)
        self._printDebug("Redirected IO to /dev/null")

    def _writepid(self):        
        """
        Writing pidfile
        """
        try:
            pidfile = open(self.pidpath, "w")
            pidfile.write(str(os.getpid()))
            pidfile.close()
        except IOError as e:
            self._printError("Unable to write pidfile at {0}. {1}".format(self.pidpath, e.strerror))
            os._exit(1)
        self._printDebug("Wrote pidfile")

    def start(self):
        if self.status():
            self._printError("Bot already running!")
            os._exit(1)

        if self.isDaemon:
            self._sendBackground()
            self._redirectIO()
            self._setupLogging()
            self._writepid()

        self._printInfo("Starting bot...")
        try:
            self.bot.start()
        except Exception as e:
            self._printError(e)
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
        self._printInfo("Stopping daemon...")
        self.bot.disconnect("Farewell comrades!")
        self._printDebug("Disconnected bot");
        self._clean()

    def _clean(self):
        if self.isDaemon:
            try:
                if os.path.exists(self.pidpath):
                    os.remove(self.pidpath)
            except OSError as e:
                self._printWarning("Problem encountered deleting pidfile. {0}".format(e.strerror))

    def sigterm_handler(self, signum, frame):
        self.stop()
        os._exit(0)

    def sighup_handler(self, signum, frame):
        #self.bot.loadConfig([self.confpath, "fortunebot.conf"])
        pass
        
def main():
    parser = ArgumentParser()
    parser.add_argument("--daemon", dest="daemon", action="store_true", default=False, help="run fortunebot as a daemon")
    parser.add_argument("--pid-file", dest="pidpath", default="/var/run/fortunebot/fortunebot.pid", help="specify path for pid file")
    parser.add_argument("--log-file", dest="logpath", default="/var/log/fortunebot/fortunebot.log", help="specify path for log file")
    parser.add_argument("--conf-file", dest="confpath", default="/opt/fortunebot/config/fortunebot.conf", help="specify path for config file")
    args = parser.parse_args()
    daemon = Daemon(args.daemon, args.pidpath, args.logpath, args.confpath)
    daemon.start()

if __name__ == "__main__":
    main()
