# -*- coding: utf-8 -*-

import random
from collections import Counter, deque

class Markov():
    
    def __init__(self, path, listen, magicWord):
        self.listen = listen
        self.magicWord = magicWord
        self.table = [{}, {}, {}]
        self._initTable(path)
        self.endMult = 20
        self.expandLimit = 50
        self.sentenceChance = 0.7
        self.chainKeywordChance = 0.4

    def on_pubmsg(self, nick, channel, text):
        if not text.split():
            return
        if self.listen:
            self._addLine(text)
        if self.magicWord in text:
            return self.generate(text)

    def _addLine(self, line):
        for triplet in self._triples(line):
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
           
    def _initTable(self, path):
        try:
            f = open(path)
        except IOError as e:
            return
        data = f.read()
        lines = data.split('\n')
        for line in lines:
            self._addLine(line)
        
    def _triples(self, line):
        if not line:
            return
        words = line.split()
        if not words:
            return
        words.insert(0, None)
        words.append(None)
        for i in range(1, len(words) - 1):
            yield (words[i-1], words[i], words[i+1])

    def _filterKeywords(self, text):
        keywords = []
        for word in text.split():
            if word in self.table[1] and word != self.magicWord:
                keywords.append(word)
        return keywords

    def getWord(self, base, keywords, prepend, order, endMult):
        if order > 2:
            order = 2
        elif order < 1:
            order = 1
        if base not in self.table[order]:
            return None
        idx = 0 if prepend else 1
        c = self.table[order][base][idx]
        if len(c) == 1:
            return c.keys()[0]
        if random.random() < self.chainKeywordChance:
            chainableKeywords = [k for k in keywords if k in c]
            if chainableKeywords:
                res = random.choice(chainableKeywords)
                keywords.remove(res)
                return res 
        endChance = (c[None] * endMult) / sum(c.values())
        if random.random() < endChance:
            return None
        res = random.choice([w for w in c.elements() if w is not None])
        if res in keywords:
            keywords.remove(res)
        return res

    def generateSentence(self, keywords):
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
        left = self.getWord(base, keywords, True, 1, 0)
        if left: 
            sentence.appendleft(left)
            for mult in range(self.endMult, 200, self.endMult):
                pair = (sentence[0], sentence[1])
                left = self.getWord(pair, keywords, True, 2, mult/100.0)
                if not left:
                    break
                sentence.appendleft(left)
        """
        Expand right
        """
        right = self.getWord(base, keywords, False, 1, 0)
        if right:
            sentence.append(right)
            for mult in range(self.endMult, 200, self.endMult):
                pair = (sentence[-2], sentence[-1])
                right = self.getWord(pair, keywords, False, 2, mult/100.0)
                if not right:
                    break
                sentence.append(right)
        return ' '.join(sentence)

    def generate(self, text):
        keywords = self._filterKeywords(text)
        msg = ""
        msg += self.generateSentence(keywords)
        while keywords and len(msg) < self.expandLimit and random.random() < self.sentenceChance:
            msg += '. '
            msg += self.generateSentence(keywords)
        return msg 
            
