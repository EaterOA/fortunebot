# -*- coding: utf-8 -*-

"""
markov.py

A script that listens to and records conversations in irc channels. When
somebody says a magic word, the script generates a markov chain response using
the recorded conversations as base.
"""

import random
from collections import Counter, deque

class Markov(object):

    NAME = "markov"
    PARAMS = [("str", "path"),
              ("bool", "listen"),
              ("bool", "record"),
              ("str", "respond")]
    HELP = "Call fortunebot's name, and it shall respond..."

    def __init__(self, path, listen, record, respond):
        self.listen = listen
        self.respond = respond
        self.table = [{}, {}, {}]
        self.sample_file = None
        if path:
            self.init_sample_file(path, record)
        self.end_mult = 20
        self.expand_limit = 50
        self.sentence_chance = 0.7
        self.chain_keyword_chance = 0.4

    def __del__(self):
        if self.sample_file:
            self.sample_file.close()
            self.sample_file = None

    def init_sample_file(self, path, record):
        if not record:
            self.sample_file = open(path)
        else:
            self.sample_file = open(path, "r+", 1) # r+w line buffered
        for line in self.sample_file:
            if self.respond not in line:
                self.add_line(line)
        if not record:
            self.sample_file.close()
            self.sample_file = None

    def on_pubmsg(self, source, channel, text):
        if not text.split():
            return
        if self.respond in text:
            return self.generate(text)
        elif self.listen:
            self.add_line(text)
            if self.sample_file:
                self.sample_file.write("{0}\n".format(text))

    def add_line(self, line):
        for triplet in self.triples(line):
            before = triplet[0]
            after = triplet[2]
            """
            0th order Markov chain
            Basically gives a random word
            """
            key0 = None
            if key0 not in self.table[0]:
                self.table[0][key0] = (Counter(), Counter())
            self.table[0][key0][0][before] += 1
            self.table[0][key0][1][after] += 1
            """
            1st order Markov chain
            Gives a word known to precede/succeed a base word
            """
            key1 = triplet[1]
            if key1 not in self.table[1]:
                self.table[1][key1] = (Counter(), Counter())
            self.table[1][key1][0][before] += 1
            self.table[1][key1][1][after] += 1
            """
            2nd order Markov chain
            Gives a word known to precede/succeed a word pair
            """
            key2a = (triplet[0], triplet[1])
            key2b = (triplet[1], triplet[2])
            if key2a not in self.table[2]:
                self.table[2][key2a] = (Counter(), Counter())
            if key2b not in self.table[2]:
                self.table[2][key2b] = (Counter(), Counter())
            self.table[2][key2b][0][before] += 1
            self.table[2][key2a][1][after] += 1

    @staticmethod
    def triples(line):
        if not line:
            return
        words = line.split()
        if not words:
            return
        words.insert(0, None)
        words.append(None)
        for i in range(1, len(words) - 1):
            yield (words[i-1], words[i], words[i+1])

    def filter_keywords(self, text):
        keywords = []
        for word in text.split():
            if word in self.table[1] and self.respond not in word:
                keywords.append(word)
        return keywords

    def get_word(self, base, keywords, prepend, order, end_mult):
        if order > 2:
            order = 2
        elif order < 1:
            order = 1
        if base not in self.table[order]:
            return None
        idx = 0 if prepend else 1
        c = self.table[order][base][idx]
        if len(c) == 1:
            return next(iter(c))
        if random.random() < self.chain_keyword_chance:
            chainables = [k for k in keywords if k in c]
            if chainables:
                res = random.choice(chainables)
                keywords.remove(res)
                return res
        end_chance = (c[None] * end_mult) / sum(c.values())
        if random.random() < end_chance:
            return None
        res = random.choice([w for w in c.elements() if w is not None])
        if res in keywords:
            keywords.remove(res)
        return res

    def generate_sentece(self, keywords):
        if not keywords:
            if not self.table[1]:
                return ""
            base = random.choice(list(self.table[1].keys()))
        else:
            base = random.choice(keywords)
            keywords.remove(base)
        sentence = deque([base])
        """
        Expand left
        """
        left = self.get_word(base, keywords, True, 1, 0)
        if left:
            sentence.appendleft(left)
            for mult in range(self.end_mult, 200, self.end_mult):
                pair = (sentence[0], sentence[1])
                left = self.get_word(pair, keywords, True, 2, mult/100.0)
                if not left:
                    break
                sentence.appendleft(left)
        """
        Expand right
        """
        right = self.get_word(base, keywords, False, 1, 0)
        if right:
            sentence.append(right)
            for mult in range(self.end_mult, 200, self.end_mult):
                pair = (sentence[-2], sentence[-1])
                right = self.get_word(pair, keywords, False, 2, mult/100.0)
                if not right:
                    break
                sentence.append(right)
        return ' '.join(sentence)

    def generate(self, text):
        keywords = self.filter_keywords(text)
        msg = ""
        msg += self.generate_sentece(keywords)
        while keywords and len(msg) < self.expand_limit and random.random() < self.sentence_chance:
            msg += '. '
            msg += self.generate_sentece(keywords)
        return msg

