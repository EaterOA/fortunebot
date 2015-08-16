#! /usr/bin/env python
# -*- coding: utf-8 -*-

import six
import mock

import irc
from fortunebot import bot

MODULE = 'fortunebot.botrunner'

EXAMPLE_CHANNEL = "#test"
EXAMPLE_NICK = "fortunebot"
EXAMPLE_MSG = "abcdefg"
EXAMPLE_MSG2 = "星空"
EXAMPLE_SCRIPT_RETURN = EXAMPLE_MSG2

class TestFortunebot(object):

    def setup(self):
        self.bot = bot.Fortunebot()
        self.bot.connection = mock.create_autospec(irc.client.ServerConnection)
        mock_script = mock.create_autospec(MockScript)
        mock_script.on_pubmsg.return_value = EXAMPLE_SCRIPT_RETURN
        self.bot.scripts = {"mock_script": mock_script}

    def test_send_msg(self):
        self.bot.send_msg(EXAMPLE_CHANNEL, EXAMPLE_MSG)
        self.bot.connection.privmsg.assert_called_with(
            EXAMPLE_CHANNEL,
            to_unicode(EXAMPLE_MSG))

        self.bot.send_msg(EXAMPLE_CHANNEL, EXAMPLE_MSG2)
        self.bot.connection.privmsg.assert_called_with(
            EXAMPLE_CHANNEL,
            to_unicode(EXAMPLE_MSG2))

    def test_send_msg_multiple(self):
        messages = [EXAMPLE_MSG + str(i) for i in six.moves.xrange(10)]
        self.bot.send_msg(EXAMPLE_CHANNEL, messages)
        assert self.bot.connection.privmsg.call_count == len(messages)

    def test_send_msg_illegal(self):
        msg = "\r\n"
        self.bot.send_msg(EXAMPLE_CHANNEL, msg)
        self.bot.connection.privmsg.assert_called_with(
            EXAMPLE_CHANNEL,
            "")

        msg = "\t\x7F"
        self.bot.send_msg(EXAMPLE_CHANNEL, msg)
        self.bot.connection.privmsg.assert_called_with(
            EXAMPLE_CHANNEL,
            "")

    def test_on_pubmsg(self):
        e = irc.client.Event("", EXAMPLE_NICK, EXAMPLE_CHANNEL, [EXAMPLE_MSG])
        self.bot.on_pubmsg(self.bot.connection, e)

        self.bot.scripts["mock_script"].on_pubmsg.assert_called_with(
            EXAMPLE_NICK,
            EXAMPLE_CHANNEL,
            EXAMPLE_MSG)
        self.bot.connection.privmsg.assert_called_with(
            EXAMPLE_CHANNEL,
            to_unicode(EXAMPLE_SCRIPT_RETURN))

class MockScript(object):
    def on_pubmsg(self, source, channel, text):
        pass

def to_unicode(s):
    return s if six.PY3 else s.decode('utf-8')
