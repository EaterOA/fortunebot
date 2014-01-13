#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
import sys

def getWeather(zipcode, apikey="YOURKEYHERE"):
    res = ""
    if len(zipcode) != 5 or not zipcode.isdigit():
        res = "ERROR: Zip code is not in 5-digit format!"
    else:
        try:
            page = urllib.urlopen("http://api.worldweatheronline.com/free/v1/weather.ashx?q={0}&format=json&fx=no&includelocation=yes&key={1}".format(zipcode, apikey)).read()
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
                res = u"{0}, {1}: {2}. {3}°F ({4}°C). Humidity: {5}%.".format(city, state, desc, tempF, tempC, humidity)
        except (IOError, ValueError):
            res = "ERROR: Unable to connect to weather API!"

    return res

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: weather.py <zip code>\n")
    else:
        res = getWeather(sys.argv[1])
        print res

if __name__ == "__main__":
    main()
