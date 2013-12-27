#! /usr/bin/env python

import urllib
import json
import sys

def getWeather(zipcode):
    rdata = {}
    if len(zipcode) != 5 or not zipcode.isdigit():
        rdata["error"] = "Zip code is not in 5-digit format!"
    else:
        try:
            page = urllib.urlopen("http://api.worldweatheronline.com/free/v1/weather.ashx?q=%s&format=json&fx=no&includelocation=yes&key=YOURKEYHERE" % zipcode).read()
            wdata = json.loads(page)["data"]
            if "error" in wdata:
                rdata["error"] = "No data found for %s!" % zipcode
            else:
                area = wdata['nearest_area'][0]
                weather = wdata['current_condition'][0]
                rdata["city"] = area['areaName'][0]['value']
                rdata["state"] = area['region'][0]['value']
                rdata["tempF"] = weather['temp_F']
                rdata["tempC"] = weather['temp_C']
                rdata["desc"] = weather['weatherDesc'][0]['value']
                rdata["humidity"] = weather['humidity']
        except IOError:
            rdata["error"] = "Unable to connect to weather API!"

    return rdata

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: weather.py <zip code>\n")
    else:
        data = getWeather(sys.argv[1])
        if "error" in data:
            sys.stderr.write("%s\n" % data["error"])
        else:
            print data

if __name__ == "__main__":
    main()
