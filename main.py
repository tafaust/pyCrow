#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config

logging.config.fileConfig('./logging.conf')

L = logging.getLogger('root')


def main():
    """Main program"""
    from pyCrow.audiolib import VoiceRecorder
    vr: VoiceRecorder = VoiceRecorder()
    vr.record_to_file('./resources/demo.wav', seconds=10.)


if __name__ == '__main__':
    L.info('Running main program.')
    main()  # most magic happens here :-)
    L.info('Finished main program.')
