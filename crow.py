#!/usr/bin/python
# -*- coding: utf-8 -*-

""" « pyCrow » entry point.
"""

# Python-native imports
import asyncio
import logging.config
from typing import Union

# Third-party imports
from pq import api

# App imports
from app import app

# prepare logging, i.e. load config and get the root logger
logging.config.fileConfig('./logging.conf')
L = logging.getLogger()


async def aproc(proc) -> Union[asyncio.Future, asyncio.Future]:
    return await proc.start()


def main() -> None:
    proc = app().api()
    asyncio.get_event_loop().run_until_complete(aproc(proc))

    # start running tasks from here on...
    task = proc.tasks.execute(standalone)

    # do something else...


@api.job()
def standalone(self):
    from pyCrow.audiolib import VoiceRecorder
    vr: VoiceRecorder = VoiceRecorder()
    vr.record_to_file('./resources/demo.wav', seconds=10.)


# script part
if __name__ == '__main__':
    L.info('Running standalone program.')
    main()
    L.info('Finished standalone program.')
