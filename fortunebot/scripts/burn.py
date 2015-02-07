# -*- coding: utf-8 -*-

"""
burn.py
"""

import random

class Burn(object):

    NAME = "burn"
    PARAMS = [("str", "words")]
    HELP = "Burn"

    def __init__(self, words):
        self.words = words.split()

    def on_pubmsg(self, source, channel, text):
        text = text.lower()
        for w in self.words:
            d = text.find(w)
            if d == -1:
                return None
            text = text[d+1:]
        return self.get_burned()

    def get_burned(self):
        choices = [
            "TOLD",
            "TOLDASAURUS REX",
            "Cash4TOLD.com",
            "Knights of the TOLD Republic",
            "King TOLD the IV",
            "CounTOLD Strike",
            "Unreal TOLDament",
            "Rampage: TOLDal Destruction",
            "The Good, The Bad, and The TOLD",
            "Super TOLD Boy",
            "Left 4 TOLD",
            "TOLDman Sachs",
            "TOLD Fortress 2",
            "www.TOLD.com",
            "Tic-tac-TOLD",
            "TOLD of the Ring",
        ]
        return random.choice(choices)
