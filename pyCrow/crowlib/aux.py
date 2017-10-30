#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Auxiliary utilities for the pykka and pyCrow libraries.

Contains helper classes and functions for the pyCrow lib and utilities for the pykka library.
"""

# Python-native imports

# Third-party imports


class Action(object):
    SERVER_STOP = {'cmd': 'server_stop'}
    SERVER_START = {'cmd': 'server_start'}
    SERVER_RESTART = {'cmd': 'server_restart'}

    CONFIG_REFRESH = {'cmd': 'config_refresh'}
    CONFIG_GET = {'cmd': 'config_get'}

    RECORD_AUDIO = {'cmd': 'record_audio'}

