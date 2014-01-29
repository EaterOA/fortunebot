"""
Simple subclass of RawConfigParser to provide less annoying
management of sections
"""

from ConfigParser import RawConfigParser

class EasyConfigParser(RawConfigParser):

    def __init__(self, defaultDict, defaultSections=[]):
        RawConfigParser.__init__(self)
        for s in defaultSections:
            self.add_section(s)

