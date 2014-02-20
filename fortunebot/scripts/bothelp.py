# -*- coding: utf-8 -*-

class BotHelp():

    def __init__(self):
        pass

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if not args or args[0] != "!help":
            return
        return self.getHelp(None if len(args) == 1 else args[1])

    def getHelp(self, script): 
        msg = ""
        if not script:
            msg = "Commands: !insult, !weather, !8ball, !fortune, !remind, !replace"
        elif script == "insult":
            msg = "!insult - Insults you elegantly"
        elif script == "weather":
            msg = "!w [zip code] - Provides weather information about the "\
                  "location specified by the zip code. Default 90024"
        elif script == "8ball":
            msg = "!8ball - Seek answer from the magic 8-ball"
        elif script == "fortune":
            msg = "!fortune [category] - Receive a fortune cookie from an "\
                  "optional category"
        elif script == "markov":
            msg = "Call fortunebot's name, and it shall respond"
        elif script == "remind":
            msg = "!remind [-m|-h|-d] <time> <target> <message> - Notify "\
                  "target with message after a certain time. -m, -h, or "\
                  "-d specifies that the time is in minutes, hours, or days"
        elif script == "replace":
            msg = "!replace <pattern> <replacement> - Replace pattern from "\
                  "your previous message with replacement. Also triggered by "\
                  "s/<pattern>/<replacement>"
        else:
            msg = "ERROR: Unrecognized command name!"
        return msg

