#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python-native imports
import logging

# Third-party imports

# App imports
from pyCrow.audiolib.record import VoiceRecorder


# prepare logging, i.e. load config and get the root L
L = logging.getLogger(__name__)
L.info(f'Loaded lib: {__name__}.')



__all__ = [
    VoiceRecorder.__name__,
]
