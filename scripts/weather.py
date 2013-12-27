#! /usr/bin/env python

import weechat
import urllib
import json

SCRIPT_NAME = "weather"
SCRIPT_AUTHOR = "Eater"
SCRIPT_VERSION = "0.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Check weather"

def weather_cb(data, signal, signal_data):
    server = signal.split(',')[0]
    channel = signal_data.split()[2]
    buff = weechat.info_get("irc_buffer", "%s,%s" % (server, channel))
    msg = signal_data.split(':')[2]
    argv = msg.split()
    if channel[0] == '#' and argv[0] == "!w":
        if len(argv[1]) == 5 and argv[1].isdigit():
            try:
                page = urllib.urlopen("http://api.worldweatheronline.com/free/v1/weather.ashx?q=%s&format=json&fx=no&includelocation=yes&key=YOURKEYHERE" % argv[1]).read()
                wdata = json.loads(page)['data']
                if 'error' in wdata:
                    weechat.command(buff, "ERROR: No data on %s!" % argv[1])
                else:
                    area = wdata['nearest_area'][0]
                    weather = wdata['current_condition'][0]
                    city = area['areaName'][0]['value']
                    state = area['region'][0]['value']
                    tempF = weather['temp_F']
                    tempC = weather['temp_C']
                    desc = weather['weatherDesc'][0]['value']
                    humidity = weather['humidity']
                    weechat.command(buff, "%s, %s: %s. %s F / %s C, humidity %s%%" % (city, state, desc, tempF, tempC, humidity))
            except IOError:
                weechat.command(buff, "ERROR: Cannot access weather API!")
        else:
            weechat.command(buff, "ERROR: !w <zip code>")
    return weechat.WEECHAT_RC_OK

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
    weechat.hook_signal("*,irc_in_privmsg", "weather_cb", "")

