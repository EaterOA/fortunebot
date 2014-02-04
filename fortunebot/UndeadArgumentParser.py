from argparse import ArgumentParser

class UndeadArgumentParser(ArgumentParser):

    def error(self, message):
        raise ValueError(message)
