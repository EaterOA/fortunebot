# -*- coding: utf-8 -*-

"""
weather.py

A script that tells the weather. Uses the World Weather Online API.
"""

import urllib
import json
import shlex
from fortunebot.utils import UndeadArgumentParser, CacheDict
from argparse import ArgumentError

class Weather(object):

    NAME = "weather"
    PARAMS = [("str", "key"),
              ("int", "cachedur"),
              ("int", "setlimit")]
    HELP = "!w [-s <save_zipcode>] [query_zipcode] - Provides weather " \
           "information about the location specified by query_zipcode. If " \
           "unspecified, will attempt to geolocate user. Can also save a " \
           "zipcode using the -s switch."

    def __init__(self, key, cachedur, setlimit):
        if not key:
            self.key = ""
        else:
            #Sanitize, because I can
            self.key = "".join([c for c in key.split()[0] if c.isalnum()])
        self.zipcache = CacheDict(duration=cachedur)
        self.hostcache = CacheDict(duration=cachedur)
        self.setcache = CacheDict(limit=setlimit)

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
            return self.set_zip(source.nick, set_zipcode)
        zipcode = args.zipcode
        if not zipcode:
            if source.nick in self.setcache:
                zipcode = self.setcache[source.nick]
            elif source.host:
                zipcode = self.get_zip(source.host)
            if not zipcode:
                return "Please specify zip"
        return self.get_weather(zipcode)

    def parse_args(self, text):
        args = text.split()
        if not args or args[0] not in ["!w", "!weather"]:
            return None
        sargs = shlex.split(" ".join(args[1:]))
        parser = UndeadArgumentParser(add_help=False)
        parser.add_argument("zipcode", nargs="?", default="")
        parser.add_argument("-s", "--set", default="", dest="set_zipcode")
        return parser.parse_args(sargs)

    def set_zip(self, nick, zipcode):
        if not self.valid_zip(zipcode):
            return "Zip code is not in 5-digit format!"
        self.setcache[nick] = zipcode

    def valid_zip(self, zipcode):
        return len(zipcode) == 5 and zipcode.isdigit()

    def get_zip(self, host):
        if host in self.hostcache:
            return self.hostcache[host]
        url = "https://freegeoip.net/json/{0}".format(host)
        res = ""
        try:
            page = urllib.urlopen(url).read()
            data = json.loads(page)
            res = data["zip_code"]
        except (IOError, ValueError):
            pass
        self.hostcache[host] = res
        return res

    def get_weather(self, zipcode):
        if not self.valid_zip(zipcode):
            return "Zip code is not in 5-digit format!"
        if zipcode in self.zipcache:
            return self.zipcache[zipcode]
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
        self.zipcache[zipcode] = res
        return res

    def on_poll(self, channel):
        self.zipcache.prune()
        self.hostcache.prune()
