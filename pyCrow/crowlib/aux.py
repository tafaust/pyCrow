#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Auxiliary functions.
"""

# Python-native imports
import asyncio
import time

# Third-party imports
# noinspection PyPackageRequirements
from pq import api


@api.job()
async def asynchronous(lag=1):
    """Causes the queue to wait for `lag` seconds.

    :param lag: The amount of seconds the global queue is delayed.
    :return:The delta, i.e. the actual amount of delay that took place. 
    """
    start = time.time()
    await asyncio.sleep(lag)
    return time.time() - start
