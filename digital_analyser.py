#!/usr/bin/env python3

from matplotlib import pyplot as plt
import pandas as pd
import re
import os


class DigitalAnalyser:
    def __int__(self):
        pass

    # def import_from_path(self, path: str, name_regex: str, record_name_regex: str):

    def files2dataframe(self, path: str, name_regex: str, record_name_regex: str):
        """Only csv files are supported now"""
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


if __name__ == '__main__':
    da = DigitalAnalyser()
    collective_df = da.files2dataframe('data_examples', r'^process_[0-9]+.csv$', r'^process_([0-9]+)?.csv$')
    print(collective_df.unstack(level=0)['D0'])
    collective_df.unstack(level=0)['D0'].plot(legend=False)
    plt.show()
