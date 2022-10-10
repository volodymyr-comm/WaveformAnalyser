#!/usr/bin/env python3

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from typing import Union, Iterable
import pandas as pd
import numpy as np
import re
import os

from helpers.digital import *
from helpers.common import *


class DigitalAnalyser:

    def __init__(self):
        self._data_df: pd.DataFrame = pd.DataFrame()
        self._change_times_df: pd.DataFrame = pd.DataFrame()
        self.record_column_name = 'Record'

    def import_from_directory(self, path: str, name_regex: str, record_name_regex: str):
        self._data_df = files2dataframe(path, name_regex, record_name_regex)

    def import_from_dict(self, data: dict):
        collective_df = pd.concat(data.values(), axis=0, keys=data.keys())
        collective_df.index.names = ['Record', list(data.values())[0].index.name]
        collective_df.sort_index(inplace=True)
        self._data_df = collective_df

    def filter_columns(self, columns: Iterable[Union[str, int, re.Pattern]]):
        cols_before = self._data_df.columns
        cols_requested = list()
        for i in columns:
            if isinstance(i, re.Pattern):
                cols_requested.extend(filter(i.match, cols_before))
            elif i in cols_before:
                cols_requested.append(i)
            else:
                raise Exception(f'No column name "{i}: in data')
        self._data_df = self._data_df.filter(cols_requested, axis=1)

    def set_index(self, col_name, **kwargs):
        self._data_df.reset_index(inplace=True)
        self._data_df.drop('Row', inplace=True, axis=1)
        self._data_df.set_index([self.record_column_name, col_name], inplace=True, **kwargs)

    def set_time_index(self, col_name, unit, **kwargs):
        self._data_df.reset_index(inplace=True)
        self._data_df.drop('Row', inplace=True, axis=1)
        # self._data_dfindex].apply(pd.to_timedelta, unit='s')
        # self._data_df[col_name] = pd.to_timedelta(self._data_df[col_name], unit=unit)
        # self._data_df[col_name] = (self._data_df[col_name]).astype('datetime64[s]')
        self._data_df[col_name] = pd.to_datetime(self._data_df[col_name], unit=unit)
        self._data_df.set_index([self.record_column_name, col_name], inplace=True, **kwargs)

    def plot2pdf(self, path, plot_type):
        with PdfPages(path) as pdf:
            # todo eventual multipage support
            if plot_type == 'scatter':
                # self._data_df.unstack(level=0).plot(subplots=True, legend=False)
                self.plot_overlapping_charts()
                pdf.savefig()
                plt.close()

            else:
                raise Exception(f'Unsupported plot type "{plot_type}"')

    def get_dataframe(self):
        return self._data_df.copy()

    def plot_overlapping_charts(self):
        plot_overlapping_charts_concept(self._data_df)

    @property
    def change_times_df(self):
        # todo: expire if data in self._data_df were changed
        # todo: make it a thread-safe
        if self._change_times_df.empty:
            self._change_times_df = signal_df_to_change_times_df(self._data_df)
        return self._change_times_df

    def check_time_dispersion(self):
        change_times_df = self.change_times_df
        mean_change_time_df = change_times_df.mean(axis=1)
        std_change_time_df = change_times_df.std(axis=1)
        mean_to_current_df = change_times_df.subtract(mean_change_time_df, axis=0)
        # plot_overlapping_charts_concept(mean_change_time_df)
        # plot_overlapping_charts_concept(abs(mean_to_current_df))
        mean_series = change_times_df.unstack().mean()
        # change_times_df.unstack().transpose()
        # mean_diff_df = change_times_df.unstack().transpose().subtract(mean_series, axis=0).transpose().stack()
        # plot_overlapping_charts_concept(mean_diff_df)
        # plot_overlapping_charts_concept(std_change_time_df)

    def show_sts_std1(self):
        change_times_df = self.change_times_df  # todo: thread-safety or copy
        mean_change_time_series = change_times_df.mean(axis=1)
        std_change_time_series = change_times_df.std(axis=1)
        within_std_mask = change_times_df.loc[change_times_df.subtract(mean_change_time_series, axis=0).abs() <= std_change_time_series]
        plot_overlapping_charts_concept(change_times_df[within_std_mask])
        plot_overlapping_charts_concept(change_times_df[~within_std_mask])

    def show_std1_concept1(self):
        change_times_df = self.change_times_df  # todo: thread-safety or copy
        change_times_unstacked_df = change_times_df.unstack()
        mean_change_time_series = change_times_unstacked_df.mean()
        std_change_time_series = change_times_unstacked_df.std()
        change_times_dist_to_mean_df = change_times_unstacked_df.transpose().subtract(mean_change_time_series, axis=0).abs()
        # Align indexes according to FutureWarning suggestion
        change_times_dist_to_mean_df, std_change_time_series = change_times_dist_to_mean_df.align(std_change_time_series, axis=0, copy=False)
        within_std_mask = change_times_dist_to_mean_df.le(std_change_time_series, axis=0)\
            .transpose()\
            .stack()
        plot_overlapping_charts_concept(change_times_df)
        # plot_overlapping_charts_concept(change_times_df[within_std_mask], color='green')
        # plot_overlapping_charts_concept(change_times_df[~within_std_mask], color='red')
        # todo for check only:
        plot_overlapping_charts_concept(change_times_df[within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='green')
        plot_overlapping_charts_concept(change_times_df[~within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='red')

    def show_std2(self):
        change_times_df = self.change_times_df  # todo: thread-safety or copy
        change_times_unstacked_df = change_times_df.unstack()
        mean_change_time_series = change_times_unstacked_df.mean()
        std_change_time_series = change_times_unstacked_df.std()
        change_times_dist_to_mean_df = change_times_unstacked_df.transpose().subtract(mean_change_time_series, axis=0).abs()
        # Align indexes according to FutureWarning suggestion
        change_times_dist_to_mean_df, std_change_time_series = change_times_dist_to_mean_df.align(std_change_time_series, axis=0, copy=False)
        within_std_mask = change_times_dist_to_mean_df.le(std_change_time_series * 2, axis=0)\
            .transpose()\
            .stack()
        plot_overlapping_charts_concept(change_times_df)
        # plot_overlapping_charts_concept(change_times_df[within_std_mask], color='green')
        # plot_overlapping_charts_concept(change_times_df[~within_std_mask], color='red')
        # todo for check only:
        plot_overlapping_charts_concept(change_times_df[within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='green')
        plot_overlapping_charts_concept(change_times_df[~within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='red')

    def show_std2_concept2(self):
        change_times_df = self.change_times_df  # todo: thread-safety or copy
        mean_change_time_series = change_times_df.groupby(level=1).mean()
        std_change_time_series = change_times_df.groupby(level=1).std() * 2
        change_times_dist_to_mean_df = change_times_df.subtract(mean_change_time_series).abs()
        # Align indexes according to FutureWarning suggestion
        change_times_dist_to_mean_df, std_change_time_series = change_times_dist_to_mean_df.align(std_change_time_series, axis=0, copy=False)
        within_std_mask = change_times_dist_to_mean_df.le(std_change_time_series)
        plot_overlapping_charts_concept(change_times_df, color='black')
        mean_change_time_series.plot(color='blue')
        plot_overlapping_charts_concept(std_change_time_series, color='purple')
        plot_overlapping_charts_concept(change_times_df[within_std_mask], color='green')
        plot_overlapping_charts_concept(change_times_df[~within_std_mask], color='red')
        # todo for check only:
        # plot_overlapping_charts_concept(change_times_df[within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='green')
        # plot_overlapping_charts_concept(change_times_df[~within_std_mask].apply(lambda x: x + list(int(i) for i in x.index.get_level_values(0))), color='red')


if __name__ == '__main__':
    from data_examples_generator import generate_data_examples_dict
    da = DigitalAnalyser()
    # da.import_from_directory('data_examples', r'^process_[0-9]+.csv$', r'^process_([0-9]+)?.csv$')
    data_dict = generate_data_examples_dict(100)
    print('data generated')
    da.import_from_dict(data_dict)
    print('data imported')
    # da.filter_columns(['TIME', re.compile(r'^D\d+$')])
    # da.set_index('TIME')
    # da.set_time_index('TIME', unit='s')
    # da._resample_concept('0.01S')
    # print(da.get_dataframe())
    # da.plot_overlapping_charts()
    # da.check_time_dispersion()
    # da.check_time_dispersion()
    # da._plot_overlapping_charts_concept()
    # da.plot2pdf('scatter.pdf', 'scatter')
    # print(da.get_dataframe().unstack(level=0).columns)
    # print(da.get_dataframe().swaplevel())
    da.show_std2_concept2()
    plt.show()
