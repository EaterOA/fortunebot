#! /usr/bin/env python

from threading import Timer
from subprocess import Popen, PIPE, STDOUT
import sys
import re

def pkill(p):
    if p.poll() == None:
        try:
            p.kill()
        except:
            pass

def getFortune(category): 
    cmd = ["fortune", "-sn", "100"]
    if category:
        #Sanitize
        category = category.split()[0]
        category = "".join([c for c in category if c.isalnum()])
        cmd.append(category)
    proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
    timeout = Timer(0.5, pkill, [proc])
    timeout.start()
    res, err = proc.communicate()
    timeout.cancel()
    if not res:
        res = "ERROR: Fortune not found" 
    else:
        res = res.strip()
        res = re.sub(r"[ \t\r\n]+", " ", res)
    return res

def main():
    category = None
    if len(sys.argv) > 1:
        category = sys.argv[1] 
    fortune = getFortune(category)
    print fortune

if __name__ == "__main__":
    main()

