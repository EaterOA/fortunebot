import os
import mock

from fortunebot import botrunner

MODULE = 'fortunebot.botrunner'

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

    @mock.patch(MODULE + '.os', autospec=True)
    def test_send_background(self, mock_os):
        self.runner.send_background()
        assert mock_os.fork.call_count == 2

    @mock.patch(MODULE + '.os', autospec=True)
    @mock.patch(MODULE + '.open')
    def test_redirect_IO(self, mock_open, mock_os):
        self.runner.redirect_IO()
        assert mock_os.close.call_count >= 3
        assert mock_open.call_count == 3

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

