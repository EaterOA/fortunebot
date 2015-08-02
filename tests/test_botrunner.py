import os

from fortunebot import botrunner

class TestFortunebotRunner():

    RELATIVE_FILE = "sup.txt"
    ABSOLUTE_FILE = "/sup.txt"

    def setup(self):
        default_args = get_default_args()
        self.runner = botrunner.FortunebotRunner(**default_args)

    def test_resolved_relative(self):
        s = self.runner.resolved(self.RELATIVE_FILE)
        assert s == os.path.abspath(self.RELATIVE_FILE)

    def test_resolved_absolute(self):
        s = self.runner.resolved(self.ABSOLUTE_FILE)
        assert s == self.ABSOLUTE_FILE

def get_default_args():
    return {
        'daemonize': False,
        'confpath': 'fortunebot.conf',
        'logpath': 'fortunebot.log',
        'pidpath': 'fortunebot.pid',
        'workpath': '.',
    }

def test_parse_args():
    args = botrunner.parse_args([])
    default_args = get_default_args()
    for k, v in default_args.items():
        assert getattr(args, k) == v

