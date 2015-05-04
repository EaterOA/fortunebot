"""
easyconfigparser.py

A subclass of ConfigParser.ConfigParser that provides less annoying declaration
of sections and a py2/3 compatible way of specifying fallback values.
"""

from six.moves import configparser

def defaultable(f):
    def wrapper(self, *args, **kwargs):
        fallback = kwargs.pop('fallback', None)
        try:
            return f(self, *args, **kwargs)
        except:
            if fallback is None:
                raise
            else:
                return fallback
    return wrapper

class EasyConfigParser(configparser.ConfigParser):

    def __init__(self, *args, **kwargs):
        sections = kwargs.pop('sections', [])
        configparser.ConfigParser.__init__(self, *args, **kwargs)
        for s in sections:
            self.add_section(s)

    @defaultable
    def get(self, *args, **kwargs):
        return configparser.ConfigParser.get(self, *args, **kwargs)

    @defaultable
    def getboolean(self, *args, **kwargs):
        return configparser.ConfigParser.getboolean(self, *args, **kwargs)

    @defaultable
    def getint(self, *args, **kwargs):
        return configparser.ConfigParser.getint(self, *args, **kwargs)

    @defaultable
    def getfloat(self, *args, **kwargs):
        return configparser.ConfigParser.getfloat(self, *args, **kwargs)
