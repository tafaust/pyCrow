#!/usr/bin/python
# -*- coding: utf-8 -*-

""" « pyCrow » entry point.
"""

# Python-native imports
import logging.config

# Third-party imports
import pykka

# App imports
from app import AppActor
from pyCrow.crowlib import Action

# prepare logging, i.e. load config and get the root L
logging.config.fileConfig('./logging.conf')
L = logging.getLogger()
logging.getLogger('pykka').setLevel(logging.DEBUG)

if __name__ == '__main__':
    L.info('Starting...')

    ref: pykka.ActorRef = None
    try:
        ref = AppActor.start()
        assert ref is not None
        L.info(msg=f'Started Actor App ({ref.actor_urn})')

    except AssertionError:
        L.error(msg='Unable to start the app.')
    except pykka.ActorDeadError as ade:
        L.warning(msg=f'Message received for dead app: {ade}')

    state = 'running' if ref.is_alive() else 'terminated'
    L.info(f'Finished standalone program. Actor App ({ref.actor_urn}) is «{state}».')
