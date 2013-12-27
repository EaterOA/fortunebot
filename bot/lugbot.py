#! /usr/bin/env python

"""
Very simple skeleton lugbot based off of irclib's testbot

Run using:
python lugbot.py <server[:port]> <channel> <nickname>

The known commands are:

    !stats -- Prints some channel information
    !die -- Commit roboticide

"""

import irc.bot

class LugBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        text = e.arguments[0].split()
        if text and text[0][0] == "!":
            self.do_command(e, text[0], text[1:])

    def do_command(self, e, cmd, args):
        nick = e.source.nick
        c = self.connection

        if cmd == "!die":
            self.die()
        elif cmd == "!stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.notice(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.notice(nick, "Voiced: " + ", ".join(voiced))

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: lugbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = LugBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
