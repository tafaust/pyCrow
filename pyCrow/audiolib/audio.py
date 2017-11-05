#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Audio Recording utilities.

Parts of this code are taken from:
- https://stackoverflow.com/a/6743593/2402281

Information to write this code are taken from:
- https://en.wikipedia.org/wiki/Voice_frequency
"""


# Python-native imports
import logging
import struct
import time
import wave
from array import array
from collections import deque
from struct import pack
from sys import byteorder
from threading import Thread
from typing import Union, Tuple

# Third-party imports
import numpy as np
import pyaudio
import pykka

# App imports
from pyCrow.audiolib.process import normalize, trim, add_silence, butter_bandpass_filter
from pyCrow.crowlib import Action

L = logging.getLogger(__name__)
L.debug(f'Loaded module: {__name__}.')


class AudioActor(pykka.ThreadingActor):
    def __init__(self, config: dict, **kwargs):
        super().__init__()
        self._config = config
        self._recorder = Recorder(**kwargs)

    def on_start(self):
        L.info(msg=f'Started AudioActor ({self.actor_urn})')

    def on_stop(self):
        L.info('AudioActor is stopped.')

    def on_failure(self, exception_type, exception_value, traceback):
        L.error(f'AudioActor failed: {exception_type} {exception_value} {traceback}')

    def on_receive(self, msg: dict) -> None:
        L.info(msg=f'AudioActor received message: {msg}')
        # process msg and alter state accordingly
        _cmd = msg.get('cmd', '').lower()
        if _cmd == Action.AUDIO_RECORD.get('cmd'):
            self._recorder.record(seconds=self._config.get('duration'))
        elif _cmd == Action.AUDIO_RECORD_TO_FILE.get('cmd'):
            self._recorder.record_to_file(
                file=self._config.get('file'), seconds=self._config.get('duration'))
        else:
            # default: do nothing but log this event
            L.info(msg=f'Received message {msg} which cannot be processed.')


class Recorder(object):
    """
    1s ==> 44100 samples
    20ms ==> 44100/50 = 882 samples
    """
    # constants for the speech recognition task
    RATE: int = 44100
    THRESHOLD: int = 500
    CHUNK_SIZE: int = 1024
    FORMAT: int = pyaudio.paInt16

    def __init__(self, threshold: int = THRESHOLD, chunk_size: int = CHUNK_SIZE,
                 format: int = FORMAT, rate: int = RATE):
        super(Recorder, self).__init__()
        self.THRESHOLD = threshold
        self.CHUNK_SIZE = chunk_size
        self.FORMAT = format
        self.RATE = rate

        self._last_recoding = np.empty(0)

        L.info('Instantiated Recorder with specs:\n' + '\n'.join(
            ['\t\t{}: {}'.format(k, v) for k, v in self.__dict__.items()]))

    def record(self, seconds: Union[int, float] = 0) -> Tuple[int, np.ndarray]:
        """
        RecordAudio a word or words from the microphone and
        return the data as a ``numpy.ndarray`` of signed shorts.

        Normalizes the audio, trims silence from the
        start and end, and pads with 0.5 seconds of
        blank sound to make sure VLC et al can play
        it without getting chopped off.
        (this shall be configurable -^)
        """
        # store data in this array
        #r = array('h')
        global r  # FIXME AHHH... need to fix this asap!!! :D
        r = np.ndarray(shape=(0,), dtype=np.dtype('h'))

        # use a ring buffer to buffer at most 1024 chunks
        ring_buffer = deque(maxlen=int(self.CHUNK_SIZE))

        # local helper: flush the buffer data to the recordings array
        def _l__persist_recordings_from_buffer():
            def _h(v):
                global r
                r = np.append(r, v).astype(dtype='h')
            L.debug('Writing audio from ring buffer to byte array.')
            Thread(target=_h, args=[ring_buffer.copy()], daemon=False).start()
            ring_buffer.clear()

        # local helper: pyaudio stream callback
        def _l__audio_stream_callback(stream_in: bytes, frame_count, time_info, status):
            if status:
                L.error('Non zero exit status in audio stream callback! Aborting...')
                return None, pyaudio.paAbort

            unpacked_in_data = list(struct.unpack('h' * frame_count, stream_in))

            # append data to the ring buffer
            if byteorder == 'big':
                ring_buffer.extendleft(unpacked_in_data)
            else:  # little
                ring_buffer.extend(unpacked_in_data)

            # when ring buffer is full, flush it to a byte array
            if len(ring_buffer) >= int(self.CHUNK_SIZE):
                _l__persist_recordings_from_buffer()

            return None, pyaudio.paContinue

        # let the recording begin...
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE, input=True, output=False,
                        frames_per_buffer=self.CHUNK_SIZE, stream_callback=_l__audio_stream_callback)
        sample_width = p.get_sample_size(self.FORMAT)

        input_specs = '\n'.join(
            ['\t\t{:30}: {}'.format(k, v) for k, v in p.get_default_input_device_info().items()])
        L.info(f'Input device is running with the following specs:\n{input_specs}')

        t = time.time()
        while stream.is_active() and (time.time() < (t + seconds) or seconds == 0):
            L.debug(f'Start time: {t}\tEnd time: {t+seconds}\tDelta: {t+seconds-time.time()}')
            time.sleep(1. / self.RATE)
            # yield sample_width, r

        # flush the rest of the buffer
        _l__persist_recordings_from_buffer()

        L.debug('Stopping audio stream...')
        stream.stop_stream()
        L.debug('Closing audio stream...')
        stream.close()
        p.terminate()

        # FIXME the processing of the data done below shall be done only!!!

        # TODO make this configurable?
        # post-processing of the audio data
        #r = normalize(r, absolute_maximum=16384)  # 16384 is the max for int16 (2**15 / 2)
        #r = trim(r, threshold=self.THRESHOLD)
        #r = add_silence(r, seconds=0.5, rate=self.RATE)

        self._last_recoding = r
        return sample_width, r

    def record_to_file(self, file: str, seconds: Union[int, float] = 0) -> None:
        """ Records from the microphone and outputs the resulting data to '`file'`.
        """
        sample_width, npdata = self.record(seconds=seconds)

        L.info(f'Audio data is of length {len(npdata)/self.RATE} before filtering.')
        # todo parametrize filtering and the like
        # bandpass filter in the Voice Frequency (VF) range
        npdata = butter_bandpass_filter(
            npdata, cutfreq=(85.0, 800.0), sampling_frequency=self.RATE / 5, order=6)

        data = pack('<' + ('h' * len(npdata.astype(array))), *npdata.astype(dtype=array))

        with wave.open(file, 'wb') as wf:
            L.info(f'Writing audio data of length {len(npdata)/self.RATE}...')
            wf.setnchannels(1)
            wf.setsampwidth(sample_width)
            wf.setframerate(self.RATE)
            wf.writeframes(data)
            L.info(f'Successfully written audio data into file "{file}".')

        # TODO refactor into its own module
        '''
        import matplotlib.pyplot as plt
        fig = plt.figure()
        s = fig.add_subplot(111)
        # s.plot(npdata)
        s.specgram(npdata, NFFT=1024, Fs=self.RATE / 5, noverlap=900, cmap='binary')
        plt.show(block=True)
        '''

    def record_mfcc_batches(self):
        pass  # TODO ...?
