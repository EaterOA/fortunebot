"""
A subclass of ConfigParser.RawConfigParser that provides less annoying
management of sections
"""

import ConfigParser

class EasyConfigParser(ConfigParser.RawConfigParser):

    def __init__(self, defaultDict, defaultSections=[]):
        ConfigParser.RawConfigParser.__init__(self, defaultDict)
        for s in defaultSections:
            self.add_section(s)

