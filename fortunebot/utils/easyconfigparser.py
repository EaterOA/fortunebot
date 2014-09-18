"""
A subclass of ConfigParser.RawConfigParser that provides less annoying
management of sections
"""

import ConfigParser

class EasyConfigParser(ConfigParser.RawConfigParser):

    def __init__(self, defaults={}, sections=[]):
        ConfigParser.RawConfigParser.__init__(self, defaults)
        for s in sections:
            self.add_section(s)

