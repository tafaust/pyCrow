#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Entry point for the pulsar-queue application.

Contains the pulsar-queue object instantiation and configuration.
"""

import json
# Python-native imports
import logging.config
import typing

# Third-party imports
import pykka

from pyCrow.audiolib import VoiceRecorder
# App imports
from pyCrow.crowlib import Action
from pyCrow.crowlib.rest import RestActor

# prepare logging, i.e. load config and get the root L
L = logging.getLogger()


class AppActor(pykka.ThreadingActor):
    """ Build Pykka App actor parent to all other actors.
    """

    def __init__(self):
        super(AppActor, self).__init__()
        # todo set default configuration
        self._config = {}

    def on_start(self):
        # load config for this application
        self._refresh_config()

        # create REST Actor
        try:
            ref: pykka.ActorRef = RestActor.start(config=self._config.get('server', {}))
            assert ref is not None
        except AssertionError:
            L.error(msg='Unable to start the REST Actor.')
        except pykka.ActorDeadError as ade:
            L.warning(msg=f'Message received for dead REST Actor: {ade}')

    def on_stop(self):
        L.debug('AppActor is stopped.')

    def on_failure(self, exception_type, exception_value, traceback):
        L.error(f'AppActor failed: {exception_type} {exception_value} {traceback}')

    def on_receive(self, msg: dict):
        L.info(msg=f'AppActor received message: {msg}')
        # process msg and interact with sub-actors accordingly

        _cmd = msg.get('cmd', '').lower()
        if _cmd == Action.CONFIG_REFRESH.get('cmd'):
            self._refresh_config()
        elif _cmd == Action.CONFIG_GET.get('cmd'):
            return self._config
        elif _cmd == Action.RECORD_AUDIO.get('cmd'):
            _duration: int = self._config.get('record', {}).get('duration', 0)
            vr: VoiceRecorder = VoiceRecorder()
            vr.record_to_file('./resources/demo.wav', seconds=_duration)

        elif _cmd in [Action.SERVER_START.get('cmd'), Action.SERVER_RESTART.get('cmd'),
                      Action.SERVER_STOP.get('cmd')]:
            pykka.ActorRegistry.broadcast(message=msg, target_class=RestActor)

        else:
            # default: do nothing but log this event
            L.info(msg=f'Received message {msg} which cannot be processed.')

    def _refresh_config(self, config_file='config.json'):
        with open(config_file, 'r') as json_data_file:
            self._config = json.load(json_data_file)
            # todo validate config... at some point
            L.info(f'Refreshing configuration:\n{self._config}')
