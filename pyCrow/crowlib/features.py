#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides distinct types of features given a pipeline module.
"""

# Python-native imports
import logging.config

# Third-party imports
import pykka

# App imports

# prepare logging, i.e. load config and get the root L
L = logging.getLogger(__name__)


class FeatureActor(pykka.ThreadingActor):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config

    def on_start(self):
        L.info(msg=f'Started FeatureActor ({self.actor_urn})')

    def on_stop(self):
        L.info('FeatureActor is stopped.')

    def on_failure(self, exception_type, exception_value, traceback):
        L.error(f'FeatureActor failed: {exception_type} {exception_value} {traceback}')

    def on_receive(self, msg: dict) -> None:
        L.info(msg=f'FeatureActor received message: {msg}')
        # process msg and alter state accordingly
        _cmd = msg.get('cmd', '').lower()
        # introduce actions to modify this actors state

    def compute_mfcc_features(self):
        # TODO come up with a feature concept
        pass  # TODO


class _MFCC_Features(object):
    pass
