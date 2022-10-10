#!/usr/bin/env python3
import matplotlib.pyplot as plt
from typing import Dict
from ctypes import *
import pandas as pd
import numpy as np
import os

from morse_translator import encrypt


def round2multiple(number, multiple):
    return round(multiple * round(number / multiple), 5)  # pay attention to round to 5 places after decimal!


def generate_data_examples_dict(cycles: int) -> dict:
    CYCLES: int = cycles
    COMPRESSED_OUTPUT_DATA: bool = False
    TIME_DISPERSION = -0.01, 0.01
    SAMPLE_RATE = 0.01
    TRIGGER_ON = 5
    in_var_dict = {
        'D0': {
            'Time dispersion': (-0.01, 0.01),
        },
        'D1': {
            'Time dispersion': (-0.02, 0.01),
        },
        'D2': {
            'Time dispersion': (-0.02, 0.03),
        },
        'D3': {
            'Time dispersion': (-0.03, 0.03),
        },
        'D4': {
            'Time dispersion': (-0.01, 0.01),
        },
    }

    # create destination folder if not exists
    os.system('mkdir -p data_examples')

    # create digital sequence
    morse_message = encrypt('EXAMPLE WAVEFORM ' * 1)
    digital_sequence = morse_message.replace('.', '00').replace('-', '11').replace(' ', '')
    digital_sequence_array = np.fromstring(' '.join(digital_sequence), dtype=c_uint8, sep=' ')

    # create ideal time array
    time_array = np.arange(len(digital_sequence_array))
    # make trigger om 5th point
    time_array -= TRIGGER_ON

    # create dummy registrations with randomized time dispersion
    cycles_dict: Dict[int, pd.DataFrame] = {}
    for meas_cycle in range(1, CYCLES + 1):
        cycle_data_dfs_list = list()
        for ch, var in in_var_dict.items():
            _time_array = time_array.copy() + np.random.uniform(*var['Time dispersion'], len(time_array))
            cycle_data_dfs_list.append(
                pd.DataFrame.from_dict({'TIME': _time_array, ch: digital_sequence_array}).set_index('TIME')
            )
        cycles_dict[meas_cycle] = pd.concat(cycle_data_dfs_list)
        cycles_dict[meas_cycle] = cycles_dict[meas_cycle].reindex(
            np.append(
                cycles_dict[meas_cycle].index.values,
                np.arange(round2multiple(cycles_dict[meas_cycle].index.min() - 2 * SAMPLE_RATE, SAMPLE_RATE),
                          round2multiple(cycles_dict[meas_cycle].index.max() + SAMPLE_RATE, SAMPLE_RATE),
                          SAMPLE_RATE)
            )
        )\
            .sort_index()\
            .fillna(method='ffill')\
            .fillna(method='bfill')
        if COMPRESSED_OUTPUT_DATA:
            # todo
            pass
    return cycles_dict


def plot_examples_dict(cycles_dict: dict):
    ax: plt.plot = None
    for meas_cycle_data in cycles_dict.values():
        if ax is None:
            ax = meas_cycle_data.plot(legend=False)
        else:
            meas_cycle_data.plot(ax=ax, legend=False)
    plt.show()


def export_examples_dict(cycles_dict: dict):
    for meas_cycle, meas_cycle_data in cycles_dict.items():
        cycles_dict[meas_cycle].to_csv(f'data_examples/process_{meas_cycle:05d}.csv')


if __name__ == '__main__':
    cycles_dict = generate_data_examples_dict(100)
    plot_examples_dict(cycles_dict)
    # export_examples_dict(cycles_dict)


