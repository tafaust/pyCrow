#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Auxiliary utilities for the pykka and pyCrow libraries.

Contains helper classes and functions for the pyCrow lib and utilities for the pykka library.
"""

# Python-native imports
import logging.config

# Third-party imports

# App imports

L = logging.getLogger(__name__)
L.debug(f'Loaded module: {__name__}.')


class Action(object):
    SERVER_STOP = {'cmd': 'server_stop'}
    SERVER_START = {'cmd': 'server_start'}
    SERVER_RESTART = {'cmd': 'server_restart'}

    CONFIG_REFRESH = {'cmd': 'config_refresh'}
    CONFIG_GET = {'cmd': 'config_get'}

    AUDIO_RECORD = {'cmd': 'audio_record'}
    AUDIO_RECORD_TO_FILE = {'cmd': 'audio_record_to_file'}
    AUDIO_PLAYBACK = {'cmd': 'audio_playback'}  # shall replay sound with the buffer delay

    """This action triggers an experiment to train or refine an existing model.
    
    Programmatically pre-hooked to this action is the recording and feature computation from 
    multiple trials.
    """
    MODEL_TRAIN = {'cmd': 'model_train'}
    """
    """
    MODEL_TEST = {'cmd': 'model_test'}

