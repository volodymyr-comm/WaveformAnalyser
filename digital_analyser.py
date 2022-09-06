#!/usr/bin/env python3

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
    return collective_df


class DigitalAnalyser:
    def __int__(self):
        self._data_df: pd.DataFrame
        print(self._data_df)

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
            print(self._data_df[cols_requested])
        self._data_df = self._data_df[cols_requested]

    def get_dataframe(self):
        return self._data_df.copy()


if __name__ == '__main__':
    da = DigitalAnalyser()
    collective_df = da.import_from_directory('data_examples', r'^process_[0-9]+.csv$', r'^process_([0-9]+)?.csv$')
    da.filter_columns([re.compile(r'^D[0-9]+$')])
    print(da.get_dataframe().unstack(level=0))
    print(da.get_dataframe().unstack(level=0)['D1'])
    da.get_dataframe().unstack(level=0)['D1'].plot(legend=False)
    plt.show()
