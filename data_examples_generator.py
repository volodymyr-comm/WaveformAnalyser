#!/usr/bin/env python3
import matplotlib.pyplot as plt
from typing import Dict
from ctypes import *
import pandas as pd
import numpy as np
import pandas
import os

from morse_translator import encrypt

if __name__ == '__main__':
    TIME_DISPERSION = -0.01, 0.01

    # create destination folder if not exists
    os.system('mkdir -p data_examples')

    # create digital sequence
    morse_message = encrypt('EXAMPLE WAVEFORM ' * 5)
    digital_sequence = morse_message.replace('.', '00').replace('-', '11').replace(' ', '')
    digital_sequence_array = np.fromstring(' '.join(digital_sequence), dtype=c_uint8, sep=' ')

    # create ideal time array
    time_array = np.arange(len(digital_sequence_array))
    # make trigger om 5th point
    time_array -= 5

    # create dummy registrations with randomized time dispersion
    cycles_dict: Dict[int, pd.DataFrame] = {}
    ax: plt.plot = None
    for meas_cycle in range(1, 101):
        _time_array = time_array.copy() + np.random.uniform(*TIME_DISPERSION, len(time_array))
        cycles_dict[meas_cycle] = pandas.DataFrame.from_dict({'TIME': _time_array, 'D0': digital_sequence_array})
        cycles_dict[meas_cycle].to_csv(f'data_examples/process_{meas_cycle:05d}.csv')

        # optionally show plots
        if ax is None:
            ax = cycles_dict[meas_cycle].set_index('TIME', drop=True).plot()
        else:
            cycles_dict[meas_cycle].set_index('TIME', drop=True).plot(ax=ax)
    plt.show()
