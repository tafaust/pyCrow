#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from pyCrow.audiolib.record import VoiceRecorder

__all__ = [
    VoiceRecorder
]

L = logging.getLogger(__name__)
L.info('Loaded lib: {}.'.format(__name__))
