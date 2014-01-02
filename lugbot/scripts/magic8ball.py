#! /usr/bin/env python

import sys
from random import choice

def get8Ball(): 
    roll = ["It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"]
    res = choice(roll)
    return res

def main():
    msg = get8Ball()
    print msg

if __name__ == "__main__":
    main()

