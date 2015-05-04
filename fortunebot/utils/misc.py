"""
misc.py

Contains miscellaneous utility functions for string manipulation, etc
"""

import six

def to_unicode(s):
    if isinstance(s, six.binary_type):
        s = s.decode('utf-8')
    return s

def strip_unprintable(s):
    illegal = {i: None for i in six.moves.xrange(32)}
    return s.translate(illegal)
