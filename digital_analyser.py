#!/usr/bin/env python3

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from typing import Union, Iterable
import pandas as pd
import re
import os


def files2dataframe(path: str, name_regex: str, record_name_regex: str):
    """
    Only csv files are supported now.
    Fast import without data filtering may consume a lot of RAM
    todo:
    * add filtering by columns
    * add oversampling reduction (eg by consecutive unique rows)
    """

    # filter files and extract record names
    file_name_pattern = re.compile(name_regex)
    file_names = list(filter(file_name_pattern.match, os.listdir(path)))
    record_name_pattern = re.compile(record_name_regex)
    record_names = [record_name_pattern.match(i)[1] for i in file_names]
    if len(record_names) != len(file_names):
        raise Exception('One or more file name do not contain record name specified in regex')
    # import files to multiindex dataframe
    cwd = os.getcwd()
    os.chdir(path)
    collective_df = pd.concat(map(pd.read_csv, file_names), axis=0, keys=record_names)
    os.chdir(cwd)
    collective_df.index.names = ['Record', 'Row']
    collective_df.sort_index(inplace=True)
    return collective_df


class DigitalAnalyser:
    def __int__(self):
        self._data_df: pd.DataFrame

    def import_from_directory(self, path: str, name_regex: str, record_name_regex: str):
        self._data_df = files2dataframe(path, name_regex, record_name_regex)

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

    def set_index(self, index, **kwargs):
        self._data_df.reset_index(inplace=True)
        self._data_df.drop('Row', inplace=True, axis=1)
        self._data_df.set_index(['Record', index], inplace=True, **kwargs)

    def plot2pdf(self, path, plot_type):
        with PdfPages(path) as pdf:
            # todo eventual multipage support
            if plot_type == 'scatter':
                # self._data_df.unstack(level=0).plot(subplots=True, legend=False)
                self._plot_scatter_concept()
                pdf.savefig()
                plt.close()

            else:
                raise Exception(f'Unsupported plot type "{plot_type}"')

    def get_dataframe(self):
        return self._data_df.copy()

    def _plot_scatter_concept(self):
        # todo: check unexpected "ramps" on time-indexed dataframes
        axs = list()
        self._data_df.groupby(level=0, axis=0).apply(
            lambda x: axs.append(x.droplevel(0).plot(subplots=True, legend=False, ax=axs[-1] if len(axs) else None)))


if __name__ == '__main__':
    da = DigitalAnalyser()
    da.import_from_directory('data_examples', r'^process_[0-9]+.csv$', r'^process_([0-9]+)?.csv$')
    da.filter_columns(['TIME', re.compile(r'^D[0-9]+$')])

    da.set_index('TIME')
    print(da.get_dataframe())
    da._plot_scatter_concept()
    da.plot2pdf('scatter.pdf', 'scatter')
    print(da.get_dataframe().unstack(level=0).columns)
    print(da.get_dataframe().swaplevel())
    plt.show()
