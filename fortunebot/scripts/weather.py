# -*- coding: utf-8 -*-

import urllib
import json

class Weather():

    def __init__(self, apikey):
        if not apikey:
            self.key = ""
        else:
            #Sanitize, because I can
            self.key = "".join([c for c in apikey.split()[0] if c.isalnum()])

    def on_pubmsg(self, nick, channel, text):
        args = text.split()
        if args[0] != "!w":
            return
        zipcode = args[1] if len(args) > 1 else "90024"
        return self.getWeather(zipcode)


    def getWeather(self, zipcode):
        res = ""
        if len(zipcode) != 5 or not zipcode.isdigit():
            res = "ERROR: Zip code is not in 5-digit format!"
        else:
            try:
                page = urllib.urlopen("http://api.worldweatheronline.com/free/v1/weather.ashx?q={0}&format=json&fx=no&includelocation=yes&key={1}".format(zipcode, self.key)).read()
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
                res = "ERROR: Unable to connect to weather API!"

        return res

