"""
easyconfigparser.py

A subclass of ConfigParser.RawConfigParser that provides less annoying
management of sections
"""

import ConfigParser
from six.moves import configparser

class EasyConfigParser(configparser.RawConfigParser):

    def __init__(self, defaults=None, sections=None):

        # I deliberately avoided defaults={} and sections=[]
        # Mutable default arguments (dict and list) are dangerous
        if defaults is None:
            defaults = {}
        if sections is None:
            sections = []

        configparser.RawConfigParser.__init__(self, defaults)
        for s in sections:
            self.add_section(s)

    def defaultable(f):
        def wrapper(self, section, option, default=None):
            try:
                return f(self, section, option)
            except:
                if default == None:
                    raise
                else:
                    return default
        return wrapper    

    @defaultable
    def get(self, section, option):
        return configparser.RawConfigParser.get(self, section, option)

    @defaultable
    def getboolean(self, section, option):
        return configparser.RawConfigParser.getboolean(self, section, option)

    @defaultable
    def getint(self, section, option):
        return configparser.RawConfigParser.getint(self, section, option)

    @defaultable
    def getfloat(self, section, option):
        return configparser.RawConfigParser.getfloat(self, section, option)
