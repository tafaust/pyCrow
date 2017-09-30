#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Entry point.
"""


# Python-native imports
import logging.config

# Third-party imports
# noinspection PyPackageRequirements
from pq.api import PulsarQueue


# prepare logging, i.e. load config and get the root logger
logging.config.fileConfig('./logging.conf')
L = logging.getLogger()


# pulsar-queue config
task_paths = ['pyCrow.crowlib.*', 'pq.jobs']
data_store = 'redis://127.0.0.1:6379/7'
worker = 2


# build pulsar-queue app
def app() -> PulsarQueue:
    L.info('Starting PulsarQueue application.')
    return PulsarQueue(config=__file__)
