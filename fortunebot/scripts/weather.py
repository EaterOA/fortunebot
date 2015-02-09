# -*- coding: utf-8 -*-

"""
weather.py

A script that tells the weather. Uses the World Weather Online API.
"""

import urllib
import json
import time
import shlex
from fortunebot.utils import UndeadArgumentParser
from argparse import ArgumentError

class Weather(object):

    NAME = "weather"
    PARAMS = [("str", "key"),
              ("int", "cachedur"),
              ("int", "setlimit")]
    HELP = "!w [zip code] - Provides weather information about the location "  \
           "specified by the zip code. Defaults to searching 90024 (LA)."

    def __init__(self, key, cachedur, setlimit):
        if not key:
            self.key = ""
        else:
            #Sanitize, because I can
            self.key = "".join([c for c in key.split()[0] if c.isalnum()])
        self.cachedur = cachedur
        self.setlimit = setlimit
        self.zipcache = {}
        self.hostcache = {}
        self.setcache = {}

    def on_pubmsg(self, source, channel, text):
        if not self.key:
            return None
        try:
            args = self.parse_args(text)
            if not args:
                return None
        except ArgumentError:
            return "Syntax: !w [-s <save_zipcode>] [query_zipcode]"
        set_zipcode = args.set_zipcode
        if set_zipcode:
            return self.setZip(source.nick, set_zipcode)
        zipcode = args.zipcode
        if not zipcode:
            if source.nick in self.setcache:
                zipcode = self.setcache[source.nick][1]
            elif source.host:
                zipcode = self.getZip(source.host)
            if not zipcode:
                return "Please specify zip"
        return self.getWeather(zipcode)

    def parse_args(self, text):
        args = text.split()
        if not args or args[0] not in ["!w", "!weather"]:
            return None
        sargs = shlex.split(" ".join(args[1:]))
        parser = UndeadArgumentParser(add_help=False)
        parser.add_argument("zipcode", nargs="?", default="")
        parser.add_argument("-s", "--set", default="", dest="set_zipcode")
        return parser.parse_args(sargs)

    def setZip(self, nick, zipcode):
        if self.setlimit == 0:
            return None
        if not self.validZip(zipcode):
            return "Zip code is not in 5-digit format!"
        if (nick not in self.setcache
                and self.setlimit <= len(self.setcache)):
            min_key = min(self.setcache, key=lambda k: self.setcache[k][0])
            del self.setcache[min_key]
        self.setcache[nick] = (int(time.time()), zipcode)

    def validZip(self, zipcode):
        return len(zipcode) == 5 and zipcode.isdigit()

    def getZip(self, host):
        if host in self.hostcache:
            return self.hostcache[host][1]
        url = "https://freegeoip.net/json/{0}".format(host)
        res = ""
        try:
            page = urllib.urlopen(url).read()
            data = json.loads(page)
            res = data["zip_code"]
        except (IOError, ValueError):
            pass
        self.hostcache[host] = (int(time.time()) + self.cachedur, res)
        return res

    def getWeather(self, zipcode):
        if not self.validZip(zipcode):
            return "Zip code is not in 5-digit format!"
        if zipcode in self.zipcache:
            return self.zipcache[zipcode][1]
        url = "http://api.worldweatheronline.com/free/v1/weather.ashx?q={0}&format=json&fx=no&includelocation=yes&key={1}".format(zipcode, self.key)
        res = ""
        try:
            page = urllib.urlopen(url).read()
            wdata = json.loads(page)["data"]
            if "error" in wdata:
                res = "No data found for {0}!".format(zipcode)
            else:
                area = wdata['nearest_area'][0]
                weather = wdata['current_condition'][0]
                city = area['areaName'][0]['value']
                state = area['region'][0]['value']
                tempF = weather['temp_F']
                tempC = weather['temp_C']
                desc = weather['weatherDesc'][0]['value']
                humidity = weather['humidity']
                res = u"{0}, {1}: {2}. {3}°F ({4}°C). Humidity: {5}%.".format(city, state, desc, tempF, tempC, humidity).encode("utf-8")
        except (IOError, ValueError):
            # Don't cache connection failures
            return "Unable to connect to weather API!"
        self.zipcache[zipcode] = (int(time.time()) + self.cachedur, res)
        return res

    def on_poll(self, channel):
        self.prune(self.zipcache)
        self.prune(self.hostcache)

    def prune(self, cache):
        cur = int(time.time())
        toggle_list = []
        for k, v in cache.items():
            if cur >= v[0]:
                toggle_list.append(k)
        for k in toggle_list:
            del cache[k]
