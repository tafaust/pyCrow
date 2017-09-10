#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from array import array

import numpy as np
from scipy.signal import butter, lfilter
from typing import Union, List, Tuple

L = logging.getLogger(__name__)
L.info('Loaded lib: {}.'.format(__name__))


def butter_bandpass(cutfreq: Union[List[float], Tuple[float, float]], sampling_frequency: float,
                    order: int = 5):
    # noinspection PyTupleAssignmentBalance
    b, a = butter(order, [(f * 2.) / sampling_frequency for f in cutfreq], btype='band')
    return b, a


def butter_bandpass_filter(data: np.ndarray, cutfreq: Union[List[float], Tuple[float, float]],
                           sampling_frequency: float, order: int = 5):
    b, a = butter_bandpass(cutfreq=cutfreq, sampling_frequency=sampling_frequency, order=order)
    return lfilter(b, a, data).astype(dtype=data.dtype)  # returns filtered data y


def is_silent(snd_data: array, threshold: int or float):
    """Returns 'True' if below the 'silent' threshold
    """
    return max(snd_data) < threshold


def normalize(snd_data: array, absolute_maximum: int or float):
    """Average the volume out
    """
    L.info('Normalizing data with {} many samples with an absolute maximum of {}'.format(
        len(snd_data), absolute_maximum))
    empirical_maximum: float = max(abs(i) for i in snd_data)
    times = float(absolute_maximum) / empirical_maximum

    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r


def trim(snd_data: array, threshold: int or float):
    """Trim the blank spots at the start and end
    """

    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i) > threshold:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data


def add_silence(snd_data: array, seconds: int or float, rate: int or float):
    """Add silence to the start and end of 'snd_data' of length 'seconds'
    """
    L.info('Adding {} seconds of silence to the data totalling in {} extra samples.'.format(
        seconds, int(seconds * rate) * 2
    ))
    r = array('h', [0 for i in range(int(seconds * rate))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds * rate))])
    return r
