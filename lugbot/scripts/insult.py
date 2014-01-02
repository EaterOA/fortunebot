#! /usr/bin/env python

import sys
import urllib
import re

def getInsult(): 
    insult = ""
    try:
        page = urllib.urlopen("http://www.pangloss.com/seidel/Shaker/index.html").read()
        match = re.search("^.+?</font>$", page, re.M)
        insult = match.group(0).split('<')[0]
    except IOError:
        insult = "ERROR: Unable to retrieve insult"
    return insult

def main():
    insult = getInsult()
    print insult

if __name__ == "__main__":
    main()

