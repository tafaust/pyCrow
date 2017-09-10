#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Parts of this code are taken from:
- https://stackoverflow.com/a/6743593/2402281

Information to write this code are taken from:
- https://en.wikipedia.org/wiki/Voice_frequency

"""

import logging
import time
import wave
from array import array
from struct import pack
from sys import byteorder

import numpy as np
import pyaudio

from pyCrow.audiolib.process import is_silent, normalize, trim, add_silence, butter_bandpass_filter


L = logging.getLogger(__name__)
L.info('Loaded module: {}.'.format(__name__))


class VoiceRecorder(object):
    # constants
    THRESHOLD = 500
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    RATE = 44100

    def __init__(self, threshold: int = THRESHOLD, chunk_size: int = CHUNK_SIZE,
                 format: int = FORMAT, rate: int = RATE):
        super(VoiceRecorder, self).__init__()
        self.THRESHOLD = threshold
        self.CHUNK_SIZE = chunk_size
        self.FORMAT = format
        self.RATE = rate

        L.info('Instantiated VoiceRecorder with specs:\n' + '\n'.join(
            ['\t\t{}: {}'.format(k, v) for k, v in self.__dict__.items()]))

    def record(self, seconds: int or float = 0):
        """
        RecordAudio a word or words from the microphone and 
        return the data as an array of signed shorts.
    
        Normalizes the audio, trims silence from the 
        start and end, and pads with 0.5 seconds of 
        blank sound to make sure VLC et al can play 
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE, input=True, output=True,
                        frames_per_buffer=self.CHUNK_SIZE)
        L.info('Input device is running with the following specs:\n' + '\n'.join(
            ['\t\t{:30}: {}'.format(k, v) for k, v in p.get_default_input_device_info().items()]))

        num_silent = 0
        snd_started = False

        r = array('h')

        t = time.time()
        while time.time() <= (t + seconds) or seconds == 0:
            # little endian, signed short
            snd_data = array('h', stream.read(self.CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = is_silent(snd_data, threshold=self.THRESHOLD)

            if silent and snd_started:
                num_silent += 1
                # print(num_silent)
            elif not silent and not snd_started:
                snd_started = seconds == 0

            if snd_started and num_silent > 50:
                break

        sample_width = p.get_sample_size(self.FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        r = normalize(r, absolute_maximum=16384)
        r = trim(r, threshold=self.THRESHOLD)
        r = add_silence(r, seconds=0.5, rate=self.RATE)

        # TODO this needs to be done online (i.e. in the above loop)
        # read data into numpy array and filter into voice frequency (VF) [parameters tuned
        # according to my voice]
        data = np.fromstring(r.tobytes(), dtype=np.int16)
        data = butter_bandpass_filter(data, cutfreq=(85.0, 800.0),
                                      sampling_frequency=self.RATE / 5, order=6)

        return sample_width, data

    def record_to_file(self, path: str, seconds: int or float = 0):
        "Records from the microphone and outputs the resulting data to 'path'"
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
        fig = plt.figure()
        s = fig.add_subplot(111)
        # s.plot(npdata)
        s.specgram(npdata, NFFT=1024, Fs=self.RATE / 5, noverlap=900, cmap='binary')
        plt.show(block=True)
        '''
