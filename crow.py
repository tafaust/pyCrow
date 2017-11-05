#!/usr/bin/python
# -*- coding: utf-8 -*-

""" « pyCrow » entry point.
"""

# Python-native imports
import logging.config

# Third-party imports
import pykka

# App imports
from app import actor_get_or_create

# prepare logging, i.e. load config and get the root L
logging.config.fileConfig('./logging.conf')
L = logging.getLogger()
logging.getLogger('pykka').setLevel(logging.DEBUG)

if __name__ == '__main__':
    L.info('Starting...')

    ref: pykka.ActorRef = actor_get_or_create('AppActor')

    state = 'running' if ref.is_alive() else 'terminated'
    L.info(f'Finished standalone program. Actor App ({ref.actor_urn}) is «{state}».')
