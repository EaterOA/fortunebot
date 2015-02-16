"""
cachedict.py

A special class of dict that tracks the time at which items are inserted. Can
optionally limit the size of the dictionary, in which case the oldest item will
be pushed out in a least-recently-set fashion. Finally, CacheDict can also
prune items according to how long they've been in the dict.

CacheDict uses a regular dict to store mappings, and additionally a deque to
store the timestamps of insertions. This deque maintains a sorted order.
Inserting a new item is O(1)
Pruning/popping is O(1)
Deleting a specific item is O(n)
Inserting an item with a specified offset is O(n)
"""

import collections
import time

class CacheDict(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.timestore = collections.deque()
        self.limit = -1
        self.duration = 0
        if "limit" in kwargs:
            self.limit = int(kwargs["limit"])
            del kwargs["limit"]
        if "duration" in kwargs:
            self.duration = int(kwargs["duration"])
            del kwargs["duration"]
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, val):
        self.insert(key, val)

    def insert(self, key, val, offset=None):
        now = int(time.time())
        if key in self.store:
            del self[key]
        if offset == None:
            self.timestore.append((key, now))
        else:
            found = False
            for i, ele in enumerate(self.timestore):
                if ele[1] > now + offset:
                    found = True
                    self.timestore.rotate(-i)
                    self.timestore.appendleft((key, now + offset))
                    self.timestore.rotate(i)
                    break
            if not found:
                self.timestore.append((key, now + offset))
        self.store[key] = val
        if self.limit >= 0 and len(self.store) > self.limit:
            del self[self.timestore[0][0]]

    def __delitem__(self, key):
        del self.store[key]
        for i, v in enumerate(self.timestore):
            if key == v[0]:
                del self.timestore[i]
                break

    def prune(self, dur=None):
        if dur == None:
            dur = self.duration
        now = int(time.time())
        ret = {}
        while self.timestore and self.timestore[0][1] + dur <= now:
            k, _ = self.timestore.popleft()
            ret[k] = self.store[k]
            del self.store[k]
        return ret

    def times(self):
        return {k: t for k, t in self.timestore}

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)
