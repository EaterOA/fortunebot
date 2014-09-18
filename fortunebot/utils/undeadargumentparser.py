"""
undeadargumentparser.py

A subclass of argparse.ArgumentParser that isn't hellbent on
exiting just because of a parsing error
"""

import argparse

class UndeadArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise argparse.ArgumentError(None, message)
