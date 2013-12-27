#! /usr/bin/env python

import weechat
import urllib
import re

SCRIPT_NAME = "insult"
SCRIPT_AUTHOR = "Eater"
SCRIPT_VERSION = "0.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Insult elegantly"

def insult_cb(data, signal, signal_data):
    server = signal.split(',')[0]
    channel = signal_data.split()[2]
    buff = weechat.info_get("irc_buffer", "%s,%s" % (server, channel))
    msg = signal_data.split(':')[2]
    args = msg.split()
    if channel[0] == '#' and args[0] == "!insult":
        try:
            page = urllib.urlopen("http://www.pangloss.com/seidel/Shaker/index.html").read()
            match = re.search("^.+?</font>$", page, re.M)
            insult = match.group(0).split('<')[0]
            weechat.command(buff, insult)
        except IOError:
            weechat.command(buff, "ERROR: Cannot access insultbase!")

    return weechat.WEECHAT_RC_OK

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
    weechat.hook_signal("*,irc_in_privmsg", "insult_cb", "")


