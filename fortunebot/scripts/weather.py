# -*- coding: utf-8 -*-

"""
weather.py

A script that tells the weather. Uses the World Weather Online API.
"""

import urllib
import json
import time

class Weather(object):

    NAME = "weather"
    PARAMS = [("str", "key"),
              ("int", "cachedur")]
    HELP = "!w [zip code] - Provides weather information about the location "  \
           "specified by the zip code. Defaults to searching 90024 (LA)."

    def __init__(self, key, cachedur):
        if not key:
            self.key = ""
        else:
            #Sanitize, because I can
            self.key = "".join([c for c in key.split()[0] if c.isalnum()])
        self.cachedur = cachedur
        self.zipcache = {}
        self.hostcache = {}

    def prune(self, cache):
        cur = int(time.time())
        toggle_list = []
        for k, v in cache.items():
            if cur >= v[0]:
                toggle_list.append(k)
        for k in toggle_list:
            del cache[k]

    def on_poll(self, channel):
        self.prune(self.zipcache)
        self.prune(self.hostcache)

    def on_pubmsg(self, source, channel, text):
        if not self.key:
            return
        args = text.split()
        if not args or args[0] not in ["!w", "!weather"]:
            return
        if len(args) > 1:
            zipcode = args[1]
        else:
            zipcode = self.getZip(source.host)
            if not zipcode:
                return "ERROR: Unable to geolocate host; please specify zip"
        return self.getWeather(zipcode)

    def getZip(self, host):
        if not host:
            return ""
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
        if len(zipcode) != 5 or not zipcode.isdigit():
            return "ERROR: Zip code is not in 5-digit format!"
        if zipcode in self.zipcache:
            return self.zipcache[zipcode][1]
        url = "http://api.worldweatheronline.com/free/v1/weather.ashx?q={0}&format=json&fx=no&includelocation=yes&key={1}".format(zipcode, self.key)
        res = ""
        try:
            page = urllib.urlopen(url).read()
            wdata = json.loads(page)["data"]
            if "error" in wdata:
                res = "ERROR: No data found for {0}!".format(zipcode)
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
            return "ERROR: Unable to connect to weather API!"
        self.zipcache[zipcode] = (int(time.time()) + self.cachedur, res)
        return res
