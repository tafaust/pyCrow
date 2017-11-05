#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Method invocation abstraction layer.

This module provides an abstraction layer to design pipelines in this framework. Thus, method
invocations may be chained in here and are optimized before executed concurrently. The actual 
implementation is based on the `pulsar-queue` actor framework.
"""

# Python-native imports
import logging.config

# Third-party imports
import pykka

# App imports


L = logging.getLogger(__name__)
L.debug(f'Loaded module: {__name__}.')


class OfflinePipeline(pykka.ThreadingActor):
    # proxy
    class __OfflinePipeline(object):
        pykka_traversable = True

        def __init__(self, *args, **kwargs):
            for k, v in kwargs.items():
                self.__setattr__(name=k, value=v)

    instance = None

    def __new__(cls, *args, **kwargs):
        if not OfflinePipeline.instance:
            OfflinePipeline.instance = OfflinePipeline.__OfflinePipeline(*args, **kwargs)
        return OfflinePipeline.instance


class OnlinePipeline(object):
    def __init__(self):
        super(OnlinePipeline, self).__init__()
