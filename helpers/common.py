import pandas as pd
import numpy as np
import os
import re


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


def plot_overlapping_charts_concept(data: pd.DataFrame, color='random'):
    axs = list()
    data.groupby(level=0, axis=0).apply(
        lambda x: axs.append(x.droplevel(0).plot(subplots=True,
                                                 legend=False,
                                                 style='.-',
                                                 color=np.random.rand(3) if color == 'random' else color,
                                                 ax=axs[-1] if len(axs) else None),
                             )
    )
