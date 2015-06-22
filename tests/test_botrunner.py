import unittest
from fortunebot import botrunner

class TestFortunebotRunner(unittest.TestCase):
    pass

def test_parse_args():
    # defaults
    args = botrunner.parse_args([])
    assert not args.daemonize
    assert args.confpath == 'fortunebot.conf'
    assert args.logpath == 'fortunebot.log'
    assert args.pidpath == 'fortunebot.pid'
    assert args.workpath == '.'

