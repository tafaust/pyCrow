#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Audio Recording utilities.

Parts of this code are taken from:
- https://stackoverflow.com/a/6743593/2402281

Information to write this code are taken from:
- https://en.wikipedia.org/wiki/Voice_frequency
"""

import logging
import struct
import time
import wave
from array import array
from collections import deque
from struct import pack
from sys import byteorder
from threading import Thread
from typing import Union

import numpy as np
import pyaudio

from pyCrow.audiolib.process import normalize, trim, add_silence, butter_bandpass_filter

L = logging.getLogger(__name__)
L.info(f'Loaded module: {__name__}.')


class VoiceRecorder(object):
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
        super(VoiceRecorder, self).__init__()
        self.THRESHOLD = threshold
        self.CHUNK_SIZE = chunk_size
        self.FORMAT = format
        self.RATE = rate

        L.info('Instantiated VoiceRecorder with specs:\n' + '\n'.join(
            ['\t\t{}: {}'.format(k, v) for k, v in self.__dict__.items()]))

    def record(self, seconds: Union[int, float] = 0):
        """
        RecordAudio a word or words from the microphone and
        return the data as an array of signed shorts.

        Normalizes the audio, trims silence from the
        start and end, and pads with 0.5 seconds of
        blank sound to make sure VLC et al can play
        it without getting chopped off.
        (this shall be configurable -^)
        """
        # store data in this array
        r = array('h')

        # use a ring buffer to buffer at most 10000 chunks
        ring_buffer = deque(maxlen=int(1e4 * self.CHUNK_SIZE))

        def _persist_recordings_from_buffer():
            L.debug('Writing audio from ring buffer to byte array.')
            Thread(target=r.extend, args=[ring_buffer.copy()]).start()
            ring_buffer.clear()

        def _audio_stream_callback(stream_in: bytes, frame_count, time_info, status):
            L.debug(f'Audio stream callback status is {status}')
            if status:
                L.error('Non zero exit status in audio stream callback! Exiting...')
                exit()

            unpacked_in_data = list(struct.unpack('h' * frame_count, stream_in))

            # append data to the ring buffer
            if byteorder == 'big':
                ring_buffer.extendleft(unpacked_in_data)
            else:  # little
                ring_buffer.extend(unpacked_in_data)

            # when ring buffer is full, flush it to a byte array
            if len(ring_buffer) >= int(self.CHUNK_SIZE):
                _persist_recordings_from_buffer()

            return None, pyaudio.paContinue

        # let the recording begin…
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE, input=True, output=False,
                        frames_per_buffer=self.CHUNK_SIZE, stream_callback=_audio_stream_callback)
        sample_width = p.get_sample_size(self.FORMAT)

        input_specs = '\n'.join(
            ['\t\t{:30}: {}'.format(k, v) for k, v in p.get_default_input_device_info().items()])
        L.info(f'Input device is running with the following specs:\n{input_specs}')

        t = time.time()
        while stream.is_active() and (time.time() <= (t + seconds) or seconds == 0):
            time.sleep(1 / self.RATE)
            # yield sample_width, r

        # flush the rest of the buffer
        _persist_recordings_from_buffer()

        L.debug('Stopping audio stream.')
        stream.stop_stream()
        L.debug('Closing audio stream.')
        stream.close()
        p.terminate()

        # TODO make this configurable?
        # post-processing of the audio data
        r = normalize(r, absolute_maximum=16384)  # 16384 is the max for int16 (2**15 / 2)
        r = trim(r, threshold=self.THRESHOLD)
        r = add_silence(r, seconds=0.5, rate=self.RATE)

        # TODO this shall to be done online (i.e. in the loop above)
        # read data into numpy array and bandpass filter within the voice frequency (VF)
        data = np.fromstring(r.tobytes(), dtype=np.int16)
        data = butter_bandpass_filter(
            data, cutfreq=(85.0, 800.0), sampling_frequency=self.RATE / 5, order=6)

        return sample_width, data

    def record_to_file(self, path: str, seconds: Union[int, float] = 0):
        """ Records from the microphone and outputs the resulting data to 'path'
        """
        sample_width, npdata = self.record(seconds=seconds)
        data = pack('<' + ('h' * len(npdata.astype(array))), *npdata.astype(array))

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.RATE)
        wf.writeframes(data)
        wf.close()

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
        pass  # TODO
