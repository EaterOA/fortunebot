#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convenience script to copy the packaged config file into a standard config
directory for fortunebot

Hooked by setuptools into `fortunebot-generate-config`
"""

from __future__ import print_function
import sys
import os
import shutil
from pkg_resources import resource_filename
from appdirs import user_config_dir

APP = "fortunebot"
CONFIG_SRC_NAME = "config/fortunebot.conf.example"
CONFIG_NAME = "fortunebot.conf"

def main():

    src_file = resource_filename(APP, CONFIG_SRC_NAME)
    dest_dir = user_config_dir(APP)
    dest_file = os.path.join(dest_dir, CONFIG_NAME)
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir, 0700)
        except OSError as e:
            error_exit(e)
    try:
        shutil.copyfile(src_file, dest_file)
    except IOError as e:
        error_exit(e)
    print("Created config file in {}".format(dest_file))

def error_exit(e):
    print(e, file=sys.stderr)
    sys.exit(1)
