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
        if self.limit == 0:
            return
        curtime = int(time.time())
        if key in self.store:
            del self[key]
        if self.limit > 0 and len(self.store) >= self.limit:
            del self[self.timestore[0][0]]
        self.store[key] = val
        self.timestore.append((key, curtime))

    def __delitem__(self, key):
        del self.store[key]
        for i, v in enumerate(self.timestore):
            if key == v[0]:
                del self.timestore[i]
                break

    def prune(self, dur=None):
        if dur == None:
            dur = self.duration
        curtime = int(time.time())
        ret = {}
        while self.timestore and self.timestore[0][1] + dur <= curtime:
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
