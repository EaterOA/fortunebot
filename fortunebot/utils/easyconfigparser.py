"""
easyconfigparser.py

A subclass of ConfigParser.RawConfigParser that provides less annoying
management of sections
"""

import ConfigParser

class EasyConfigParser(ConfigParser.RawConfigParser):

    def __init__(self, defaults=None, sections=None):

        # I deliberately avoided defaults={} and sections=[]
        # Mutable default arguments (dict and list) are dangerous
        if defaults is None:
            defaults = {}
        if sections is None:
            sections = []

        ConfigParser.RawConfigParser.__init__(self, defaults)
        for s in sections:
            self.add_section(s)

